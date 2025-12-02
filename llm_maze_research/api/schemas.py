"""Request/response schemas for FastAPI."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ExperimentConfigRequest(BaseModel):
    """Request to start an experiment."""

    # Environment config
    maze_size: int = Field(16, ge=4, le=64)
    maze_difficulty: str = Field("medium", pattern="^(easy|medium|hard)$")
    num_episodes: int = Field(10, ge=1, le=100)

    # Agent config
    model: str = Field("gpt-3.5-turbo")  # Options: gpt-3.5-turbo, gpt-4, o1-mini, openrouter, ollama
    agent_strategy: str = Field("adaptive", pattern="^(adaptive|tool_trusting|tool_avoiding|llm_solver)$")
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    use_openai: bool = Field(False)

    # Tool config
    use_tool: bool = Field(True)
    noise_type: str = Field("random", pattern="^(none|random|biased|delayed)$")
    noise_level: float = Field(0.3, ge=0.0, le=1.0)
    tool_query_frequency: float = Field(0.5, ge=0.0, le=1.0)

    # Execution config
    seed: int = Field(42, ge=0)
    max_steps_per_episode: int = Field(500, ge=10)

    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "maze_size": 16,
                "maze_difficulty": "medium",
                "num_episodes": 10,
                "model": "gpt-4-turbo",
                "agent_strategy": "adaptive",
                "temperature": 0.7,
                "use_tool": True,
                "noise_type": "random",
                "noise_level": 0.3,
                "tool_query_frequency": 0.5,
                "seed": 42,
                "max_steps_per_episode": 500,
            }
        }


class ExperimentResponse(BaseModel):
    """Response containing experiment info."""

    experiment_id: str
    status: str = Field(..., pattern="^(pending|running|completed|failed)$")
    progress: Optional[float] = Field(None, ge=0.0, le=1.0)
    config: Dict[str, Any]
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class ExperimentResultsResponse(BaseModel):
    """Response with experiment results."""

    experiment_id: str
    status: str
    config: Dict[str, Any]
    metrics: Dict[str, Any]
    episodes: Optional[List[Dict[str, Any]]] = None


class MetricsResponse(BaseModel):
    """Response with aggregated metrics."""

    total_episodes: int
    success_rate: float
    avg_steps: float
    median_steps: float
    avg_path_optimality: float
    avg_tool_usage_rate: float
    avg_tool_accuracy: float
    avg_tool_following_rate: float
    duration_seconds: float


class ComparisonRequest(BaseModel):
    """Request to compare multiple experiments."""

    experiment_ids: List[str] = Field(..., min_items=2)
    metrics: Optional[List[str]] = None


class ComparisonResponse(BaseModel):
    """Response with experiment comparison."""

    experiments: List[Dict[str, Any]]
    common_metrics: Dict[str, Any]


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field("healthy")
    version: str
    uptime_seconds: float
