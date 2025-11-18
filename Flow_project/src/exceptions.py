class FlowNetworkError(Exception):
    """Базовое исключение для ошибок в сети потока."""
    pass

class NodeNotFoundError(FlowNetworkError):
    """Исключение при отсутствии узла."""
    def __init__(self, node_id):
        super().__init__(f"Узел '{node_id}' не найден")

class EdgeNotFoundError(FlowNetworkError):
    """Исключение при отсутствии ребра."""
    def __init__(self, edge_id):
        super().__init__(f"Ребро '{edge_id}' не найдено")

class InvalidInputError(FlowNetworkError):
    """Исключение при неверных входных данных."""
    def __init__(self, message):
        super().__init__(message)

class NetworkNotValidError(FlowNetworkError):
    """Исключение при невалидной структуре сети."""
    def __init__(self, message):
        super().__init__(message)