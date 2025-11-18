import unittest
import sys
import os

# Добавляем путь к src для импорта модулей
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from graph import Graph
from algorithms import FordFulkerson
from exceptions import NetworkNotValidError

class TestFordFulkerson(unittest.TestCase):
    """Тесты для алгоритма Форда-Фалкерсона."""
    
    def setUp(self):
        """Настройка перед каждым тестом."""
        self.graph = Graph()
    
    def create_simple_network(self):
        """Создает простую тестовую сеть."""
        # s -> A -> t
        self.graph.add_node("s", "Source", is_source=True)
        self.graph.add_node("A", "Node A")
        self.graph.add_node("t", "Sink", is_sink=True)
        
        self.graph.add_edge("e1", "s", "A", 10.0)
        self.graph.add_edge("e2", "A", "t", 5.0)
    
    def create_complex_network(self):
        """Создает более сложную тестовую сеть."""
        # Классический пример сети
        self.graph.add_node("s", "Source", is_source=True)
        self.graph.add_node("A", "Node A")
        self.graph.add_node("B", "Node B")
        self.graph.add_node("C", "Node C")
        self.graph.add_node("D", "Node D")
        self.graph.add_node("t", "Sink", is_sink=True)
        
        self.graph.add_edge("e1", "s", "A", 10.0)
        self.graph.add_edge("e2", "s", "C", 10.0)
        self.graph.add_edge("e3", "A", "B", 4.0)
        self.graph.add_edge("e4", "A", "C", 2.0)
        self.graph.add_edge("e5", "A", "D", 8.0)
        self.graph.add_edge("e6", "B", "t", 10.0)
        self.graph.add_edge("e7", "C", "D", 9.0)
        self.graph.add_edge("e8", "D", "t", 10.0)
    
    def test_simple_network_max_flow(self):
        """Тест максимального потока в простой сети."""
        self.create_simple_network()
        ff = FordFulkerson(self.graph)
        
        max_flow = ff.calculate_max_flow("s", "t")
        self.assertEqual(max_flow, 5.0)  # Ограничено ребром A->t
    
    def test_complex_network_max_flow(self):
        """Тест максимального потока в сложной сети."""
        self.create_complex_network()
        ff = FordFulkerson(self.graph)
        
        max_flow = ff.calculate_max_flow("s", "t")
        # Ожидаемый максимальный поток для этой сети
        self.assertEqual(max_flow, 15.0)
    
    def test_no_source_sink(self):
        """Тест сети без источника или стока."""
        self.graph.add_node("A", "Node A")
        self.graph.add_node("B", "Node B")
        self.graph.add_edge("e1", "A", "B", 10.0)
        
        ff = FordFulkerson(self.graph)
        with self.assertRaises(NetworkNotValidError):
            ff.calculate_max_flow("A", "B")
    
    def test_same_source_sink(self):
        """Тест с одинаковым источником и стоком."""
        self.graph.add_node("A", "Node A", is_source=True, is_sink=True)
        
        ff = FordFulkerson(self.graph)
        with self.assertRaises(NetworkNotValidError):
            ff.calculate_max_flow("A", "A")
    
    def test_disconnected_network(self):
        """Тест несвязной сети."""
        self.graph.add_node("s", "Source", is_source=True)
        self.graph.add_node("t", "Sink", is_sink=True)
        # Нет ребер между s и t
        
        ff = FordFulkerson(self.graph)
        max_flow = ff.calculate_max_flow("s", "t")
        self.assertEqual(max_flow, 0.0)
    
    def test_min_cut(self):
        """Тест нахождения минимального разреза."""
        self.create_complex_network()
        ff = FordFulkerson(self.graph)
        
        max_flow = ff.calculate_max_flow("s", "t")
        S, T = ff.get_min_cut("s")
        
        # Проверяем, что источник в S
        self.assertIn("s", S)
        # Проверяем, что сток в T
        self.assertIn("t", T)
        # Проверяем, что множества не пересекаются
        self.assertFalse(set(S) & set(T))
    
    def test_flow_conservation(self):
        """Тест сохранения потока."""
        self.create_complex_network()
        ff = FordFulkerson(self.graph)
        
        max_flow = ff.calculate_max_flow("s", "t")
        
        # Проверяем сохранение потока для каждого узла (кроме источника и стока)
        for node in self.graph.get_all_nodes():
            if node.is_source or node.is_sink:
                continue
                
            inflow = 0
            outflow = 0
            
            # Суммируем входящие потоки
            for edge in self.graph.get_all_edges():
                if edge.end_node_id == node.id:
                    inflow += edge.flow
            
            # Суммируем исходящие потоки
            for edge in self.graph.get_edges_from_node(node.id):
                outflow += edge.flow
            
            # Поток должен сохраняться
            self.assertAlmostEqual(inflow, outflow, places=6)
    
    def test_capacity_constraints(self):
        """Тест ограничений пропускной способности."""
        self.create_complex_network()
        ff = FordFulkerson(self.graph)
        
        max_flow = ff.calculate_max_flow("s", "t")
        
        # Проверяем, что поток не превышает пропускную способность
        for edge in self.graph.get_all_edges():
            self.assertLessEqual(edge.flow, edge.capacity)
            self.assertGreaterEqual(edge.flow, 0.0)

class TestResidualGraph(unittest.TestCase):
    """Тесты для остаточного графа."""
    
    def test_residual_graph_creation(self):
        """Тест создания остаточного графа."""
        graph = Graph()
        graph.add_node("s", "Source", is_source=True)
        graph.add_node("A", "Node A")
        graph.add_node("t", "Sink", is_sink=True)
        
        graph.add_edge("e1", "s", "A", 10.0, 3.0)  # Поток 3.0
        graph.add_edge("e2", "A", "t", 5.0, 2.0)   # Поток 2.0
        
        ff = FordFulkerson(graph)
        
        # Проверяем узлы в остаточном графе
        residual_nodes = ff.residual_graph.get_all_nodes()
        self.assertEqual(len(residual_nodes), 3)
        
        # Проверяем ребра в остаточном графе
        residual_edges = ff.residual_graph.get_all_edges()
        # Должны быть 4 ребра: 2 прямых и 2 обратных
        self.assertEqual(len(residual_edges), 4)
        
        # Проверяем пропускные способности
        forward_e1 = ff.residual_graph.get_edge("e1_forward")
        self.assertEqual(forward_e1.capacity, 7.0)  # 10.0 - 3.0
        
        backward_e1 = ff.residual_graph.get_edge("e1_backward")
        self.assertEqual(backward_e1.capacity, 3.0)  # Текущий поток
        
        forward_e2 = ff.residual_graph.get_edge("e2_forward")
        self.assertEqual(forward_e2.capacity, 3.0)  # 5.0 - 2.0
        
        backward_e2 = ff.residual_graph.get_edge("e2_backward")
        self.assertEqual(backward_e2.capacity, 2.0)  # Текущий поток

if __name__ == '__main__':
    unittest.main()