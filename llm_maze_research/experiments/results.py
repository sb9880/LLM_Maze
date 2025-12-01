"""Results storage and aggregation for experiments."""

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import json

import pandas as pd


@dataclass
class ExperimentResult:
    """Result from a single experiment."""

    experiment_id: str
    timestamp: str
    config: Dict[str, Any]
    metrics: Dict[str, Any]
    episodes: List[Dict[str, Any]]


class ResultsAggregator:
    """Aggregate and save experiment results."""

    def __init__(self, results_dir: Optional[Path] = None):
        """
        Initialize results aggregator.

        Args:
            results_dir: Directory to save results
        """
        self.results_dir = Path(results_dir or "results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.results: List[ExperimentResult] = []

    def save_result(
        self,
        experiment_id: str,
        config: Dict[str, Any],
        metrics: Dict[str, Any],
        episodes: List[Dict[str, Any]],
    ) -> Path:
        """
        Save experiment result.

        Args:
            experiment_id: Unique experiment ID
            config: Experiment configuration
            metrics: Aggregated metrics
            episodes: Individual episode data

        Returns:
            Path to saved result file
        """
        result = ExperimentResult(
            experiment_id=experiment_id,
            timestamp=datetime.now().isoformat(),
            config=config,
            metrics=metrics,
            episodes=episodes,
        )

        self.results.append(result)

        # Save to JSON
        result_dict = asdict(result)
        result_file = self.results_dir / f"{experiment_id}.json"

        with open(result_file, "w") as f:
            json.dump(result_dict, f, indent=2, default=str)

        return result_file

    def save_csv_summary(
        self,
        experiment_ids: List[str],
        output_file: Optional[Path] = None,
    ) -> Path:
        """
        Save aggregated results as CSV.

        Args:
            experiment_ids: List of experiment IDs to include
            output_file: Output CSV file path

        Returns:
            Path to saved CSV file
        """
        output_file = output_file or self.results_dir / "results_summary.csv"

        # Collect metrics from all results
        rows = []
        for result in self.results:
            if result.experiment_id in experiment_ids:
                row = {
                    "experiment_id": result.experiment_id,
                    "timestamp": result.timestamp,
                    **result.config,
                    **result.metrics,
                }
                rows.append(row)

        df = pd.DataFrame(rows)
        df.to_csv(output_file, index=False)

        return output_file

    def compare_experiments(
        self,
        experiment_ids: List[str],
        metrics_keys: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Compare multiple experiments.

        Args:
            experiment_ids: List of experiment IDs to compare
            metrics_keys: Specific metrics to include (None = all)

        Returns:
            DataFrame with comparison
        """
        comparison_data = []

        for result in self.results:
            if result.experiment_id in experiment_ids:
                row = {"experiment_id": result.experiment_id}

                # Add config
                row.update(result.config)

                # Add metrics
                if metrics_keys:
                    for key in metrics_keys:
                        row[key] = result.metrics.get(key)
                else:
                    row.update(result.metrics)

                comparison_data.append(row)

        return pd.DataFrame(comparison_data)

    def load_result(self, experiment_id: str) -> Optional[ExperimentResult]:
        """Load saved result from file."""
        result_file = self.results_dir / f"{experiment_id}.json"

        if not result_file.exists():
            return None

        with open(result_file) as f:
            data = json.load(f)

        return ExperimentResult(**data)

    def get_results_by_config(
        self,
        config_filter: Dict[str, Any],
    ) -> List[ExperimentResult]:
        """
        Get results matching config filter.

        Args:
            config_filter: Config keys/values to filter by

        Returns:
            Matching results
        """
        matching = []

        for result in self.results:
            match = True
            for key, value in config_filter.items():
                if result.config.get(key) != value:
                    match = False
                    break
            if match:
                matching.append(result)

        return matching

    def generate_report(self, output_file: Optional[Path] = None) -> Path:
        """
        Generate HTML report with visualizations.

        Args:
            output_file: Output HTML file path

        Returns:
            Path to saved report
        """
        output_file = output_file or self.results_dir / "report.html"

        html_content = self._generate_html_report()

        with open(output_file, "w") as f:
            f.write(html_content)

        return output_file

    def _generate_html_report(self) -> str:
        """Generate HTML report content."""
        html = """
        <html>
        <head>
            <title>LLM Maze Navigation Experiment Results</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #333; }
                table { border-collapse: collapse; width: 100%; margin-top: 20px; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #4CAF50; color: white; }
                tr:nth-child(even) { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <h1>LLM Tool Overreliance Study Results</h1>
            <h2>Experiment Summary</h2>
            <p>Total Experiments: {}</p>
        """.format(
            len(self.results)
        )

        # Add results table
        html += "<h2>Results Table</h2>"
        html += "<table>"
        html += "<tr><th>Experiment ID</th><th>Timestamp</th><th>Success Rate</th><th>Avg Steps</th></tr>"

        for result in self.results:
            html += "<tr>"
            html += f"<td>{result.experiment_id}</td>"
            html += f"<td>{result.timestamp}</td>"
            html += f"<td>{result.metrics.get('success_rate', 'N/A'):.2%}</td>"
            html += f"<td>{result.metrics.get('avg_steps', 'N/A'):.1f}</td>"
            html += "</tr>"

        html += "</table>"
        html += "</body></html>"

        return html
