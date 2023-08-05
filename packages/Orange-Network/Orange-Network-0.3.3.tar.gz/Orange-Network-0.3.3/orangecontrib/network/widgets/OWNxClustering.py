"""
<name>Net Clustering</name>
<description>Orange widget for community detection in networks</description>
<icon>icons/NetworkClustering.svg</icon>
<contact>Miha Stajdohar (miha.stajdohar(@at@)gmail.com)</contact>
<priority>6430</priority>
"""

import Orange.network
import Orange.network.community as cd
import OWGUI

from OWWidget import *


NAME = "Net Clustering"
DESCRIPTION = "Orange widget for community detection in networks"
ICON = "icons/NetworkClustering.svg"
PRIORITY = 6430

INPUTS = [("Network", Orange.network.Graph, "setNetwork", Default)]
OUTPUTS = [("Network", Orange.network.Graph),
           ("Community Detection", cd.CommunityDetection)]

REPLACES = ["_network.widgets.OWNxClustering.OWNxClustering"]

class OWNxClustering(OWWidget):

    settingsList = ['method', 'iterationHistory', 'autoApply', 'iterations',
                    'hop_attenuation']

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager, 'Nx Clustering')

        self.inputs = [("Network", Orange.network.Graph,
                        self.setNetwork, Default)]
        self.outputs = [("Network", Orange.network.Graph),
                        ("Community Detection", cd.CommunityDetection)]

        self.net = None
        self.method = 0
        self.iterationHistory = 0
        self.autoApply = 0
        self.iterations = 1000
        self.hop_attenuation = 0.1
        self.loadSettings()

        OWGUI.spin(self.controlArea, self, "iterations", 1,
                   100000, 1, label="Iterations: ")
        ribg = OWGUI.radioButtonsInBox(self.controlArea, self, "method",
                                       [], "Method", callback=self.cluster)
        OWGUI.appendRadioButton(ribg, self, "method",
                        "Label propagation clustering (Raghavan et al., 2007)",
                        callback=self.cluster)

        OWGUI.appendRadioButton(ribg, self, "method",
                        "Label propagation clustering (Leung et al., 2009)",
                        callback=self.cluster)
        OWGUI.doubleSpin(OWGUI.indentedBox(ribg), self, "hop_attenuation",
                         0, 1, 0.01, label="Hop attenuation (delta): ")

        self.info = OWGUI.widgetLabel(self.controlArea, ' ')
        OWGUI.checkBox(self.controlArea, self, "iterationHistory",
                       "Append clustering data on each iteration",
                       callback=self.cluster)
        OWGUI.checkBox(self.controlArea, self, "autoApply",
                       "Commit automatically")
        OWGUI.button(self.controlArea, self, "Commit",
                     callback=lambda b=True: self.cluster(b))

        self.cluster()

    def setNetwork(self, net):
        self.net = net
        if self.autoApply:
            self.cluster()

    def cluster(self, btn=False):
        if not btn and not self.autoApply:
            return

        self.info.setText(' ')

        if self.method == 0:
            alg = cd.label_propagation
            kwargs = {'results2items': 1,
                      'resultHistory2items': self.iterationHistory,
                      'iterations': self.iterations}

        elif self.method == 1:
            alg = cd.label_propagation_hop_attenuation
            kwargs = {'results2items': 1,
                      'resultHistory2items': self.iterationHistory,
                      'iterations': self.iterations,
                      'delta': self.hop_attenuation}

        self.send("Community Detection", cd.CommunityDetection(alg, **kwargs))

        if self.net is None:
            self.send("Network", None)
            return

        labels = alg(self.net, **kwargs)

        self.info.setText('%d clusters found' % len(set(labels.values())))
        self.send("Network", self.net)
