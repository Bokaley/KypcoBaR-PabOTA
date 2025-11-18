from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                              QLineEdit, QComboBox, QDoubleSpinBox, QCheckBox,
                              QDialogButtonBox, QLabel, QMessageBox)
from PySide6.QtCore import Qt, Signal

from src.flow_network import FlowNetwork
from src.exceptions import InvalidInputError, NodeNotFoundError

class AddNodeDialog(QDialog):
    """Диалог добавления нового узла."""
    
    # Сигналы на уровне класса
    node_added = Signal(str, str, bool, bool)  # id, name, is_source, is_sink
    
    def __init__(self, network: FlowNetwork, parent=None):
        super().__init__(parent)
        self.network = network
        self.setup_ui()
    
    def setup_ui(self):
        """Настраивает интерфейс диалога."""
        self.setWindowTitle("Добавить узел")
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout(self)
        
        # Форма
        form_layout = QFormLayout()
        
        self.id_edit = QLineEdit()
        self.id_edit.setPlaceholderText("Уникальный идентификатор")
        form_layout.addRow("ID:", self.id_edit)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Название узла")
        form_layout.addRow("Название:", self.name_edit)
        
        self.source_checkbox = QCheckBox("Источник")
        self.sink_checkbox = QCheckBox("Сток")
        
        # Группируем чекбоксы
        checkbox_layout = QHBoxLayout()
        checkbox_layout.addWidget(self.source_checkbox)
        checkbox_layout.addWidget(self.sink_checkbox)
        form_layout.addRow("Тип:", checkbox_layout)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def accept(self):
        """Обработка нажатия OK."""
        node_id = self.id_edit.text().strip()
        name = self.name_edit.text().strip() or node_id
        is_source = self.source_checkbox.isChecked()
        is_sink = self.sink_checkbox.isChecked()
        
        if not node_id:
            QMessageBox.warning(self, "Ошибка", "ID узла не может быть пустым")
            return
        
        try:
            # Проверяем, не существует ли уже узел с таким ID
            if any(node.id == node_id for node in self.network.get_all_nodes()):
                QMessageBox.warning(self, "Ошибка", f"Узел с ID '{node_id}' уже существует")
                return
            
            # Проверяем логику источника/стока
            if is_source and is_sink:
                QMessageBox.warning(self, "Ошибка", "Узел не может быть одновременно источником и стоком")
                return
            
            self.node_added.emit(node_id, name, is_source, is_sink)
            super().accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить узел: {str(e)}")

class EditNodeDialog(QDialog):
    """Диалог редактирования узла."""
    
    # Сигналы на уровне класса
    node_edited = Signal(str, str, bool, bool)  # id, new_name, new_is_source, new_is_sink
    
    def __init__(self, node_id: str, network: FlowNetwork, parent=None):
        super().__init__(parent)
        self.node_id = node_id
        self.network = network
        self.setup_ui()
        self.load_node_data()
        
    def setup_ui(self):
        """Настраивает интерфейс диалога."""
        self.setWindowTitle("Редактировать узел")
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout(self)
        
        # Форма
        form_layout = QFormLayout()
        
        self.id_label = QLabel(self.node_id)
        form_layout.addRow("ID:", self.id_label)
        
        self.name_edit = QLineEdit()
        form_layout.addRow("Название:", self.name_edit)
        
        self.source_checkbox = QCheckBox("Источник")
        self.sink_checkbox = QCheckBox("Сток")
        
        checkbox_layout = QHBoxLayout()
        checkbox_layout.addWidget(self.source_checkbox)
        checkbox_layout.addWidget(self.sink_checkbox)
        form_layout.addRow("Тип:", checkbox_layout)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def load_node_data(self):
        """Загружает данные узла в форму."""
        try:
            node = self.network.get_node(self.node_id)
            self.name_edit.setText(node.name)
            self.source_checkbox.setChecked(node.is_source)
            self.sink_checkbox.setChecked(node.is_sink)
        except NodeNotFoundError:
            QMessageBox.critical(self, "Ошибка", f"Узел '{self.node_id}' не найден")
            self.reject()
    
    def accept(self):
        """Обработка нажатия OK."""
        new_name = self.name_edit.text().strip() or self.node_id
        is_source = self.source_checkbox.isChecked()
        is_sink = self.sink_checkbox.isChecked()
        
        if is_source and is_sink:
            QMessageBox.warning(self, "Ошибка", "Узел не может быть одновременно источником и стоком")
            return
        
        self.node_edited.emit(self.node_id, new_name, is_source, is_sink)
        super().accept()

