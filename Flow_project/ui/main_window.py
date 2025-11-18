from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                              QToolBar, QStatusBar, QLabel, QPushButton,
                              QDockWidget, QMessageBox, QHBoxLayout)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt

from src.flow_network import FlowNetwork
from .graph_widget import GraphWidget

class MainWindow(QMainWindow):
    """Главное окно приложения."""
    
    def __init__(self):
        super().__init__()
        self.network = FlowNetwork()
        self.setup_ui()
        self.create_demo_network()
    
    def setup_ui(self):
        """Настраивает интерфейс главного окна."""
        self.setWindowTitle("Визуализатор максимального потока")
        self.setGeometry(100, 100, 1200, 800)
        
        self.setup_actions()
        self.setup_menus()
        self.setup_toolbar()
        self.setup_central_widget()
        self.setup_statusbar()
    
    def setup_actions(self):
        """Создает действия."""
        self.new_action = QAction("&Новый", self)
        self.new_action.triggered.connect(self.new_network)
        
        self.exit_action = QAction("&Выход", self)
        self.exit_action.triggered.connect(self.close)
    
    def setup_menus(self):
        """Настраивает меню."""
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("&Файл")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.exit_action)
    
    def setup_toolbar(self):
        """Настраивает панель инструментов."""
        toolbar = QToolBar("Основная панель")
        self.addToolBar(toolbar)
        
        # Добавляем кнопки в тулбар
        self.add_node_btn = QPushButton("Добавить узел")
        self.add_node_btn.clicked.connect(self.add_node)
        toolbar.addWidget(self.add_node_btn)
        
        self.add_edge_btn = QPushButton("Добавить ребро")
        self.add_edge_btn.clicked.connect(self.add_edge)
        toolbar.addWidget(self.add_edge_btn)
        
        self.calc_flow_btn = QPushButton("Вычислить поток")
        self.calc_flow_btn.clicked.connect(self.calculate_flow)
        toolbar.addWidget(self.calc_flow_btn)
        
        self.reset_btn = QPushButton("Сбросить")
        self.reset_btn.clicked.connect(self.reset_flows)
        toolbar.addWidget(self.reset_btn)
        
        self.center_btn = QPushButton("Центрировать")
        self.center_btn.clicked.connect(self.center_graph)
        toolbar.addWidget(self.center_btn)
    
    def setup_central_widget(self):
        """Настраивает центральный виджет."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Создаем виджет графа
        self.graph_widget = GraphWidget(self.network, self)
        
        layout.addWidget(self.graph_widget)
    
    def setup_statusbar(self):
        """Настраивает строку состояния."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.selection_label = QLabel("Готов")
        self.status_bar.addWidget(self.selection_label)
    
    def on_network_changed(self):
        """Обработчик изменения сети."""
        self.selection_label.setText("Сеть обновлена")
    
    def on_selection_changed(self, item_type: str, item_id: str):
        """Обработчик изменения выбора."""
        if item_type == "node":
            self.selection_label.setText(f"Выбран узел: {item_id}")
        elif item_type == "edge":
            self.selection_label.setText(f"Выбрано ребро: {item_id}")
        else:
            self.selection_label.setText("Готов")
    
    def add_node(self):
        """Добавляет узел."""
        self.graph_widget.show_add_node_dialog()
    
    def add_edge(self):
        """Добавляет ребро."""
        self.graph_widget.show_add_edge_dialog()
    
    def calculate_flow(self):
        """Вычисляет максимальный поток."""
        self.graph_widget.calculate_max_flow()
    
    def reset_flows(self):
        """Сбрасывает потоки."""
        self.graph_widget.reset_flows()
    
    def center_graph(self):
        """Центрирует граф."""
        self.graph_widget.center_on_graph()
    
    def new_network(self):
        """Создает новую сеть."""
        reply = QMessageBox.question(
            self,
            "Новая сеть",
            "Создать новую сеть? Все несохраненные данные будут потеряны.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.network = FlowNetwork()
            self.graph_widget.network = self.network
            self.graph_widget.clear_scene()
            self.selection_label.setText("Создана новая сеть")
    
    def create_demo_network(self):
        """Создает демонстрационную сеть."""
        try:
            # Добавляем узлы
            self.network.add_node("s", "Источник", is_source=True)
            self.network.add_node("1", "Узел 1")
            self.network.add_node("2", "Узел 2")
            self.network.add_node("3", "Узел 3")
            self.network.add_node("t", "Сток", is_sink=True)
            
            # Добавляем ребра
            self.network.add_edge("e1", "s", "1", 10.0)
            self.network.add_edge("e2", "s", "2", 5.0)
            self.network.add_edge("e3", "1", "2", 15.0)
            self.network.add_edge("e4", "1", "3", 10.0)
            self.network.add_edge("e5", "2", "3", 10.0)
            self.network.add_edge("e6", "2", "t", 10.0)
            self.network.add_edge("e7", "3", "t", 10.0)
            
            # Обновляем виджет
            self.graph_widget.populate_scene()
            self.selection_label.setText("Демо-сеть загружена")
            
        except Exception as e:
            print(f"Ошибка при создании демо-сети: {e}")