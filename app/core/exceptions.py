class AppException(Exception):
    status_code = 500
    detail = "Internal server error"

    def __init__(self, detail: str | None = None):
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)


class NotFoundError(AppException):
    status_code = 404
    detail = "Resource not found"


class ConflictError(AppException):
    status_code = 409
    detail = "Resource error"
