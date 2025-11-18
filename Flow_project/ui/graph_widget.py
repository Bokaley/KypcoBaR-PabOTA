from PySide6.QtWidgets import (QGraphicsView, QGraphicsScene, QMenu, 
                              QMessageBox, QInputDialog)
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QAction
from PySide6.QtCore import Qt, QPointF
import random

from src.flow_network import FlowNetwork
from src.exceptions import NodeNotFoundError, EdgeNotFoundError, InvalidInputError
from .node_graphics_item import NodeGraphicsItem
from .edge_graphics_item import EdgeGraphicsItem

class GraphWidget(QGraphicsView):
    """Виджет для отображения и взаимодействия с графом."""
    
    def __init__(self, network: FlowNetwork = None, parent=None):
        super().__init__(parent)
        self.network = network or FlowNetwork()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Словари для хранения графических элементов
        self.node_items = {}  # node_id -> NodeGraphicsItem
        self.edge_items = {}  # edge_id -> EdgeGraphicsItem
        
        self.setup_ui()
        self.setup_context_menus()
        
        # Если сеть уже содержит данные, отображаем их
        if self.network.get_all_nodes():
            self.populate_scene()
    
    def setup_ui(self):
        """Настраивает виджет."""
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Устанавливаем контекстное меню
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_scene_context_menu)
    
    def setup_context_menus(self):
        """Настраивает контекстные меню."""
        # Контекстное меню для сцены
        self.scene_context_menu = QMenu(self)
        
        self.add_node_action = QAction("Добавить узел", self)
        self.add_node_action.triggered.connect(self.show_add_node_dialog)
        self.scene_context_menu.addAction(self.add_node_action)
        
        self.add_edge_action = QAction("Добавить ребро", self)
        self.add_edge_action.triggered.connect(self.show_add_edge_dialog)
        self.scene_context_menu.addAction(self.add_edge_action)
        
        self.scene_context_menu.addSeparator()
        
        self.calculate_flow_action = QAction("Вычислить максимальный поток", self)
        self.calculate_flow_action.triggered.connect(self.calculate_max_flow)
        self.scene_context_menu.addAction(self.calculate_flow_action)
        
        self.reset_flows_action = QAction("Сбросить потоки", self)
        self.reset_flows_action.triggered.connect(self.reset_flows)
        self.scene_context_menu.addAction(self.reset_flows_action)
        
        self.scene_context_menu.addSeparator()
        
        self.center_action = QAction("Центрировать граф", self)
        self.center_action.triggered.connect(self.center_on_graph)
        self.scene_context_menu.addAction(self.center_action)
        
        # Контекстное меню для узла
        self.node_context_menu = QMenu(self)
        
        self.edit_node_action = QAction("Редактировать узел", self)
        self.edit_node_action.triggered.connect(self.edit_selected_node)
        self.node_context_menu.addAction(self.edit_node_action)
        
        self.remove_node_action = QAction("Удалить узел", self)
        self.remove_node_action.triggered.connect(self.remove_selected_node)
        self.node_context_menu.addAction(self.remove_node_action)
        
        self.node_context_menu.addSeparator()
        
        self.set_source_action = QAction("Сделать источником", self)
        self.set_source_action.triggered.connect(lambda: self.set_node_type('source'))
        self.node_context_menu.addAction(self.set_source_action)
        
        self.set_sink_action = QAction("Сделать стоком", self)
        self.set_sink_action.triggered.connect(lambda: self.set_node_type('sink'))
        self.node_context_menu.addAction(self.set_sink_action)
        
        self.node_context_menu.addSeparator()
        
        self.add_edge_from_action = QAction("Добавить ребро из этого узла", self)
        self.add_edge_from_action.triggered.connect(self.add_edge_from_selected_node)
        self.node_context_menu.addAction(self.add_edge_from_action)
        
        # Контекстное меню для ребра
        self.edge_context_menu = QMenu(self)
        
        self.edit_edge_action = QAction("Редактировать ребро", self)
        self.edit_edge_action.triggered.connect(self.edit_selected_edge)
        self.edge_context_menu.addAction(self.edit_edge_action)
        
        self.remove_edge_action = QAction("Удалить ребро", self)
        self.remove_edge_action.triggered.connect(self.remove_selected_edge)
        self.edge_context_menu.addAction(self.remove_edge_action)
    
    def populate_scene(self):
        """Заполняет сцену элементами из сети."""
        self.clear_scene()
        
        # Создаем узлы
        nodes = self.network.get_all_nodes()
        for node in nodes:
            self.add_node_item(node)
        
        # Создаем ребра
        edges = self.network.get_all_edges()
        for edge in edges:
            self.add_edge_item(edge)
        
        self.center_on_graph()
    
    def clear_scene(self):
        """Очищает сцену."""
        self.node_items.clear()
        self.edge_items.clear()
        self.scene.clear()
    
    def add_node_item(self, node):
        """Добавляет графический элемент узла на сцену."""
        if node.id in self.node_items:
            return self.node_items[node.id]
        
        # Случайная позиция для нового узла
        pos = QPointF(
            random.uniform(-200, 200),
            random.uniform(-200, 200)
        )
        
        # Передаем self как graph_widget для прямых вызовов
        item = NodeGraphicsItem(node, self)
        
        # Сначала добавляем в сцену
        self.scene.addItem(item)
        # Потом устанавливаем позицию
        item.setPos(pos)
        
        self.node_items[node.id] = item
        return item
    
    def add_edge_item(self, edge):
        """Добавляет графический элемент ребра на сцену."""
        if edge.id in self.edge_items:
            return self.edge_items[edge.id]
        
        # Получаем позиции узлов
        start_item = self.node_items.get(edge.start_node_id)
        end_item = self.node_items.get(edge.end_node_id)
        
        if not start_item or not end_item:
            return None
        
        start_pos = start_item.pos()
        end_pos = end_item.pos()
        
        # Передаем self как graph_widget для прямых вызовов
        item = EdgeGraphicsItem(edge, start_pos, end_pos, self)
        
        self.scene.addItem(item)
        self.edge_items[edge.id] = item
        return item
    
    def center_on_graph(self):
        """Центрирует вид на графе."""
        if self.scene.items():
            self.scene.setSceneRect(self.scene.itemsBoundingRect())
            self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
    
    # Методы-обработчики (вместо слотов)
    def on_node_selected(self, node_id):
        """Обработчик выбора узла."""
        print(f"Узел выбран: {node_id}")
        if hasattr(self.parent(), 'on_selection_changed'):
            self.parent().on_selection_changed("node", node_id)
    
    def on_node_double_clicked(self, node_id):
        """Обработчик двойного клика по узлу."""
        self.show_edit_node_dialog(node_id)
    
    def on_node_context_menu(self, node_id, scene_pos):
        """Обработчик контекстного меню узла."""
        self.selected_node_id = node_id
        view_pos = self.mapFromScene(scene_pos)
        self.node_context_menu.exec(self.mapToGlobal(view_pos))
    
    def on_edge_selected(self, edge_id):
        """Обработчик выбора ребра."""
        print(f"Ребро выбрано: {edge_id}")
        if hasattr(self.parent(), 'on_selection_changed'):
            self.parent().on_selection_changed("edge", edge_id)
    
    def on_edge_context_menu(self, edge_id, scene_pos):
        """Обработчик контекстного меню ребра."""
        self.selected_edge_id = edge_id
        view_pos = self.mapFromScene(scene_pos)
        self.edge_context_menu.exec(self.mapToGlobal(view_pos))
    
    def show_scene_context_menu(self, pos):
        """Показывает контекстное меню сцены."""
        self.scene_context_menu.exec(self.mapToGlobal(pos))
    
    # Методы для работы с узлами и ребрами
    def show_add_node_dialog(self):
        """Показывает диалог добавления узла."""
        node_id, ok = QInputDialog.getText(self, "Добавить узел", "Введите ID узла:")
        if ok and node_id:
            try:
                node = self.network.add_node(node_id, node_id)
                self.add_node_item(node)
                if hasattr(self.parent(), 'on_network_changed'):
                    self.parent().on_network_changed()
            except InvalidInputError as e:
                QMessageBox.warning(self, "Ошибка", str(e))
    
    def show_add_edge_dialog(self):
        """Показывает диалог добавления ребра."""
        # Упрощенная версия - запрашиваем данные через диалоги
        start_node_id, ok1 = QInputDialog.getText(self, "Добавить ребро", "ID начального узла:")
        if not ok1 or not start_node_id:
            return
            
        end_node_id, ok2 = QInputDialog.getText(self, "Добавить ребро", "ID конечного узла:")
        if not ok2 or not end_node_id:
            return
            
        # Исправленный вызов getDouble для PySide6
        capacity, ok3 = QInputDialog.getDouble(
            self, 
            "Добавить ребро", 
            "Пропускная способность:", 
            value=1.0, 
            decimals=1
        )
        if not ok3:
            return
            
        edge_id = f"{start_node_id}_{end_node_id}"
        
        try:
            edge = self.network.add_edge(edge_id, start_node_id, end_node_id, capacity)
            self.add_edge_item(edge)
            if hasattr(self.parent(), 'on_network_changed'):
                self.parent().on_network_changed()
        except (NodeNotFoundError, InvalidInputError) as e:
            QMessageBox.warning(self, "Ошибка", str(e))
    
    def show_edit_node_dialog(self, node_id: str):
        """Показывает диалог редактирования узла."""
        try:
            node = self.network.get_node(node_id)
            new_name, ok = QInputDialog.getText(self, "Редактировать узел", "Новое название:", text=node.name)
            if ok and new_name:
                node.name = new_name
                if node_id in self.node_items:
                    self.node_items[node_id].update_appearance()
        except NodeNotFoundError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
    
    def calculate_max_flow(self):
        """Вычисляет максимальный поток."""
        try:
            if not self.network.validate_network():
                QMessageBox.warning(self, "Ошибка", "Сеть невалидна. Убедитесь, что есть источник и сток.")
                return
            
            max_flow, min_cut_S, min_cut_T = self.network.calculate_max_flow()
            
            # Обновляем отображение ребер
            for edge_item in self.edge_items.values():
                edge_item.update()
            
            QMessageBox.information(
                self, 
                "Результат", 
                f"Максимальный поток: {max_flow}\n"
                f"Минимальный разрез:\n"
                f"S (достижимые): {', '.join(min_cut_S)}\n"
                f"T (недостижимые): {', '.join(min_cut_T)}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось вычислить поток: {str(e)}")
    
    def reset_flows(self):
        """Сбрасывает все потоки к нулю."""
        self.network.reset_flows()
        
        # Обновляем графические элементы
        for edge_item in self.edge_items.values():
            edge_item.update()
        
        QMessageBox.information(self, "Сброс", "Все потоки сброшены к нулю")
    
    def edit_selected_node(self):
        """Редактирует выбранный узел."""
        if hasattr(self, 'selected_node_id'):
            self.show_edit_node_dialog(self.selected_node_id)
    
    def remove_selected_node(self):
        """Удаляет выбранный узел."""
        if hasattr(self, 'selected_node_id'):
            node_id = self.selected_node_id
            reply = QMessageBox.question(
                self, 
                "Подтверждение удаления", 
                f"Удалить узел '{node_id}' и все связанные ребра?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    self.network.remove_node(node_id)
                    if node_id in self.node_items:
                        item = self.node_items.pop(node_id)
                        self.scene.removeItem(item)
                    
                    # Удаляем связанные ребра
                    edges_to_remove = []
                    for edge_id, edge_item in self.edge_items.items():
                        if (edge_item.edge.start_node_id == node_id or 
                            edge_item.edge.end_node_id == node_id):
                            edges_to_remove.append(edge_id)
                    
                    for edge_id in edges_to_remove:
                        item = self.edge_items.pop(edge_id)
                        self.scene.removeItem(item)
                    
                    if hasattr(self.parent(), 'on_network_changed'):
                        self.parent().on_network_changed()
                        
                except NodeNotFoundError as e:
                    QMessageBox.warning(self, "Ошибка", str(e))
    
    def set_node_type(self, node_type: str):
        """Устанавливает тип узла (источник/сток)."""
        if not hasattr(self, 'selected_node_id'):
            return
        
        node_id = self.selected_node_id
        
        try:
            if node_type == 'source':
                self.network.set_node_as_source(node_id)
            elif node_type == 'sink':
                self.network.set_node_as_sink(node_id)
            
            # Обновляем графический элемент
            if node_id in self.node_items:
                self.node_items[node_id].update_appearance()
            
            if hasattr(self.parent(), 'on_network_changed'):
                self.parent().on_network_changed()
            
        except (NodeNotFoundError, InvalidInputError) as e:
            QMessageBox.warning(self, "Ошибка", str(e))
    
    def add_edge_from_selected_node(self):
        """Добавляет ребро из выбранного узла."""
        if not hasattr(self, 'selected_node_id'):
            return
        
        start_node_id = self.selected_node_id
        
        end_node_id, ok1 = QInputDialog.getText(self, "Добавить ребро", "ID конечного узла:")
        if not ok1 or not end_node_id:
            return
            
        # Исправленный вызов getDouble для PySide6
        capacity, ok2 = QInputDialog.getDouble(
            self, 
            "Добавить ребро", 
            "Пропускная способность:", 
            value=1.0, 
            decimals=1
        )
        if not ok2:
            return
            
        edge_id = f"{start_node_id}_{end_node_id}"
        
        try:
            edge = self.network.add_edge(edge_id, start_node_id, end_node_id, capacity)
            self.add_edge_item(edge)
            if hasattr(self.parent(), 'on_network_changed'):
                self.parent().on_network_changed()
        except (NodeNotFoundError, InvalidInputError) as e:
            QMessageBox.warning(self, "Ошибка", str(e))
    
    def edit_selected_edge(self):
        """Редактирует выбранное ребро."""
        if hasattr(self, 'selected_edge_id'):
            edge_id = self.selected_edge_id
            try:
                edge = self.network.get_edge(edge_id)
                # Исправленный вызов getDouble для PySide6
                new_capacity, ok = QInputDialog.getDouble(
                    self, 
                    "Редактировать ребро", 
                    "Новая пропускная способность:", 
                    value=edge.capacity, 
                    decimals=1
                )
                if ok:
                    self.network.update_edge_capacity(edge_id, new_capacity)
                    if edge_id in self.edge_items:
                        self.edge_items[edge_id].update()
                    if hasattr(self.parent(), 'on_network_changed'):
                        self.parent().on_network_changed()
            except (EdgeNotFoundError, InvalidInputError) as e:
                QMessageBox.warning(self, "Ошибка", str(e))
    
    def remove_selected_edge(self):
        """Удаляет выбранное ребро."""
        if hasattr(self, 'selected_edge_id'):
            edge_id = self.selected_edge_id
            reply = QMessageBox.question(
                self, 
                "Подтверждение удаления", 
                f"Удалить ребро '{edge_id}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    self.network.remove_edge(edge_id)
                    if edge_id in self.edge_items:
                        item = self.edge_items.pop(edge_id)
                        self.scene.removeItem(item)
                    if hasattr(self.parent(), 'on_network_changed'):
                        self.parent().on_network_changed()
                except EdgeNotFoundError as e:
                    QMessageBox.warning(self, "Ошибка", str(e))