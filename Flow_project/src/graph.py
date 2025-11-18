from dataclasses import dataclass
from typing import Dict, List, Optional
from .exceptions import InvalidInputError

@dataclass
class Node:
    """Класс узла графа."""
    id: str
    name: str
    is_source: bool = False
    is_sink: bool = False
    
    def __post_init__(self):
        if not self.id:
            raise InvalidInputError("ID узла не может быть пустым")
        if not self.name:
            self.name = self.id

@dataclass
class Edge:
    """Класс ребра графа."""
    id: str
    start_node_id: str
    end_node_id: str
    capacity: float
    flow: float = 0.0
    
    def __post_init__(self):
        if not self.id:
            raise InvalidInputError("ID ребра не может быть пустым")
        if self.capacity < 0:
            raise InvalidInputError("Пропускная способность не может быть отрицательной")
        if self.flow < 0:
            raise InvalidInputError("Поток не может быть отрицательным")
        if self.flow > self.capacity:
            raise InvalidInputError("Поток не может превышать пропускную способность")
    
    @property
    def residual_capacity(self) -> float:
        """Остаточная пропускная способность."""
        return self.capacity - self.flow

class Graph:
    """Класс для представления графа."""
    
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, Edge] = {}
        self.adjacency_list: Dict[str, List[str]] = {}  # Список смежности
    
    def add_node(self, node_id: str, name: str = "", is_source: bool = False, is_sink: bool = False) -> Node:
        """Добавляет узел в граф."""
        if node_id in self.nodes:
            raise InvalidInputError(f"Узел с ID '{node_id}' уже существует")
        
        node = Node(node_id, name or node_id, is_source, is_sink)
        self.nodes[node_id] = node
        self.adjacency_list[node_id] = []
        return node
    
    def get_node(self, node_id: str) -> Node:
        """Возвращает узел по ID."""
        if node_id not in self.nodes:
            raise NodeNotFoundError(node_id)
        return self.nodes[node_id]
    
    def remove_node(self, node_id: str):
        """Удаляет узел и все связанные с ним ребра."""
        if node_id not in self.nodes:
            raise NodeNotFoundError(node_id)
        
        # Удаляем все инцидентные ребра
        edges_to_remove = []
        for edge_id, edge in self.edges.items():
            if edge.start_node_id == node_id or edge.end_node_id == node_id:
                edges_to_remove.append(edge_id)
        
        for edge_id in edges_to_remove:
            self.remove_edge(edge_id)
        
        # Удаляем узел
        del self.nodes[node_id]
        del self.adjacency_list[node_id]
    
    def add_edge(self, edge_id: str, start_node_id: str, end_node_id: str, capacity: float) -> Edge:
        """Добавляет ребро в граф."""
        if edge_id in self.edges:
            raise InvalidInputError(f"Ребро с ID '{edge_id}' уже существует")
        
        # Проверяем существование узлов
        self.get_node(start_node_id)
        self.get_node(end_node_id)
        
        if start_node_id == end_node_id:
            raise InvalidInputError("Петли не поддерживаются")
        
        edge = Edge(edge_id, start_node_id, end_node_id, capacity)
        self.edges[edge_id] = edge
        self.adjacency_list[start_node_id].append(edge_id)
        
        return edge
    
    def get_edge(self, edge_id: str) -> Edge:
        """Возвращает ребро по ID."""
        if edge_id not in self.edges:
            raise EdgeNotFoundError(edge_id)
        return self.edges[edge_id]
    
    def remove_edge(self, edge_id: str):
        """Удаляет ребро из графа."""
        if edge_id not in self.edges:
            raise EdgeNotFoundError(edge_id)
        
        edge = self.edges[edge_id]
        # Удаляем из списка смежности
        if edge.start_node_id in self.adjacency_list:
            if edge_id in self.adjacency_list[edge.start_node_id]:
                self.adjacency_list[edge.start_node_id].remove(edge_id)
        
        del self.edges[edge_id]
    
    def get_edges_from_node(self, node_id: str) -> List[Edge]:
        """Возвращает все исходящие ребра из узла."""
        if node_id not in self.adjacency_list:
            return []
        
        edges = []
        for edge_id in self.adjacency_list[node_id]:
            edges.append(self.edges[edge_id])
        return edges
    
    def get_all_nodes(self) -> List[Node]:
        """Возвращает все узлы графа."""
        return list(self.nodes.values())
    
    def get_all_edges(self) -> List[Edge]:
        """Возвращает все ребра графа."""
        return list(self.edges.values())
    
    def has_edge(self, start_node_id: str, end_node_id: str) -> bool:
        """Проверяет существование ребра между узлами."""
        if start_node_id not in self.adjacency_list:
            return False
        
        for edge_id in self.adjacency_list[start_node_id]:
            edge = self.edges[edge_id]
            if edge.end_node_id == end_node_id:
                return True
        return False
    
    def get_source_nodes(self) -> List[Node]:
        """Возвращает все источники."""
        return [node for node in self.nodes.values() if node.is_source]
    
    def get_sink_nodes(self) -> List[Node]:
        """Возвращает все стоки."""
        return [node for node in self.nodes.values() if node.is_sink]