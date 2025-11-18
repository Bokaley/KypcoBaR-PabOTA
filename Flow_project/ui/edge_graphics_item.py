from PySide6.QtWidgets import QGraphicsItem, QGraphicsPathItem
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath, QFont
from PySide6.QtCore import Qt, QPointF
import math

from src.graph import Edge

class EdgeGraphicsItem(QGraphicsPathItem):
    """Графический элемент для отображения ребра в сцене."""
    
    # Константы
    ARROW_SIZE = 10
    HOVER_WIDTH = 6
    NORMAL_WIDTH = 3
    
    # Цвета
    DEFAULT_COLOR = QColor(96, 125, 139)      # Серо-синий
    FLOW_COLOR = QColor(0, 150, 136)          # Бирюзовый
    HOVER_COLOR = QColor(233, 30, 99)         # Розовый
    SELECTED_COLOR = QColor(255, 152, 0)      # Оранжевый
    TEXT_COLOR = QColor(0, 0, 0)              # Черный
    
    def __init__(self, edge: Edge, start_pos: QPointF, end_pos: QPointF, graph_widget=None):
        super().__init__()
        self.edge = edge
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.graph_widget = graph_widget  # Ссылка на родительский виджет
        self._is_hovered = False
        
        # Настройка элемента
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
        
        # Устанавливаем z-value ниже узлов
        self.setZValue(-1)
        
        self.update_path()
    
    def update_positions(self, start_pos: QPointF, end_pos: QPointF):
        """Обновляет позиции начала и конца ребра."""
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.update_path()
        self.update()
    
    def update_path(self):
        """Обновляет путь ребра с учетом стрелки."""
        path = QPainterPath()
        
        # Вычисляем вектор направления
        direction = self.end_pos - self.start_pos
        length = math.sqrt(direction.x()**2 + direction.y()**2)
        
        if length == 0:
            return
        
        # Нормализуем вектор
        unit_vector = QPointF(direction.x() / length, direction.y() / length)
        
        # Корректируем точки для избежания наложения на узлы
        start_adjusted = self.start_pos + unit_vector * 25
        end_adjusted = self.end_pos - unit_vector * 25
        
        # Рисуем линию
        path.moveTo(start_adjusted)
        path.lineTo(end_adjusted)
        
        # Рисуем стрелку
        arrow_tip = end_adjusted
        arrow_base = end_adjusted - unit_vector * self.ARROW_SIZE
        
        # Перпендикулярный вектор
        perp = QPointF(-unit_vector.y(), unit_vector.x())
        
        arrow_point1 = arrow_base + perp * (self.ARROW_SIZE / 2)
        arrow_point2 = arrow_base - perp * (self.ARROW_SIZE / 2)
        
        path.moveTo(arrow_tip)
        path.lineTo(arrow_point1)
        path.lineTo(arrow_point2)
        path.lineTo(arrow_tip)
        
        self.setPath(path)
    
    def paint(self, painter: QPainter, option, widget=None):
        """Отрисовывает ребро."""
        # Определяем цвет и толщину
        if self.isSelected():
            color = self.SELECTED_COLOR
            width = self.HOVER_WIDTH
        elif self._is_hovered:
            color = self.HOVER_COLOR
            width = self.HOVER_WIDTH
        else:
            # Интерполируем цвет в зависимости от загрузки ребра
            if self.edge.capacity > 0:
                ratio = self.edge.flow / self.edge.capacity
                color = self._interpolate_color(self.DEFAULT_COLOR, self.FLOW_COLOR, ratio)
            else:
                color = self.DEFAULT_COLOR
            width = self.NORMAL_WIDTH
        
        # Устанавливаем перо
        pen = QPen(color, width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(QBrush(color))
        
        # Рисуем путь
        painter.drawPath(self.path())
        
        # Рисуем текст с информацией о потоке
        self._draw_flow_text(painter)
    
    def _interpolate_color(self, color1: QColor, color2: QColor, ratio: float) -> QColor:
        """Интерполирует между двумя цветами."""
        r = int(color1.red() * (1 - ratio) + color2.red() * ratio)
        g = int(color1.green() * (1 - ratio) + color2.green() * ratio)
        b = int(color1.blue() * (1 - ratio) + color2.blue() * ratio)
        return QColor(r, g, b)
    
    def _draw_flow_text(self, painter: QPainter):
        """Рисует текст с информацией о потоке."""
        # Вычисляем середину ребра
        mid_point = (self.start_pos + self.end_pos) / 2
        
        # Смещаем текст перпендикулярно линии
        direction = self.end_pos - self.start_pos
        length = math.sqrt(direction.x()**2 + direction.y()**2)
        
        if length == 0:
            return
        
        unit_vector = QPointF(direction.x() / length, direction.y() / length)
        perp = QPointF(-unit_vector.y(), unit_vector.x())
        
        text_offset = perp * 20
        text_pos = mid_point + text_offset
        
        # Подготавливаем текст
        text = f"{self.edge.id}\n{self.edge.flow:.1f}/{self.edge.capacity:.1f}"
        
        # Устанавливаем шрифт
        font = QFont("Arial", 8)
        painter.setFont(font)
        painter.setPen(QPen(self.TEXT_COLOR))
        
        # Рисуем текст
        painter.drawText(text_pos, text)
    
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
                self.graph_widget.on_edge_selected(self.edge.id)
        elif event.button() == Qt.MouseButton.RightButton:
            scene_pos = self.mapToScene(event.pos())
            if self.graph_widget:
                self.graph_widget.on_edge_context_menu(self.edge.id, scene_pos)
        
        super().mousePressEvent(event)