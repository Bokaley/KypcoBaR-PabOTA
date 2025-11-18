from PySide6.QtWidgets import QGraphicsItem, QGraphicsTextItem
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont
from PySide6.QtCore import Qt, QPointF, QRectF

from src.graph import Node

class NodeGraphicsItem(QGraphicsItem):
    """Графический элемент для отображения узла в сцене."""
    
    # Константы
    NODE_RADIUS = 25
    HOVER_RADIUS = 28
    BORDER_WIDTH = 2
    
    # Цвета
    SOURCE_COLOR = QColor(76, 175, 80)    # Зеленый
    SINK_COLOR = QColor(244, 67, 54)      # Красный
    DEFAULT_COLOR = QColor(33, 150, 243)  # Синий
    SELECTED_COLOR = QColor(255, 193, 7)  # Желтый
    HOVER_COLOR = QColor(156, 39, 176)    # Фиолетовый
    BORDER_COLOR = QColor(0, 0, 0)        # Черный
    TEXT_COLOR = QColor(255, 255, 255)    # Белый
    
    def __init__(self, node: Node, graph_widget=None):
        super().__init__()
        self.node = node
        self.graph_widget = graph_widget  # Ссылка на родительский виджет
        self._is_hovered = False
        
        # Настройка элемента
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)
        
        # Создаем текстовый элемент для ID
        self.text_item = QGraphicsTextItem(str(node.id), self)
        self.text_item.setDefaultTextColor(self.TEXT_COLOR)
        font = QFont("Arial", 8, QFont.Weight.Bold)
        self.text_item.setFont(font)
        
        # Центрируем текст
        text_rect = self.text_item.boundingRect()
        self.text_item.setPos(-text_rect.width() / 2, -text_rect.height() / 2)
    
    def boundingRect(self) -> QRectF:
        """Возвращает ограничивающий прямоугольник."""
        radius = self.HOVER_RADIUS if self._is_hovered else self.NODE_RADIUS
        return QRectF(-radius, -radius, 2 * radius, 2 * radius)
    
    def paint(self, painter: QPainter, option, widget=None):
        """Отрисовывает узел."""
        # Определяем основной цвет
        if self.node.is_source:
            base_color = self.SOURCE_COLOR
        elif self.node.is_sink:
            base_color = self.SINK_COLOR
        else:
            base_color = self.DEFAULT_COLOR
        
        # Корректируем цвет в зависимости от состояния
        if self.isSelected():
            fill_color = self.SELECTED_COLOR
        elif self._is_hovered:
            fill_color = self.HOVER_COLOR
        else:
            fill_color = base_color
        
        # Определяем радиус
        radius = self.HOVER_RADIUS if self._is_hovered else self.NODE_RADIUS
        
        # Рисуем заливку
        painter.setBrush(QBrush(fill_color))
        painter.setPen(QPen(self.BORDER_COLOR, self.BORDER_WIDTH))
        painter.drawEllipse(-radius, -radius, 2 * radius, 2 * radius)
        
        # Если узел источник или сток, добавляем дополнительную обводку
        if self.node.is_source or self.node.is_sink:
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(self.BORDER_COLOR, self.BORDER_WIDTH * 2))
            painter.drawEllipse(-radius - 2, -radius - 2, 2 * radius + 4, 2 * radius + 4)
    
    def hoverEnterEvent(self, event):
        """Обработка входа курсора."""
        self._is_hovered = True
        self.update()
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        """Обработка выхода курсора."""
        self._is_hovered = False
        self.update()
        super().hoverLeaveEvent(event)
    
    def mousePressEvent(self, event):
        """Обработка нажатия мыши."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Прямой вызов вместо сигнала
            if self.graph_widget:
                self.graph_widget.on_node_selected(self.node.id)
        elif event.button() == Qt.MouseButton.RightButton:
            scene_pos = self.mapToScene(event.pos())
            if self.graph_widget:
                self.graph_widget.on_node_context_menu(self.node.id, scene_pos)
        
        super().mousePressEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """Обработка двойного клика."""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.graph_widget:
                self.graph_widget.on_node_double_clicked(self.node.id)
        super().mouseDoubleClickEvent(event)
    
    def itemChange(self, change, value):
        """Обработка изменений элемента."""
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            if self.scene():
                self.scene().update()
        return super().itemChange(change, value)
    
    def update_appearance(self):
        """Обновляет внешний вид узла."""
        self.update()