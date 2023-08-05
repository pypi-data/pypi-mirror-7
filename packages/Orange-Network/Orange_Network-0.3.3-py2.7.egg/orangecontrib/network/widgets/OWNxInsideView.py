"""
<name>Net Inside View</name>
<description>Orange widget for community detection in networks</description>
<icon>icons/NetworkInsideView.svg</icon>
<contact>Miha Stajdohar (miha.stajdohar(@at@)gmail.com)</contact> 
<priority>6460</priority>
"""

import Orange
import OWGUI

from OWWidget import *


NAME = "Net Inside View"
DESCRIPTION = "Orange widget for community detection in networks"
ICON = "icons/NetworkInsideView.svg"
PRIORITY = 6460

OUTPUTS = [("Nx View", Orange.network.NxView)]

REPLACES = ["_network.widgets.OWNxInsideView.OWNxInsideView"]


class NxInsideView(Orange.network.NxView):
    """Network Inside View
    
    """

    def __init__(self, nhops):
        Orange.network.NxView.__init__(self)

        self._nhops = nhops
        self._center_node = None

    def init_network(self, graph):
        self._network = graph

        if graph is None:
            return None

        selected = self._nx_explorer.networkCanvas.selected_nodes()
        if selected is None or len(selected) <= 0:
            self._center_node = graph.nodes_iter().next()
        else:
            self._center_node = selected[0]

        nodes = self._get_neighbors()
        return Orange.network.nx.Graph.subgraph(self._network, nodes)

    def update_network(self):
        nodes = self._get_neighbors()
        subnet = Orange.network.nx.Graph.subgraph(self._network, nodes)

        if self._nx_explorer is not None:
            self._nx_explorer.change_graph(subnet)

    def set_nhops(self, nhops):
        self._nhops = nhops

    def node_selection_changed(self):
        selection = self._nx_explorer.networkCanvas.selected_nodes()
        if len(selection) == 1:
            self._center_node = selection[0]
            self.update_network()

    def _get_neighbors(self):
        nodes = set([self._center_node])
        for n in range(self._nhops):
            neighbors = set()
            for node in nodes:
                neighbors.update(self._network.neighbors(node))
            nodes.update(neighbors)
        return nodes

class OWNxInsideView(OWWidget):

    settingsList = ['_nhops']

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager, 'Net Inside View')

        self.inputs = []
        self.outputs = [("Nx View", Orange.network.NxView)]

        self._nhops = 2

        self.loadSettings()

        ib = OWGUI.widgetBox(self.controlArea, "Preferences", orientation="vertical")
        OWGUI.spin(ib, self, "_nhops", 1, 6, 1, label="Number of hops: ", callback=self.update_view)

        self.inside_view = NxInsideView(self._nhops)
        self.send("Nx View", self.inside_view)

    def update_view(self):
        self.inside_view.set_nhops(self._nhops)

        self.inside_view.update_network()
