class ValidationError(Exception):
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.message = message  # Store the message in an attribute
        self.status_code = status_code if status_code is not None else 400