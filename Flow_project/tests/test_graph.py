import unittest
import sys
import os

# Добавляем путь к src для импорта модулей
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from graph import Graph, Node, Edge
from exceptions import InvalidInputError, NodeNotFoundError, EdgeNotFoundError

class TestNode(unittest.TestCase):
    """Тесты для класса Node."""
    
    def test_node_creation(self):
        """Тест создания узла."""
        node = Node("A", "Node A")
        self.assertEqual(node.id, "A")
        self.assertEqual(node.name, "Node A")
        self.assertFalse(node.is_source)
        self.assertFalse(node.is_sink)
    
    def test_node_creation_with_flags(self):
        """Тест создания узла с флагами источника/стока."""
        node = Node("S", "Source", is_source=True)
        self.assertTrue(node.is_source)
        self.assertFalse(node.is_sink)
        
        node = Node("T", "Sink", is_sink=True)
        self.assertFalse(node.is_source)
        self.assertTrue(node.is_sink)
    
    def test_node_creation_empty_id(self):
        """Тест создания узла с пустым ID."""
        with self.assertRaises(InvalidInputError):
            Node("", "Empty ID")

class TestEdge(unittest.TestCase):
    """Тесты для класса Edge."""
    
    def test_edge_creation(self):
        """Тест создания ребра."""
        edge = Edge("e1", "A", "B", 10.0)
        self.assertEqual(edge.id, "e1")
        self.assertEqual(edge.start_node_id, "A")
        self.assertEqual(edge.end_node_id, "B")
        self.assertEqual(edge.capacity, 10.0)
        self.assertEqual(edge.flow, 0.0)
    
    def test_edge_creation_with_flow(self):
        """Тест создания ребра с ненулевым потоком."""
        edge = Edge("e1", "A", "B", 10.0, 5.0)
        self.assertEqual(edge.flow, 5.0)
        self.assertEqual(edge.residual_capacity, 5.0)
    
    def test_edge_creation_negative_capacity(self):
        """Тест создания ребра с отрицательной пропускной способностью."""
        with self.assertRaises(InvalidInputError):
            Edge("e1", "A", "B", -5.0)
    
    def test_edge_creation_negative_flow(self):
        """Тест создания ребра с отрицательным потоком."""
        with self.assertRaises(InvalidInputError):
            Edge("e1", "A", "B", 10.0, -1.0)
    
    def test_edge_creation_flow_exceeds_capacity(self):
        """Тест создания ребра с потоком, превышающим пропускную способность."""
        with self.assertRaises(InvalidInputError):
            Edge("e1", "A", "B", 5.0, 10.0)

