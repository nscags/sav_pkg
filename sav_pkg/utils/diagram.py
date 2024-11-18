from pathlib import Path
from typing import Optional, TYPE_CHECKING

from graphviz import Digraph
import ipaddress

from bgpy.simulation_engine import BGP
from bgpy.simulation_engine import BGPFull
from bgpy.simulation_engine import BaseSimulationEngine
from bgpy.simulation_framework import Scenario
from bgpy.utils import Diagram

from sav_pkg.enums import Outcomes

if TYPE_CHECKING:
    from bgpy.as_graphs.base.as_graph import AS


class SAVDiagram(Diagram):
    """Creates a diagram of an AS graph with traceback"""

    def __init__(self):
        self.dot: Digraph = Digraph(format="png")
        # purple is cooler but I guess that's not paper worthy
        # self.dot.attr(bgcolor='purple:pink')

    def generate_as_graph(
        self,
        engine: BaseSimulationEngine,
        scenario: Scenario,
        # Just the data plane
        traceback: dict[int, int],
        description: str,
        metric_tracker,
        diagram_ranks: tuple[tuple["AS", ...], ...],
        static_order: bool = False,
        path: Optional[Path] = None,
        view: bool = False,
    ) -> None:
        self._add_legend(traceback, scenario)
        display_next_hop_asn = self._display_next_hop_asn(engine, scenario)
        self._add_ases(engine, traceback, scenario, display_next_hop_asn)
        self._add_edges(engine)
        self._add_traffic_edges(scenario, traceback)
        self._add_diagram_ranks(diagram_ranks, static_order)
        self._add_description(description, display_next_hop_asn)
        self._render(path=path, view=view)
    

    def _get_count(self, traceback, scenario):
        fn = tp = fp = tn = ad = vd = af = vf = 0

        for key, outcome in traceback.items():
            if outcome == Outcomes.FALSE_NEGATIVE.value: 
                fn += 1
            elif outcome == Outcomes.TRUE_POSITIVE.value:
                tp += 1
            elif outcome == Outcomes.FALSE_POSITIVE.value:
                fp += 1
            elif outcome == Outcomes.TRUE_NEGATIVE.value:
                tn += 1
            elif outcome == Outcomes.DISCONNECTED.value and key[3] in scenario.attacker_asns:
                ad += 1
            elif outcome == Outcomes.DISCONNECTED.value and key[3] in scenario.victim_asns:
                vd += 1
            elif (outcome == Outcomes.FILTERED_ON_PATH.value 
                  and key[0] in scenario.reflector_asns 
                  and key[3] in scenario.attacker_asns):
                af += 1
            elif (outcome == Outcomes.FILTERED_ON_PATH.value 
                  and key[0] in scenario.reflector_asns 
                  and key[3] in scenario.victim_asns):
                vf += 1

        return fn, tp, fp, tn, ad, vd, af, vf


    def _add_legend(self, traceback: dict, scenario: Scenario) -> None:
        """Adds legend to the graph with outcome counts"""

        fn, tp, fp, tn, ad, vd, af, vf = self._get_count(traceback, scenario)

        html = f"""<
            <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
                <TR>
                    <TD COLSPAN="6" BORDER="0" ALIGN="CENTER" VALIGN="MIDDLE"><b>(Data Plane Outcomes)</b></TD>
                </TR>
                <TR>
                    <TD COLSPAN="2" BORDER="0" ALIGN="CENTER" VALIGN="MIDDLE">(Attacker Outcomes)</TD>
                    <TD COLSPAN="2" BORDER="0" ALIGN="CENTER" VALIGN="MIDDLE">(Victim Outcomes)</TD>
                </TR>
                <TR>
                    <TD BGCOLOR="#ff6060:white">&#10004; FALSE NEGATIVE &#10004;</TD>
                    <TD>{fn}</TD>
                    <TD BGCOLOR="#90ee90:white">&#10004; TRUE NEGATIVE &#10004;</TD>
                    <TD>{tn}</TD>
                </TR>
                <TR>
                    <TD BGCOLOR="#ff6060:white">&#10006; TRUE POSITIVE &#10006;</TD>
                    <TD>{tp}</TD>  
                    <TD BGCOLOR="#90ee90:white">&#10006; FALSE POSITIVE &#10006;</TD>
                    <TD>{fp}</TD>
                </TR>
                <TR>
                    <TD BGCOLOR="#ff6060:white">&#10005; FILTERED ON PATH &#10005;</TD>
                    <TD>{af}</TD> 
                    <TD BGCOLOR="#90ee90:white">&#10005; FILTERED ON PATH &#10005;</TD>
                    <TD>{vf}</TD>
                </TR>
                <TR>
                    <TD BGCOLOR="#ff6060:white">&#8869; DISCONNECTED &#8869;</TD>
                    <TD>{ad}</TD> 
                    <TD BGCOLOR="#90ee90:white">&#8869; DISCONNECTED &#8869;</TD>
                    <TD>{vd}</TD>
                </TR>
        """
        
        # ROAs takes up the least space right underneath the legend
        # which is why we have this here instead of a separate node
        # html += """
        #       <TR>
        #         <TD COLSPAN="2" BORDER="0">ROAs (prefix, origin, max_len)</TD>
        #       </TR>
        #       """
        # for roa_info in scenario.roa_infos:
        #     html += f"""
        #       <TR>
        #         <TD>{roa_info.prefix}</TD>
        #         <TD>{roa_info.origin}</TD>
        #         <TD>{roa_info.max_length}</TD>
        #       </TR>"""
        html += """</TABLE>>"""

        kwargs = {"color": "black", "style": "filled", "fillcolor": "white"}
        self.dot.node("Legend", html, shape="plaintext", **kwargs)

    def _display_next_hop_asn(
        self, engine: BaseSimulationEngine, scenario: Scenario
    ) -> bool:
        """Displays the next hop ASN

        We want to display the next hop ASN any time it has been manipulated
        That only happens when the next_hop_asn is not equal to the as object's ASN
        (which occurs when the AS is the origin) or the next ASN in the path
        """

        for as_obj in engine.as_graph:
            for ann in as_obj.policy._local_rib.values():
                if len(ann.as_path) == 1 and ann.as_path[0] != ann.next_hop_asn:
                    return True
                elif len(ann.as_path) > 1 and ann.as_path[1] != ann.next_hop_asn:
                    return True
        return False

    def _add_ases(
        self,
        engine: BaseSimulationEngine,
        traceback: dict,
        scenario: Scenario,
        display_next_hop_asn: bool,
    ) -> None:
        # First add all nodes to the graph
        for as_obj in engine.as_graph:
            self._encode_as_obj_as_node(
                self.dot, as_obj, engine, traceback, scenario, display_next_hop_asn
            )

    def _encode_as_obj_as_node(
        self,
        subgraph: Digraph,
        as_obj: "AS",
        engine: BaseSimulationEngine,
        traceback: dict,
        scenario: Scenario,
        display_next_hop_asn: bool,
    ) -> None:
        kwargs = dict()

        html = self._get_html(as_obj, engine, traceback, scenario, display_next_hop_asn)

        kwargs = self._get_kwargs(as_obj, engine, traceback, scenario)

        subgraph.node(str(as_obj.asn), html, **kwargs)


    def _get_outcome_html(self, traceback, scenario, as_obj):
        
        attacker_str = ""
        victim_str = ""
        
        for (key_asn, _, _, origin), outcome in traceback.items():
            if key_asn == as_obj.asn:
                # This is extremely messy looking switch case, may want to rewrite in future
                if outcome == Outcomes.DISCONNECTED.value and origin in scenario.attacker_asns:
                    attacker_str = "&#8869;"
                elif outcome == Outcomes.DISCONNECTED.value and origin in scenario.victim_asns:
                    victim_str = "&#8869;"
                # allowing a packet takes priority over blocking a packet
                # attacker sends packets to all neighbors
                # if even one packet reaches the reflector, it is considered an attacker succes
                elif outcome == Outcomes.FALSE_NEGATIVE.value and attacker_str not in ["&#8869;"]:
                    attacker_str = "&#10004;"
                elif outcome == Outcomes.TRUE_POSITIVE.value and attacker_str not in ["&#8869;", "&#10004;"]: 
                    attacker_str = "&#10006;"
                # Victim behaves as normal, should only have one of these two outcomes (excluding disconnected)
                elif outcome == Outcomes.TRUE_NEGATIVE.value and victim_str not in ["&#8869;"]:
                    victim_str = "&#10004;"
                elif outcome == Outcomes.FALSE_POSITIVE.value and victim_str not in ["&#8869;", "&#10004;"]:
                    victim_str = "&#10006;"
                
                elif outcome == Outcomes.FORWARD.value and origin in scenario.attacker_asns and attacker_str not in ["&#8869;", "&#10004;", "&#10006;"]:
                    attacker_str = "&#10003;"
                elif outcome == Outcomes.FORWARD.value and origin in scenario.victim_asns and victim_str not in ["&#8869;", "&#10004;", "&#10006;"]:
                    victim_str = "&#10003;"

                elif outcome == Outcomes.FILTERED_ON_PATH.value and origin in scenario.attacker_asns and attacker_str not in ["&#8869;", "&#10004;", "&#10006;"]:
                    attacker_str = "&#10005;"
                elif outcome == Outcomes.FILTERED_ON_PATH.value and origin in scenario.victim_asns and victim_str not in ["&#8869;", "&#10004;", "&#10006;"]:
                    victim_str ="&#10005;"

        return attacker_str, victim_str


    def _get_html(
        self,
        as_obj: "AS",
        engine: BaseSimulationEngine,
        traceback: dict,
        scenario: Scenario,
        display_next_hop_asn: bool,
    ) -> str:
        if display_next_hop_asn:
            colspan = 5
        else:
            colspan = 4
        asn_str = str(as_obj.asn)
        if as_obj.asn in scenario.victim_asns:
            asn_str = "&#128519;" + asn_str + "&#128519;"
        elif as_obj.asn in scenario.attacker_asns:
            asn_str = "&#128520;" + asn_str + "&#128520;"
        elif as_obj.asn in scenario.reflector_asns:
            asn_str = "&#128526;" + asn_str + "&#128526;"
        
        # make the SAV policy bold (or at least stand out more)
        if as_obj.asn in scenario.sav_policy_asn_dict:
            sav_policy_str = scenario.sav_policy_asn_dict.get(as_obj.asn).name
        else:
            sav_policy_str = "No SAV"


        attacker_str = ""
        victim_str = ""

        if as_obj.asn in scenario.attacker_asns:
            attacker_str = "O"
            victim_str = ""
        elif as_obj.asn in scenario.victim_asns:
            victim_str = "O"
            attacker_str = ""          
        else:
            attacker_str, victim_str = self._get_outcome_html(traceback, scenario, as_obj)
        

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
                <TD COLSPAN="{colspan}" BORDER="0" ALIGN="CENTER" VALIGN="MIDDLE">{sav_policy_str}</TD>
            </TR>"""
        
        # local_rib_anns = tuple(list(as_obj.policy._local_rib.values()))
        # local_rib_anns = tuple(
        #     sorted(
        #         local_rib_anns,
        #         key=lambda x: ipaddress.ip_network(x.prefix).num_addresses,
        #         reverse=True,
        #     )
        # )
        # if len(local_rib_anns) > 0:
        #     html += f"""<TR>
        #                 <TD COLSPAN="{colspan}" ALIGN="CENTER" VALIGN="MIDDLE">Local RIB</TD>
        #               </TR>"""

        #     for ann in local_rib_anns:
        #         # if (ann.as_path[-1] in scenario.attacker_asns or 
        #         #     ann.as_path[-1] in scenario.victim_asns):
        #             mask = "/" + ann.prefix.split("/")[-1]
        #             path = ", ".join(str(x) for x in ann.as_path)
        #             ann_help = ""
        #             if getattr(ann, "blackhole", False):
        #                 ann_help = "&#10041;"
        #             elif getattr(ann, "preventive", False):
        #                 ann_help = "&#128737;"
        #             elif any(x in ann.as_path for x in scenario.attacker_asns):
        #                 ann_help = "&#128520;"
        #             elif any(x == ann.origin for x in scenario.victim_asns):
        #                 ann_help = "&#128519;"
        #             elif any(x == ann.origin for x in scenario.reflector_asns):
        #                 ann_help = "&#128526;"
        #             else:
        #                 raise Exception(f"Not valid ann for rib? {ann}")

        #             html += f"""<TR>
        #                         <TD>{mask}</TD>
        #                         <TD>{path}</TD>
        #                         <TD>{ann_help}</TD>"""
        #             if display_next_hop_asn:
        #                 html += f"""<TD>{ann.next_hop_asn}</TD>"""
        #             html += """</TR>"""

        html += "</TABLE>>"
        return html


    def _get_kwargs(
        self,
        as_obj: "AS",
        engine: BaseSimulationEngine,
        traceback: dict,
        scenario: Scenario,
    ) -> dict[str, str]:
        kwargs = {
            "color": "black",
            "style": "filled",
            "fillcolor": "white",
            "gradientangle": "270",
        }

        # If the as obj is the attacker
        if as_obj.asn in scenario.attacker_asns:
            kwargs.update({"fillcolor": "#ff6060", "shape": "doublecircle"})
            if as_obj.policy.__class__ not in (BGP, BGPFull):
                kwargs["shape"] = "doubleoctagon"
            # If people complain about the red being too dark lol:
            kwargs.update({"fillcolor": "#FF7F7F"})
            # kwargs.update({"fillcolor": "#ff4d4d"})
        # As obj is the victim
        elif as_obj.asn in scenario.victim_asns:
            kwargs.update({"fillcolor": "#90ee90", "shape": "doublecircle"})
            # if as_obj.policy.__class__ not in (BGP, BGPFull):
            #     kwargs["shape"] = "doubleoctagon"
        # obj is the reflector
        elif as_obj.asn in scenario.reflector_asns:
            kwargs.update({"fillcolor": "#99d9ea", "shape": "doublecircle"})
            if as_obj.policy.__class__ not in (BGP, BGPFull):
                kwargs["shape"] = "doubleoctagon"

        # As obj is not attacker or victim or reflector
        else:
            kwargs.update({"fillcolor": "grey:white"})

            if as_obj.policy.__class__ not in [BGP, BGPFull]:
                kwargs["shape"] = "octagon"
        return kwargs


    def _add_traffic_edges(self, scenario, traceback):
        # NOTE: since this does not track visted ASes
        #       multiple attackers will cause multiple
        #       traffic lines over same edge
        for key, outcome in traceback.items():
            asn, _, prev_hop, origin = key
            if origin in scenario.attacker_asns:
                color = 'red'
                    # if outcome in [Outcomes.FALSE_NEGATIVE.value, Outcomes.TRUE_POSITIVE.value]:
                if prev_hop not in [None, -1]:
                    self.dot.edge(str(prev_hop), 
                                    str(asn), 
                                    constraint='false', 
                                    color=color, 
                                    style="dotted", 
                                    penwidth='3',
                    )
            elif origin in scenario.victim_asns:
                color = '#22B14C'
                # if outcome in [Outcomes.TRUE_NEGATIVE.value, Outcomes.FALSE_POSITIVE]:
                if prev_hop not in [None, -1]:
                    self.dot.edge(str(prev_hop), 
                                        str(asn), 
                                        constraint='false', 
                                        color=color, 
                                        style="dotted", 
                                        penwidth='3',
                    )


    def _add_edges(self, engine: BaseSimulationEngine):
        # Then add all connections to the graph
        # Starting with provider to customer
        for as_obj in engine.as_graph:
            # Add provider customer edges
            for customer_obj in as_obj.customers:
                self.dot.edge(str(as_obj.asn), str(customer_obj.asn))
            # Add peer edges
            # Only add if the largest asn is the curren as_obj to avoid dups
            for peer_obj in as_obj.peers:
                if as_obj.asn > peer_obj.asn:
                    self.dot.edge(
                        str(as_obj.asn),
                        str(peer_obj.asn),
                        dir="none",
                        style="dashed",
                        penwidth="2",
                    )


    def _add_diagram_ranks(
        self, diagram_ranks: tuple[tuple["AS", ...], ...], static_order: bool
    ) -> None:
        # TODO: Refactor
        if static_order is False:
            for i, rank in enumerate(diagram_ranks):
                g = Digraph(f"Propagation_rank_{i}")
                g.attr(rank="same")
                for as_obj in rank:
                    g.node(str(as_obj.asn))
                self.dot.subgraph(g)
        else:
            for i, rank in enumerate(diagram_ranks):
                with self.dot.subgraph() as s:
                    s.attr(rank="same")  # set all nodes to the same rank
                    previous_asn = None
                    for as_obj in rank:
                        asn = str(as_obj.asn)
                        s.node(asn)
                        if previous_asn is not None:
                            # Add invisible edge to maintain static order
                            s.edge(previous_asn, asn, style="invis")  # type: ignore
                        previous_asn = asn


    def _add_description(self, description: str, display_next_hop_asn: bool) -> None:
        if display_next_hop_asn:
            description += (
                "\nLocal RIB rows displayed as: " "prefix, as path, origin, next_hop"
            )
        # https://stackoverflow.com/a/57461245/8903959
        self.dot.attr(label=description)