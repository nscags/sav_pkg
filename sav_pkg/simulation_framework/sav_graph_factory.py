from bgpy.simulation_framework import GraphFactory


class SAVGraphFactory(GraphFactory):

    def __init__(self, pickle_path, graph_dir, **kwargs):
        from sav_pkg.utils.utils import get_metric_keys
        super().__init__(
            pickle_path=pickle_path,
            graph_dir=graph_dir,
            metric_keys=tuple(list(get_metric_keys())),
            **kwargs
        )