class TestGraph(unittest.TestCase):
    """Тесты для класса Graph."""
    
    def setUp(self):
        """Настройка перед каждым тестом."""
        self.graph = Graph()
    
    def test_add_node(self):
        """Тест добавления узла."""
        node = self.graph.add_node("A", "Node A")
        self.assertEqual(node.id, "A")
        self.assertIn("A", self.graph.nodes)
        self.assertIn("A", self.graph.adjacency_list)
    
    def test_add_duplicate_node(self):
        """Тест добавления узла с существующим ID."""
        self.graph.add_node("A", "Node A")
        with self.assertRaises(InvalidInputError):
            self.graph.add_node("A", "Another Node A")
    
    def test_get_node(self):
        """Тест получения узла."""
        self.graph.add_node("A", "Node A")
        node = self.graph.get_node("A")
        self.assertEqual(node.id, "A")
    
    def test_get_nonexistent_node(self):
        """Тест получения несуществующего узла."""
        with self.assertRaises(NodeNotFoundError):
            self.graph.get_node("X")
    
    def test_remove_node(self):
        """Тест удаления узла."""
        self.graph.add_node("A", "Node A")
        self.graph.remove_node("A")
        self.assertNotIn("A", self.graph.nodes)
        self.assertNotIn("A", self.graph.adjacency_list)
    
    def test_remove_node_with_edges(self):
        """Тест удаления узла с инцидентными ребрами."""
        self.graph.add_node("A", "Node A")
        self.graph.add_node("B", "Node B")
        self.graph.add_edge("e1", "A", "B", 10.0)
        
        self.graph.remove_node("A")
        self.assertNotIn("A", self.graph.nodes)
        self.assertNotIn("e1", self.graph.edges)
    
    def test_add_edge(self):
        """Тест добавления ребра."""
        self.graph.add_node("A", "Node A")
        self.graph.add_node("B", "Node B")
        
        edge = self.graph.add_edge("e1", "A", "B", 10.0)
        self.assertEqual(edge.id, "e1")
        self.assertIn("e1", self.graph.edges)
        self.assertIn("e1", self.graph.adjacency_list["A"])
    
    def test_add_edge_nonexistent_nodes(self):
        """Тест добавления ребра с несуществующими узлами."""
        with self.assertRaises(NodeNotFoundError):
            self.graph.add_edge("e1", "A", "B", 10.0)
    
    def test_add_duplicate_edge(self):
        """Тест добавления ребра с существующим ID."""
        self.graph.add_node("A", "Node A")
        self.graph.add_node("B", "Node B")
        self.graph.add_edge("e1", "A", "B", 10.0)
        
        with self.assertRaises(InvalidInputError):
            self.graph.add_edge("e1", "A", "B", 5.0)
    
    def test_add_self_loop(self):
        """Тест добавления петли."""
        self.graph.add_node("A", "Node A")
        with self.assertRaises(InvalidInputError):
            self.graph.add_edge("e1", "A", "A", 10.0)
    
    def test_get_edge(self):
        """Тест получения ребра."""
        self.graph.add_node("A", "Node A")
        self.graph.add_node("B", "Node B")
        self.graph.add_edge("e1", "A", "B", 10.0)
        
        edge = self.graph.get_edge("e1")
        self.assertEqual(edge.id, "e1")
    
    def test_get_nonexistent_edge(self):
        """Тест получения несуществующего ребра."""
        with self.assertRaises(EdgeNotFoundError):
            self.graph.get_edge("e1")
    
    def test_remove_edge(self):
        """Тест удаления ребра."""
        self.graph.add_node("A", "Node A")
        self.graph.add_node("B", "Node B")
        self.graph.add_edge("e1", "A", "B", 10.0)
        
        self.graph.remove_edge("e1")
        self.assertNotIn("e1", self.graph.edges)
        self.assertNotIn("e1", self.graph.adjacency_list["A"])
    
    def test_get_edges_from_node(self):
        """Тест получения ребер из узла."""
        self.graph.add_node("A", "Node A")
        self.graph.add_node("B", "Node B")
        self.graph.add_node("C", "Node C")
        
        self.graph.add_edge("e1", "A", "B", 10.0)
        self.graph.add_edge("e2", "A", "C", 5.0)
        
        edges = self.graph.get_edges_from_node("A")
        self.assertEqual(len(edges), 2)
        edge_ids = {edge.id for edge in edges}
        self.assertEqual(edge_ids, {"e1", "e2"})
    
    def test_has_edge(self):
        """Тест проверки существования ребра."""
        self.graph.add_node("A", "Node A")
        self.graph.add_node("B", "Node B")
        self.graph.add_edge("e1", "A", "B", 10.0)
        
        self.assertTrue(self.graph.has_edge("A", "B"))
        self.assertFalse(self.graph.has_edge("B", "A"))
        self.assertFalse(self.graph.has_edge("A", "C"))
    
    def test_get_source_sink_nodes(self):
        """Тест получения источников и стоков."""
        self.graph.add_node("S", "Source", is_source=True)
        self.graph.add_node("T", "Sink", is_sink=True)
        self.graph.add_node("A", "Normal")
        
        sources = self.graph.get_source_nodes()
        sinks = self.graph.get_sink_nodes()
        
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].id, "S")
        self.assertEqual(len(sinks), 1)
        self.assertEqual(sinks[0].id, "T")

if __name__ == '__main__':
    unittest.main()