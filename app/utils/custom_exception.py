class CustomException(Exception):
    def __init__(self, status_code: int = 500, message: str = None, error_code: str = "ERROR", payload: str = None):
        self.status_code = status_code
        self.message = message
        self.error_code = error_code
        self.payload = payload
        super().__init__(self.message)
