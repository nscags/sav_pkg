from .sav_scenario import SAVScenario


class SAVScenarioExport2Some(SAVScenario):
    
    def _get_possible_victim_asns(
        self, 
        engine, 
        percent_adoption, 
        prev_scenario
    ) -> frozenset[int]:
        # victims are only selected from mh e2s ASes
        possible_asns = frozenset(self.scenario_config.hardcoded_asn_cls_dict.keys())
        err = "Make mypy happy"
        assert all(isinstance(x, int) for x in possible_asns), err
        assert isinstance(possible_asns, frozenset), err
        return possible_asns