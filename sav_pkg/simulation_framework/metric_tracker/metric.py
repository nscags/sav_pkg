from collections import defaultdict
from dataclasses import replace
from typing import Optional, Type

from .metric_key import MetricKey


class Metric:
    """Tracks a single metric"""

    def __init__(
        self,
        metric_key: MetricKey,
        percents: Optional[defaultdict[MetricKey, list[float]]] = None,
    ):
        self.metric_key = metric_key
        self._numerator = 0
        self._denominator = 0
        self.percents = percents if percents is not None else defaultdict(list)

    # def __add__(self, other):
    #     """Adds metric classes together"""

    #     if isinstance(other, Metric):
    #         agg_percents = defaultdict(list)
    #         for obj in (self, other):
    #             for metric_key, percent_list in obj.percents.items():
    #                 agg_percents[metric_key].extend(percent_list)
    #         return Metric(
    #             metric_key=self.metric_key,
    #             as_classes_used=self.as_classes_used,
    #             percents=agg_percents,
    #         )
    #     else:
    #         return NotImplemented

    def add_data(
        self,
        asn: int,
        data_plane_outcomes: dict[int, dict[int, dict[int, int]]],
        reflector_asns: set[int],
        attacker_asns: set[int],
    ):
        """Processes data for a single reflector ASN."""
        if asn in reflector_asns:
            self._denominator += 1  # Increment denominator for each reflector ASN
            matches = self._extract_outcome(asn, data_plane_outcomes, attacker_asns)
            if matches:
                self._numerator += 1


    def _extract_outcome(
        self,
        asn: int,
        data_plane_outcomes: dict[int, dict[int, dict[int, int]]],
        attacker_asns: set[int],
    ) -> bool:
        """
        Checks if the reflector ASN has the desired outcome from any attacker ASN.

        Returns:
            bool: True if the desired outcome is observed from any attacker ASN, False otherwise.
        """
        # Access the data plane outcomes for the ASN
        asn_outcomes = data_plane_outcomes.get(asn, {})
        # Iterate over all origins (attacker ASNs)
        for origin_asn, origin_outcomes in asn_outcomes.items():
            # Check if the origin ASN is an attacker ASN
            if origin_asn in attacker_asns:
                # Iterate over the outcomes for this origin
                for prev_hop_outcome in origin_outcomes.values():
                    # If the outcome matches the desired outcome, return True
                    if prev_hop_outcome == self.metric_key.outcome:
                        return True
        # No matching outcome found
        return False
    

    def save_percents(self):
        """Calculates and saves the percentage for this metric."""
        if self._denominator > 0:
            percent = (self._numerator / self._denominator) * 100
            self.percents[self.metric_key].append(percent)
        else:
            self.percents[self.metric_key].append(0.0)