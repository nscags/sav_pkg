from collections import defaultdict
import csv
from math import sqrt
from pathlib import Path
import pickle
from statistics import mean
from statistics import stdev
from typing import Any, Optional, Union

from bgpy.simulation_framework import MetricTracker
from bgpy.enums import Plane

from .data_key import DataKey
from .metric import Metric
from .metric_key import MetricKey

from sav_pkg.simulation_framework.utils import get_metric_key


class MetricTracker(MetricTracker):
    """Tracks metrics used in graphs across trials"""

    def __init__(
        self,
        data: Optional[defaultdict[DataKey, list[Metric]]] = None,
        metric_keys: Optional[list[MetricKey]] = list(get_metric_key()),
    ):
        """Inits data"""
        self.data = data if data is not None else defaultdict(list)
        self.metric_keys = metric_keys if metric_keys is not None else []

    #############
    # Add Funcs #
    #############

    ######################
    # Data Writing Funcs #
    ######################

    def write_data(
        self,
        csv_path: Path,
        pickle_path: Path,
    ) -> None:
        """Writes data to CSV and pickles it"""

        with csv_path.open("w") as f:
            rows = self.get_csv_rows()
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        with pickle_path.open("wb") as f:
            pickle.dump(self.get_pickle_data(), f)


    def get_csv_rows(self) -> list[dict[str, Any]]:
        """Generates rows for CSV output."""
        rows = []
        for data_key, metrics in self.data.items():
            # Aggregate percents for each MetricKey
            for metric in metrics:
                percents = metric.percents.get(metric.metric_key, [])
                mean_percent = mean(percents) if percents else 0.0
                yerr = self._get_yerr(percents)
                row = {
                    'scenario_config': data_key.scenario_config,
                    'percent_adopt': data_key.percent_adopt,
                    'propagation_round': data_key.propagation_round,
                    'as_group': metric.metric_key.as_group,
                    'outcome': metric.metric_key.outcome,
                    'value': mean_percent,
                    'yerr': yerr,
                }
                rows.append(row)
        return rows


    def get_pickle_data(self):
        """Prepares data for pickling."""
        pickle_data = []
        for data_key, metrics in self.data.items():
            for metric in metrics:
                percents = metric.percents.get(metric.metric_key, [])
                mean_percent = mean(percents) if percents else 0.0
                yerr = self._get_yerr(percents)
                data = {
                    'data_key': data_key,
                    'metric_key': metric.metric_key,
                    'value': mean_percent,
                    'yerr': yerr,
                }
                pickle_data.append(data)
        return pickle_data


    def _get_yerr(self, trial_data: list[float]) -> float:
        """Calculates the 90% confidence interval."""
        if len(trial_data) > 1:
            yerr_num = 1.645 * stdev(trial_data)
            yerr_denom = sqrt(len(trial_data))
            return float(yerr_num / yerr_denom)
        else:
            return 0.0

    ######################
    # Track Metric Funcs #
    ######################

    def track_trial_metrics(
        self,
        *,
        engine,  # Keeping as generic to match original code
        percent_adopt: Union[float, Any],  # Any to match SpecialPercentAdoptions
        trial: int,
        scenario,  # Assuming scenario has necessary attributes
        propagation_round: int,
        outcomes: dict[int, dict[int, dict[int, int]]],
    ) -> None:
        """Tracks all metrics from a single trial, adding to self.data"""
        self._track_trial_metrics(
            engine=engine,
            percent_adopt=percent_adopt,
            trial=trial,
            scenario=scenario,
            propagation_round=propagation_round,
            outcomes=outcomes,
        )


    def _track_trial_metrics(
        self,
        *,
        engine,
        percent_adopt: Union[float, Any],
        trial: int,
        scenario,
        propagation_round: int,
        outcomes: dict[int, dict[int, dict[int, int]]],
    ) -> None:
        """Tracks all metrics from a single trial, adding to self.data"""
        # Create metrics for each metric_key
        metrics = [Metric(metric_key) for metric_key in self.metric_keys]

        # Get reflector ASNs from scenario
        reflector_asns = scenario.reflector_asns
        attacker_asns = scenario.attacker_asns
        # print(f"Number of reflector ASNs: {len(reflector_asns)}")

        # Data plane outcomes
        data_plane_outcomes = outcomes[Plane.DATA.value]

        # Process each AS
        for as_obj in engine.as_graph:
            asn = as_obj.asn
            # if asn in reflector_asns:
            #     print(f"Processing reflector ASN: {asn}")
            for metric in metrics:
                metric.add_data(
                    asn=asn,
                    data_plane_outcomes=data_plane_outcomes,
                    reflector_asns=reflector_asns,
                    attacker_asns=attacker_asns,
                )

        # After processing, save percents
        for metric in metrics:
            metric.save_percents()
            # Create DataKey
            data_key = DataKey(
                propagation_round=propagation_round,
                percent_adopt=percent_adopt,
                scenario_config=scenario.scenario_config,
                metric_key=metric.metric_key,
            )
            # Append metric to data
            self.data[data_key].append(metric)

        # Debug statement to check if data is being added
        # print(f"Data added for trial {trial}: {len(self.data)} entries in self.data")