class AddEdgeDialog(QDialog):
    """Диалог добавления нового ребра."""
    
    # Сигналы на уровне класса
    edge_added = Signal(str, str, str, float)  # id, start_node_id, end_node_id, capacity
    
    def __init__(self, network: FlowNetwork, parent=None):
        super().__init__(parent)
        self.network = network
        self.setup_ui()
        self.populate_node_lists()
    
    def setup_ui(self):
        """Настраивает интерфейс диалога."""
        self.setWindowTitle("Добавить ребро")
        self.setMinimumWidth(350)
        
        layout = QVBoxLayout(self)
        
        # Форма
        form_layout = QFormLayout()
        
        self.id_edit = QLineEdit()
        self.id_edit.setPlaceholderText("Уникальный идентификатор")
        form_layout.addRow("ID ребра:", self.id_edit)
        
        self.start_node_combo = QComboBox()
        form_layout.addRow("Начальный узел:", self.start_node_combo)
        
        self.end_node_combo = QComboBox()
        form_layout.addRow("Конечный узел:", self.end_node_combo)
        
        self.capacity_spinbox = QDoubleSpinBox()
        self.capacity_spinbox.setRange(0.1, 1000.0)
        self.capacity_spinbox.setValue(1.0)
        self.capacity_spinbox.setDecimals(1)
        self.capacity_spinbox.setSuffix(" единиц")
        form_layout.addRow("Пропускная способность:", self.capacity_spinbox)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def populate_node_lists(self):
        """Заполняет списки узлов."""
        nodes = self.network.get_all_nodes()
        for node in nodes:
            self.start_node_combo.addItem(f"{node.name} ({node.id})", node.id)
            self.end_node_combo.addItem(f"{node.name} ({node.id})", node.id)
    
    def accept(self):
        """Обработка нажатия OK."""
        edge_id = self.id_edit.text().strip()
        start_node_data = self.start_node_combo.currentData()
        end_node_data = self.end_node_combo.currentData()
        capacity = self.capacity_spinbox.value()
        
        if not edge_id:
            QMessageBox.warning(self, "Ошибка", "ID ребра не может быть пустым")
            return
        
        if not start_node_data or not end_node_data:
            QMessageBox.warning(self, "Ошибка", "Необходимо выбрать начальный и конечный узлы")
            return
        
        if start_node_data == end_node_data:
            QMessageBox.warning(self, "Ошибка", "Начальный и конечный узел не могут совпадать")
            return
        
        # Проверяем, не существует ли уже ребро с таким ID
        try:
            self.network.get_edge(edge_id)
            QMessageBox.warning(self, "Ошибка", f"Ребро с ID '{edge_id}' уже существует")
            return
        except:
            pass  # Ребро не существует - это нормально
        
        self.edge_added.emit(edge_id, start_node_data, end_node_data, capacity)
        super().accept()

class EditEdgeDialog(QDialog):
    """Диалог редактирования ребра."""
    
    # Сигналы на уровне класса
    edge_edited = Signal(str, float)  # id, new_capacity
    
    def __init__(self, edge_id: str, network: FlowNetwork, parent=None):
        super().__init__(parent)
        self.edge_id = edge_id
        self.network = network
        self.setup_ui()
        self.load_edge_data()
    
    def setup_ui(self):
        """Настраивает интерфейс диалога."""
        self.setWindowTitle("Редактировать ребро")
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout(self)
        
        # Форма
        form_layout = QFormLayout()
        
        self.id_label = QLabel(self.edge_id)
        form_layout.addRow("ID ребра:", self.id_label)
        
        self.info_label = QLabel()
        form_layout.addRow("Информация:", self.info_label)
        
        self.capacity_spinbox = QDoubleSpinBox()
        self.capacity_spinbox.setRange(0.1, 1000.0)
        self.capacity_spinbox.setValue(1.0)
        self.capacity_spinbox.setDecimals(1)
        self.capacity_spinbox.setSuffix(" единиц")
        form_layout.addRow("Новая пропускная способность:", self.capacity_spinbox)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def load_edge_data(self):
        """Загружает данные ребра в форму."""
        try:
            edge = self.network.get_edge(self.edge_id)
            start_node = self.network.get_node(edge.start_node_id)
            end_node = self.network.get_node(edge.end_node_id)
            
            info_text = f"{start_node.name} → {end_node.name}\n"
            info_text += f"Текущий поток: {edge.flow:.1f}\n"
            info_text += f"Текущая пропускная способность: {edge.capacity:.1f}"
            
            self.info_label.setText(info_text)
            self.capacity_spinbox.setValue(edge.capacity)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные ребра: {str(e)}")
            self.reject()
    
    def accept(self):
        """Обработка нажатия OK."""
        new_capacity = self.capacity_spinbox.value()
        
        try:
            edge = self.network.get_edge(self.edge_id)
            if new_capacity < edge.flow:
                QMessageBox.warning(
                    self, 
                    "Ошибка", 
                    f"Новая пропускная способность ({new_capacity}) "
                    f"не может быть меньше текущего потока ({edge.flow})"
                )
                return
            
            self.edge_edited.emit(self.edge_id, new_capacity)
            super().accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить ребро: {str(e)}")

class FlowResultDialog(QDialog):
    """Диалог отображения результатов вычисления потока."""
    
    def __init__(self, max_flow: float, source_id: str, sink_id: str, 
                 min_cut_S: list, min_cut_T: list, parent=None):
        super().__init__(parent)
        self.max_flow = max_flow
        self.source_id = source_id
        self.sink_id = sink_id
        self.min_cut_S = min_cut_S
        self.min_cut_T = min_cut_T
        self.setup_ui()
    
    def setup_ui(self):
        """Настраивает интерфейс диалога."""
        self.setWindowTitle("Результаты вычисления максимального потока")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Основная информация
        main_info = QLabel(
            f"<h3>Максимальный поток: {self.max_flow:.2f}</h3>"
            f"<p>Источник: {self.source_id}<br>"
            f"Сток: {self.sink_id}</p>"
        )
        layout.addWidget(main_info)
        
        # Минимальный разрез
        cut_layout = QHBoxLayout()
        
        # Множество S
        s_widget = QVBoxLayout()
        s_label = QLabel("<b>Множество S (достижимые из источника):</b>")
        s_list = QLabel(", ".join(self.min_cut_S) if self.min_cut_S else "Пусто")
        s_widget.addWidget(s_label)
        s_widget.addWidget(s_list)
        
        # Множество T
        t_widget = QVBoxLayout()
        t_label = QLabel("<b>Множество T (недостижимые):</b>")
        t_list = QLabel(", ".join(self.min_cut_T) if self.min_cut_T else "Пусто")
        t_widget.addWidget(t_label)
        t_widget.addWidget(t_list)
        
        cut_layout.addLayout(s_widget)
        cut_layout.addLayout(t_widget)
        layout.addLayout(cut_layout)
        
        # Кнопка закрытия
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)