"""
Модуль пользовательского интерфейса.
"""

from .main_window import MainWindow
from .graph_widget import GraphWidget
from .node_graphics_item import NodeGraphicsItem
from .edge_graphics_item import EdgeGraphicsItem
from .dialogs import (AddNodeDialog, EditNodeDialog, AddEdgeDialog, 
                     EditEdgeDialog, FlowResultDialog)

__all__ = [
    'MainWindow',
    'GraphWidget', 
    'NodeGraphicsItem',
    'EdgeGraphicsItem',
    'AddNodeDialog', 'EditNodeDialog', 'AddEdgeDialog',
    'EditEdgeDialog', 'FlowResultDialog'
]