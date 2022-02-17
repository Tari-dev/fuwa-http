class HTTPException(Exception):
    def __init__(self, resp, data):
        self.data = data
        self.status = resp.status
        self.message = data.get("message")

    def __str__(self) -> str:
        c_name = self.__class__.__name__
        fmt = "{0}: {1.status}: {1.message}"

        return fmt.format(c_name, self)

class NotFound(HTTPException):
    """Raised on 404
    """
    pass

class Forbidden(HTTPException):
    """Raised on 403
    """
    pass

class TooManyRequests(HTTPException):
    """Raised on 429
    """
    pass

class InternalServerError(HTTPException):
    """Raised on 500-504 codes
    """
    pass