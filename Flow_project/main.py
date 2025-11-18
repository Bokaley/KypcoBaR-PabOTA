#!/usr/bin/env python3
"""
Главный файл приложения для визуализации максимального потока.
"""

import sys
import os

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'ui'))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from PySide6.QtCore import QTimer

from ui.main_window import MainWindow

def main():
    """Главная функция приложения."""
    # Создаем приложение
    app = QApplication(sys.argv)
    
    # Настраиваем шрифт по умолчанию для лучшей читаемости
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Создаем и показываем главное окно
    window = MainWindow()
    window.show()
    
    # Запускаем event loop
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())