from typing import Dict, List, Optional, Tuple
from collections import deque
from .graph import Graph, Node, Edge
from .exceptions import NetworkNotValidError

class FordFulkerson:
    """Реализация алгоритма Форда-Фалкерсона для поиска максимального потока."""
    
    def __init__(self, graph: Graph):
        self.graph = graph
        self.residual_graph = Graph()
        self._build_residual_graph()
    
    def _build_residual_graph(self):
        """Строит остаточный граф."""
        # Копируем все узлы
        for node in self.graph.get_all_nodes():
            self.residual_graph.add_node(
                node.id, node.name, node.is_source, node.is_sink
            )
        
        # Создаем прямые и обратные ребра
        for edge in self.graph.get_all_edges():
            # Прямое ребро с остаточной пропускной способностью
            if edge.residual_capacity > 0:
                self.residual_graph.add_edge(
                    f"{edge.id}_forward",
                    edge.start_node_id,
                    edge.end_node_id,
                    edge.residual_capacity
                )
            
            # Обратное ребро с пропускной способностью равной текущему потоку
            if edge.flow > 0:
                self.residual_graph.add_edge(
                    f"{edge.id}_backward",
                    edge.end_node_id,
                    edge.start_node_id,
                    edge.flow
                )
    
    def _bfs(self, source_id: str, sink_id: str) -> Optional[Dict[str, str]]:
        """
        Поиск в ширину для нахождения увеличивающего пути.
        Возвращает словарь parent, если путь найден.
        """
        visited = set()
        queue = deque([source_id])
        parent = {}
        
        visited.add(source_id)
        
        while queue:
            current_id = queue.popleft()
            
            if current_id == sink_id:
                return parent
            
            for edge in self.residual_graph.get_edges_from_node(current_id):
                neighbor_id = edge.end_node_id
                if neighbor_id not in visited and edge.capacity > 0:
                    visited.add(neighbor_id)
                    parent[neighbor_id] = (current_id, edge.id)
                    queue.append(neighbor_id)
        
        return None
    
    def _find_augmenting_path(self, source_id: str, sink_id: str) -> Optional[Tuple[float, List[str]]]:
        """Находит увеличивающий путь и возвращает минимальную пропускную способность и путь."""
        parent = self._bfs(source_id, sink_id)
        if not parent:
            return None
        
        # Восстанавливаем путь и находим минимальную пропускную способность
        path = []
        current_id = sink_id
        min_capacity = float('inf')
        
        while current_id != source_id:
            prev_id, edge_id = parent[current_id]
            edge = self.residual_graph.get_edge(edge_id)
            min_capacity = min(min_capacity, edge.capacity)
            path.append(edge_id)
            current_id = prev_id
        
        path.reverse()
        return min_capacity, path
    
    def _update_flows(self, path: List[str], flow: float):
        """Обновляет потоки в исходном графе по найденному пути."""
        for edge_id in path:
            if edge_id.endswith('_forward'):
                # Прямое ребро - увеличиваем поток
                original_edge_id = edge_id.replace('_forward', '')
                original_edge = self.graph.get_edge(original_edge_id)
                original_edge.flow += flow
            elif edge_id.endswith('_backward'):
                # Обратное ребро - уменьшаем поток
                original_edge_id = edge_id.replace('_backward', '')
                original_edge = self.graph.get_edge(original_edge_id)
                original_edge.flow -= flow
    
    def calculate_max_flow(self, source_id: str, sink_id: str) -> float:
        """
        Вычисляет максимальный поток от источника к стоку.
        Возвращает значение максимального потока.
        """
        # Проверяем валидность входных данных
        if source_id not in self.graph.nodes:
            raise NodeNotFoundError(source_id)
        if sink_id not in self.graph.nodes:
            raise NodeNotFoundError(sink_id)
        if source_id == sink_id:
            raise NetworkNotValidError("Источник и сток не могут быть одним узлом")
        
        source_node = self.graph.get_node(source_id)
        if not source_node.is_source:
            raise NetworkNotValidError(f"Узел '{source_id}' не является источником")
        
        sink_node = self.graph.get_node(sink_id)
        if not sink_node.is_sink:
            raise NetworkNotValidError(f"Узел '{sink_id}' не является стоком")
        
        max_flow = 0
        
        while True:
            # Строим остаточный граф заново
            self.residual_graph = Graph()
            self._build_residual_graph()
            
            # Ищем увеличивающий путь
            result = self._find_augmenting_path(source_id, sink_id)
            if not result:
                break
            
            flow, path = result
            max_flow += flow
            
            # Обновляем потоки
            self._update_flows(path, flow)
        
        return max_flow
    
    def get_min_cut(self, source_id: str) -> Tuple[List[str], List[str]]:
        """
        Находит минимальный разрез после вычисления максимального потока.
        Возвращает кортеж (множество S, множество T).
        """
        visited = set()
        queue = deque([source_id])
        
        visited.add(source_id)
        
        while queue:
            current_id = queue.popleft()
            for edge in self.residual_graph.get_edges_from_node(current_id):
                neighbor_id = edge.end_node_id
                if neighbor_id not in visited and edge.capacity > 0:
                    visited.add(neighbor_id)
                    queue.append(neighbor_id)
        
        S = list(visited)  # Множество достижимых из источника узлов
        T = [node_id for node_id in self.graph.nodes if node_id not in visited]
        
        return S, T