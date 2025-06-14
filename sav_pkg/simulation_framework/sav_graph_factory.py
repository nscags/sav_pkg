from bgpy.simulation_framework import GraphFactory

from sav_pkg.utils.utils import get_metric_keys


class SAVGraphFactory(GraphFactory):

    def __init__(self, pickle_path, graph_dir, **kwargs):
        super().__init__(
            pickle_path=pickle_path,
            graph_dir=graph_dir,
            metric_keys=tuple(list(get_metric_keys())),
            **kwargs
        )