"""FastAPI application for maze navigation experiments."""

import asyncio
from datetime import datetime
from typing import Dict, Optional, Any
import uuid
import numpy as np

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import structlog

from api.schemas import (
    ExperimentConfigRequest,
    ExperimentResponse,
    ExperimentResultsResponse,
    HealthResponse,
    ComparisonRequest,
    ComparisonResponse,
)
from experiments.runner import ExperimentConfig, ExperimentRunner
from experiments.results import ResultsAggregator
from api.dashboard import router as dashboard_router

logger = structlog.get_logger(__name__)


def convert_numpy_types(obj: Any) -> Any:
    """Convert numpy types to native Python types for JSON serialization."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    elif isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_numpy_types(item) for item in obj]
    return obj

# Application state
app = FastAPI(
    title="LLM Maze Navigation API",
    description="API for studying LLM overreliance on external tools",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory experiment tracking
experiments: Dict[str, dict] = {}
results_aggregator = ResultsAggregator()

# Startup time for health checks
startup_time = datetime.now()


@app.on_event("startup")
async def startup_event():
    """Initialize application."""
    logger.info("api_startup")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("api_shutdown")


# Include dashboard routes
app.include_router(dashboard_router)


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    uptime = (datetime.now() - startup_time).total_seconds()
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        uptime_seconds=uptime,
    )


@app.post("/api/v1/experiments/start", response_model=ExperimentResponse)
async def start_experiment(
    config: ExperimentConfigRequest,
    background_tasks: BackgroundTasks,
) -> ExperimentResponse:
    """
    Start a new experiment.

    Args:
        config: Experiment configuration
        background_tasks: FastAPI background tasks

    Returns:
        Experiment info with status
    """
    experiment_id = f"exp_{uuid.uuid4().hex[:12]}"

    # Create experiment entry
    experiments[experiment_id] = {
        "id": experiment_id,
        "status": "pending",
        "config": config.dict(),
        "created_at": datetime.now().isoformat(),
        "started_at": None,
        "completed_at": None,
        "progress": 0.0,
        "results": None,
    }

    # Schedule experiment execution
    background_tasks.add_task(_run_experiment_background, experiment_id, config)

    logger.info("experiment_started", experiment_id=experiment_id)

    return ExperimentResponse(
        experiment_id=experiment_id,
        status="pending",
        progress=0.0,
        config=config.dict(),
        created_at=experiments[experiment_id]["created_at"],
    )


async def _run_experiment_background(
    experiment_id: str,
    config: ExperimentConfigRequest,
) -> None:
    """Run experiment in background."""
    try:
        experiments[experiment_id]["status"] = "running"
        experiments[experiment_id]["started_at"] = datetime.now().isoformat()

        # Create experiment runner
        exp_config = ExperimentConfig(**config.dict())
        runner = ExperimentRunner(exp_config)

        # Run experiment
        results = await asyncio.to_thread(runner.run)

        # Store results
        experiments[experiment_id]["results"] = results
        experiments[experiment_id]["status"] = "completed"
        experiments[experiment_id]["completed_at"] = datetime.now().isoformat()
        experiments[experiment_id]["progress"] = 1.0

        # Save results
        results_aggregator.save_result(
            experiment_id,
            results["config"],
            results["metrics"],
            results["episodes"],
        )

        logger.info("experiment_completed", experiment_id=experiment_id)

    except Exception as e:
        experiments[experiment_id]["status"] = "failed"
        error_msg = f"{type(e).__name__}: {str(e)}"
        experiments[experiment_id]["error"] = error_msg
        logger.error("experiment_failed", experiment_id=experiment_id, error=error_msg)
        import traceback
        traceback.print_exc()


@app.get("/api/v1/experiments/{experiment_id}", response_model=ExperimentResponse)
async def get_experiment(experiment_id: str) -> ExperimentResponse:
    """
    Get experiment status and info.

    Args:
        experiment_id: Experiment identifier

    Returns:
        Experiment status and metadata
    """
    if experiment_id not in experiments:
        raise HTTPException(status_code=404, detail="Experiment not found")

    exp = experiments[experiment_id]
    return ExperimentResponse(
        experiment_id=experiment_id,
        status=exp["status"],
        progress=exp.get("progress", 0.0),
        config=exp["config"],
        created_at=exp["created_at"],
        started_at=exp.get("started_at"),
        completed_at=exp.get("completed_at"),
    )


@app.get(
    "/api/v1/experiments/{experiment_id}/results",
    response_model=ExperimentResultsResponse,
)
async def get_results(experiment_id: str) -> ExperimentResultsResponse:
    """
    Get experiment results.

    Args:
        experiment_id: Experiment identifier

    Returns:
        Full results with episodes
    """
    if experiment_id not in experiments:
        raise HTTPException(status_code=404, detail="Experiment not found")

    exp = experiments[experiment_id]
    if exp["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Experiment not completed (status: {exp['status']})",
        )

    results = exp["results"]
    return ExperimentResultsResponse(
        experiment_id=experiment_id,
        status=exp["status"],
        config=convert_numpy_types(results["config"]),
        metrics=convert_numpy_types(results["metrics"]),
        episodes=convert_numpy_types(results["episodes"]),
    )


@app.post("/api/v1/experiments/{experiment_id}/cancel")
async def cancel_experiment(experiment_id: str) -> dict:
    """
    Cancel a running experiment.

    Args:
        experiment_id: Experiment identifier

    Returns:
        Confirmation message
    """
    if experiment_id not in experiments:
        raise HTTPException(status_code=404, detail="Experiment not found")

    exp = experiments[experiment_id]
    if exp["status"] not in ["pending", "running"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel experiment with status: {exp['status']}",
        )

    exp["status"] = "cancelled"
    logger.info("experiment_cancelled", experiment_id=experiment_id)

    return {"message": "Experiment cancelled", "experiment_id": experiment_id}


@app.get("/api/v1/experiments")
async def list_experiments(
    status: Optional[str] = None,
    limit: int = 100,
) -> dict:
    """
    List all experiments.

    Args:
        status: Filter by status (optional)
        limit: Maximum number to return

    Returns:
        List of experiments
    """
    results = []
    count = 0

    for exp_id, exp in experiments.items():
        if status and exp["status"] != status:
            continue
        if count >= limit:
            break

        results.append({
            "experiment_id": exp_id,
            "status": exp["status"],
            "created_at": exp["created_at"],
            "config": exp["config"],
        })
        count += 1

    return {
        "experiments": results,
        "total_count": len(experiments),
        "returned_count": len(results),
    }


@app.post("/api/v1/results/compare", response_model=ComparisonResponse)
async def compare_experiments(request: ComparisonRequest) -> ComparisonResponse:
    """
    Compare multiple experiments.

    Args:
        request: Comparison request with experiment IDs

    Returns:
        Comparison results
    """
    # Verify all experiments exist and are completed
    for exp_id in request.experiment_ids:
        if exp_id not in experiments:
            raise HTTPException(
                status_code=404,
                detail=f"Experiment {exp_id} not found",
            )
        if experiments[exp_id]["status"] != "completed":
            raise HTTPException(
                status_code=400,
                detail=f"Experiment {exp_id} not completed",
            )

    # Get comparison dataframe
    comparison_df = results_aggregator.compare_experiments(
        request.experiment_ids,
        request.metrics,
    )

    return ComparisonResponse(
        experiments=comparison_df.to_dict(orient="records"),
        common_metrics={},  # Could compute common metrics here
    )


@app.get("/api/v1/results/aggregate")
async def get_aggregate_results(experiment_ids: Optional[list] = None) -> dict:
    """
    Get aggregated results across experiments.

    Args:
        experiment_ids: List of experiment IDs (None = all)

    Returns:
        Aggregated metrics
    """
    if experiment_ids is None:
        experiment_ids = [
            exp_id
            for exp_id, exp in experiments.items()
            if exp["status"] == "completed"
        ]

    if not experiment_ids:
        raise HTTPException(
            status_code=400,
            detail="No completed experiments found",
        )

    # Get all results
    all_metrics = {}
    for exp_id in experiment_ids:
        if exp_id in experiments and experiments[exp_id]["status"] == "completed":
            results = experiments[exp_id]["results"]
            all_metrics[exp_id] = results["metrics"]

    return {
        "experiment_count": len(all_metrics),
        "experiments": all_metrics,
    }


@app.post("/api/v1/batch/start")
async def start_batch_experiments(
    configs: list,
    background_tasks: BackgroundTasks,
) -> dict:
    """
    Start multiple experiments in batch.

    Args:
        configs: List of experiment configurations
        background_tasks: Background task queue

    Returns:
        List of experiment IDs
    """
    experiment_ids = []

    for config_dict in configs:
        config = ExperimentConfigRequest(**config_dict)
        exp_id = f"exp_{uuid.uuid4().hex[:12]}"

        experiments[exp_id] = {
            "id": exp_id,
            "status": "pending",
            "config": config.dict(),
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "progress": 0.0,
            "results": None,
        }

        background_tasks.add_task(_run_experiment_background, exp_id, config)
        experiment_ids.append(exp_id)

    logger.info("batch_experiments_started", count=len(experiment_ids))

    return {
        "experiment_ids": experiment_ids,
        "count": len(experiment_ids),
    }


@app.get("/api/v1/status")
async def api_status() -> dict:
    """Get API status and statistics."""
    total_experiments = len(experiments)
    completed = sum(1 for exp in experiments.values() if exp["status"] == "completed")
    running = sum(1 for exp in experiments.values() if exp["status"] == "running")
    pending = sum(1 for exp in experiments.values() if exp["status"] == "pending")

    return {
        "status": "operational",
        "total_experiments": total_experiments,
        "completed_experiments": completed,
        "running_experiments": running,
        "pending_experiments": pending,
        "uptime_seconds": (datetime.now() - startup_time).total_seconds(),
    }
