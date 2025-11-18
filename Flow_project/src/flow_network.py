from typing import List, Tuple, Dict
from .graph import Graph, Node, Edge
from .algorithms import FordFulkerson
from .exceptions import NodeNotFoundError, EdgeNotFoundError, InvalidInputError, NetworkNotValidError

class FlowNetwork:
    """Класс для управления сетью потока."""
    
    def __init__(self):
        self.graph = Graph()
        self.algorithm = FordFulkerson(self.graph)
    
    # Методы для работы с узлами
    def add_node(self, node_id: str, name: str = "", is_source: bool = False, is_sink: bool = False) -> Node:
        """Добавляет узел в сеть."""
        return self.graph.add_node(node_id, name, is_source, is_sink)
    
    def get_node(self, node_id: str) -> Node:
        """Возвращает узел по ID."""
        return self.graph.get_node(node_id)
    
    def remove_node(self, node_id: str):
        """Удаляет узел из сети."""
        self.graph.remove_node(node_id)
    
    def set_node_as_source(self, node_id: str):
        """Устанавливает узел как источник."""
        node = self.get_node(node_id)
        node.is_source = True
        node.is_sink = False
    
    def set_node_as_sink(self, node_id: str):
        """Устанавливает узел как сток."""
        node = self.get_node(node_id)
        node.is_sink = True
        node.is_source = False
    
    def get_source_node(self) -> Node:
        """Возвращает источник (предполагается один источник)."""
        sources = self.graph.get_source_nodes()
        if not sources:
            raise NetworkNotValidError("В сети нет источника")
        return sources[0]
    
    def get_sink_node(self) -> Node:
        """Возвращает сток (предполагается один сток)."""
        sinks = self.graph.get_sink_nodes()
        if not sinks:
            raise NetworkNotValidError("В сети нет стока")
        return sinks[0]
    
    # Методы для работы с ребрами
    def add_edge(self, edge_id: str, start_node_id: str, end_node_id: str, capacity: float) -> Edge:
        """Добавляет ребро в сеть."""
        return self.graph.add_edge(edge_id, start_node_id, end_node_id, capacity)
    
    def get_edge(self, edge_id: str) -> Edge:
        """Возвращает ребро по ID."""
        return self.graph.get_edge(edge_id)
    
    def remove_edge(self, edge_id: str):
        """Удаляет ребро из сети."""
        self.graph.remove_edge(edge_id)
    
    def update_edge_capacity(self, edge_id: str, new_capacity: float):
        """Обновляет пропускную способность ребра."""
        edge = self.get_edge(edge_id)
        if new_capacity < edge.flow:
            raise InvalidInputError(
                f"Новая пропускная способность ({new_capacity}) "
                f"меньше текущего потока ({edge.flow})"
            )
        edge.capacity = new_capacity
    
    # Методы для вычисления потока
    def calculate_max_flow(self) -> Tuple[float, List[str], List[str]]:
        """Вычисляет максимальный поток и возвращает значение потока и минимальный разрез."""
        source = self.get_source_node()
        sink = self.get_sink_node()
        
        max_flow = self.algorithm.calculate_max_flow(source.id, sink.id)
        S, T = self.algorithm.get_min_cut(source.id)
        
        return max_flow, S, T
    
    def reset_flows(self):
        """Сбрасывает все потоки к нулю."""
        for edge in self.graph.get_all_edges():
            edge.flow = 0
    
    # Методы для получения информации
    def get_all_nodes(self) -> List[Node]:
        """Возвращает все узлы сети."""
        return self.graph.get_all_nodes()
    
    def get_all_edges(self) -> List[Edge]:
        """Возвращает все ребра сети."""
        return self.graph.get_all_edges()
    
    def get_edges_from_node(self, node_id: str) -> List[Edge]:
        """Возвращает все исходящие ребра из узла."""
        return self.graph.get_edges_from_node(node_id)
    
    def validate_network(self) -> bool:
        """Проверяет валидность сети."""
        try:
            sources = self.graph.get_source_nodes()
            sinks = self.graph.get_sink_nodes()
            
            if len(sources) != 1:
                raise NetworkNotValidError("Должен быть ровно один источник")
            if len(sinks) != 1:
                raise NetworkNotValidError("Должен быть ровно один сток")
            
            # Проверяем связность
            source_id = sources[0].id
            sink_id = sinks[0].id
            
            # Простая проверка на достижимость стока из источника
            visited = set()
            stack = [source_id]
            
            while stack:
                current_id = stack.pop()
                if current_id == sink_id:
                    break
                if current_id not in visited:
                    visited.add(current_id)
                    for edge in self.graph.get_edges_from_node(current_id):
                        stack.append(edge.end_node_id)
            else:
                raise NetworkNotValidError("Сток недостижим из источника")
            
            return True
            
        except NetworkNotValidError:
            return False
    
    def get_network_info(self) -> Dict:
        """Возвращает информацию о сети."""
        nodes = self.get_all_nodes()
        edges = self.get_all_edges()
        
        total_capacity = sum(edge.capacity for edge in edges)
        total_flow = sum(edge.flow for edge in edges)
        
        source = self.get_source_node()
        sink = self.get_sink_node()
        
        return {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "source": source.id,
            "sink": sink.id,
            "total_capacity": total_capacity,
            "total_flow": total_flow
        }