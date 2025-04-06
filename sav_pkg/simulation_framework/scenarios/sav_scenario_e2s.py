from .sav_scenario import SAVScenario


class SAVScenarioExport2Some(SAVScenario):
    
    def _get_possible_victim_asns(
        self, 
        engine, 
        percent_adoption, 
        prev_scenario
    ) -> frozenset[int]:
        # victims are only selected from mh e2s ASes
        group_asns = engine.as_graph.asn_groups[self.scenario_config.victim_subcategory_attr]
        hardcoded_asns = self.scenario_config.hardcoded_asn_cls_dict.keys()
        possible_asns = frozenset(set(hardcoded_asns) & set(group_asns))
        if not possible_asns:
            super()._get_possible_victim_asns(self, engine, percent_adoption, prev_scenario)
        err = "Make mypy happy"
        assert all(isinstance(x, int) for x in possible_asns), err
        assert isinstance(possible_asns, frozenset), err
        return possible_asns