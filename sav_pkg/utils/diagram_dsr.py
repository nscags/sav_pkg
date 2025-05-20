import ipaddress
from typing import TYPE_CHECKING

from bgpy.simulation_engine import BGP, BaseSimulationEngine, BGPFull

from sav_pkg.enums import Outcomes
from sav_pkg.simulation_framework import SAVScenarioDSR
from .diagram import SAVDiagram

if TYPE_CHECKING:
    from bgpy.as_graphs.base.as_graph import AS


class SAVDiagramDSR(SAVDiagram):

    def _get_outcome_html(self, traceback, scenario, as_obj):
        attacker_str = ""
        victim_str = ""

        for (key_asn, _, _, origin), outcome in traceback.items():
            if key_asn == as_obj.asn:
                # This is extremely messy looking switch case, may want to rewrite in future
                if (
                    outcome == Outcomes.DISCONNECTED.value
                    and origin in scenario.attacker_asns
                ):
                    attacker_str = "&#8869;"
                elif (
                    outcome == Outcomes.DISCONNECTED.value
                    and origin in scenario.victim_asns
                ):
                    victim_str = "&#8869;"
                # allowing a packet takes priority over blocking a packet
                # attacker sends packets to all neighbors
                # if even one packet reaches the reflector, it is considered an attacker succes
                elif outcome == Outcomes.FALSE_NEGATIVE.value and attacker_str not in [
                    "&#8869;"
                ]:
                    attacker_str = "&#10004;"
                elif outcome == Outcomes.TRUE_POSITIVE.value and attacker_str not in [
                    "&#8869;",
                    "&#10004;",
                ]:
                    attacker_str = "&#10006;"
                # Victim behaves as normal, should only have one of these two outcomes (excluding disconnected)
                elif outcome == Outcomes.TRUE_NEGATIVE.value and victim_str not in [
                    "&#8869;"
                ]:
                    victim_str = "&#10004;"
                elif outcome == Outcomes.FALSE_POSITIVE.value and victim_str not in [
                    "&#8869;",
                    "&#10004;",
                ]:
                    victim_str = "&#10006;"

                elif (
                    outcome == Outcomes.FORWARD.value
                    and origin in scenario.attacker_asns
                    and attacker_str not in ["&#8869;", "&#10004;", "&#10006;"]
                ):
                    attacker_str = "&#10003;"
                elif (
                    outcome == Outcomes.FORWARD.value
                    and origin in scenario.victim_asns
                    and victim_str not in ["&#8869;", "&#10004;", "&#10006;"]
                ):
                    victim_str = "&#10003;"

                elif (
                    outcome == Outcomes.A_FILTERED_ON_PATH.value
                    and origin in scenario.attacker_asns
                    and attacker_str not in ["&#8869;", "&#10004;", "&#10006;"]
                ):
                    attacker_str = "&#10005;"
                elif (
                    outcome == Outcomes.V_FILTERED_ON_PATH.value
                    and origin in scenario.victim_asns
                    and victim_str not in ["&#8869;", "&#10004;", "&#10006;"]
                ):
                    victim_str = "&#10005;"

        return attacker_str, victim_str

    def _get_html(
        self,
        as_obj: "AS",
        engine: BaseSimulationEngine,
        traceback: dict,
        scenario: SAVScenarioDSR,
        display_next_hop_asn: bool,
    ) -> str:
        if display_next_hop_asn:
            colspan = 5
        else:
            colspan = 4
        asn_str = str(as_obj.asn)
        edge_server_str = "&#9889;"
        anycast_server_str = "&#9729;&#65039;"
        user_str = "&#128516;"
        if as_obj.asn in scenario.edge_server_asns:
            asn_str = edge_server_str + asn_str + edge_server_str
        elif as_obj.asn in scenario.anycast_server_asns:
            asn_str = anycast_server_str + asn_str + anycast_server_str
        elif as_obj.asn in scenario.user_asns:
            asn_str = user_str + asn_str + user_str

        if as_obj.asn in scenario.sav_policy_asn_dict:
            sav_policy_str = scenario.sav_policy_asn_dict.get(as_obj.asn).name
        else:
            sav_policy_str = "No SAV"

        attacker_str = ""
        victim_str = ""
        if as_obj.asn in scenario.edge_server_asns:
            victim_str = "O"
        else:
            attacker_str, victim_str = self._get_outcome_html(
                traceback, scenario, as_obj
            )

        html = f"""<
            <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="{colspan}">
            <TR>
                <TD BGCOLOR="#ff6060" WIDTH="30" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER" VALIGN="MIDDLE">{attacker_str}</TD>
                <TD BORDER="0" ALIGN="CENTER" VALIGN="MIDDLE">{asn_str}</TD>
                <TD BGCOLOR="#90ee90" WIDTH="30" HEIGHT="30" FIXEDSIZE="TRUE" ALIGN="CENTER" VALIGN="MIDDLE">{victim_str}</TD>
            </TR>
            <TR>
                <TD COLSPAN="{colspan}" BORDER="0" ALIGN="CENTER" VALIGN="MIDDLE">{as_obj.policy.name}</TD>
            </TR>
            <TR>
                <TD COLSPAN="{colspan}" BORDER="0" ALIGN="CENTER" VALIGN="MIDDLE"><b>{sav_policy_str}</b></TD>
            </TR>"""

        local_rib_anns = tuple(list(as_obj.policy._local_rib.values()))
        local_rib_anns = tuple(
            sorted(
                local_rib_anns,
                key=lambda x: ipaddress.ip_network(x.prefix).num_addresses,
                reverse=True,
            )
        )
        if len(local_rib_anns) > 0:
            html += f"""<TR>
                        <TD COLSPAN="{colspan}" ALIGN="CENTER" VALIGN="MIDDLE">Local RIB</TD>
                      </TR>"""

            for ann in local_rib_anns:
                if ann.origin not in (scenario.edge_server_asns):
                    # print(f"\nDIAG: \nAnn: \n{ann}")
                    mask = "/" + ann.prefix.split("/")[-1]
                    path = ", ".join(str(x) for x in ann.as_path)
                    ann_help = ""
                    if getattr(ann, "blackhole", False):
                        ann_help = "&#10041;"
                    elif getattr(ann, "preventive", False):
                        ann_help = "&#128737;"
                    elif any(x == ann.origin for x in scenario.edge_server_asns):
                        ann_help = edge_server_str
                    elif any(x == ann.origin for x in scenario.anycast_server_asns):
                        ann_help = anycast_server_str
                    elif any(x == ann.origin for x in scenario.user_asns):
                        ann_help = user_str
                    else:
                        raise Exception(f"Not valid ann for rib? {ann}")

                    html += f"""<TR>
                                <TD>{mask}</TD>
                                <TD>{path}</TD>
                                <TD>{ann_help}</TD>"""
                    if display_next_hop_asn:
                        html += f"""<TD>{ann.next_hop_asn}</TD>"""
                    html += """</TR>"""

        html += "</TABLE>>"
        return html

    def _get_kwargs(
        self,
        as_obj: "AS",
        engine: BaseSimulationEngine,
        traceback: dict,
        scenario: SAVScenarioDSR,
    ) -> dict[str, str]:
        kwargs = {
            "color": "black",
            "style": "filled",
            "fillcolor": "white",
            "gradientangle": "270",
        }

        # If the as obj is the edge server
        if as_obj.asn in scenario.edge_server_asns:
            kwargs.update({"fillcolor": "#90ee90", "shape": "doublecircle"})
        # As obj is the anycast server
        elif as_obj.asn in scenario.anycast_server_asns:
            kwargs.update({"fillcolor": "#eeb690", "shape": "doublecircle"})
        # obj is the user
        elif as_obj.asn in scenario.user_asns:
            kwargs.update({"fillcolor": "#99d9ea", "shape": "doublecircle"})

        # As obj is one of the above
        else:
            kwargs.update({"fillcolor": "grey:white"})

            if as_obj.policy.__class__ not in [BGP, BGPFull]:
                kwargs["shape"] = "octagon"
        return kwargs

    def _add_traffic_edges(self, scenario: SAVScenarioDSR, traceback):
        # NOTE: since this does not track visted ASes
        #       multiple attackers will cause multiple
        #       traffic lines over same edge
        for key, outcome in traceback.items():
            asn, _, prev_hop, origin = key
            if origin in scenario.edge_server_asns:
                color = "#22B14C"
                # if outcome in [Outcomes.TRUE_NEGATIVE.value, Outcomes.FALSE_POSITIVE]:
                if prev_hop not in [None, -1] and outcome not in [Outcomes.V_FILTERED_ON_PATH.value, Outcomes.A_FILTERED_ON_PATH.value]:
                    self.dot.edge(
                        str(prev_hop),
                        str(asn),
                        constraint="false",
                        color=color,
                        style="dotted",
                        penwidth="3",
                    )
