from flask import jsonify, make_response
import werkzeug.exceptions as werk_excep

from bot.lib.util_sys import get_exception_traceback


#######################
# For JSON Responses  #
#######################
# Error handler
def common_error_response(code, name, description, title, field_errors, business_errors):
    """
    Common Json response
    {
        errcode: num (http error code),
        errname: str (http error name),
        errdesc: str (http error description),

        errtitle: str (Short text describing the error),
        errors = { # Contains errors thrown by the tradingbot
            'fields': {
                'field_1_name': [list of errors with respect to field1],
                'field_2_name: [list of errors with respect to fields2],
                .....
            },

            'business': [list of business errors]
        }
    }

    """

    errors = None
    if field_errors is not None or business_errors is not None:
        errors = dict()
    if field_errors is not None:
        errors.update({'fields': field_errors})
    if business_errors is not None:
        errors.update({'business': business_errors})

    return make_response(
        jsonify({
            'errcode': code, 'errname': name, 'errdesc': description,
            'errtitle': title,  'errors': errors}
        ), code), code


def error_response(error):
    """
    HTTP Exceptions purposefully raised by the application
    """

    return common_error_response(
        code=error.code,
        name=error.name,
        description=error.description,

        title=error.title,
        field_errors=error.field_errors,
        business_errors=error.business_errors
    )


def flask_error_response(error):
    """
    HTTP exceptions raised by flask
    """
    return common_error_response(
        code=error.code,
        name=error.name,
        description=error.description,

        title=error.name,
        field_errors=None,
        business_errors=None,
    )


def uncaught_exception(exception, debug):
    """
    Non-HTTP exceptions raised by python
    Mask it as a server error
    """
    x = None
    # if debug:
    #     x = ServerError(
    #         title="Unexpected Error (DEBUG): " + exception.__class__.__name__,
    #         business_errors=[get_exception_traceback(exception)]
    #     )
    # else:
    #     x = ServerError(title="Unexpected Error")

    x = ServerError(
        title="Unexpected Error (DEBUG): " + exception.__class__.__name__,
        business_errors=[get_exception_traceback(exception)]
    )

    return common_error_response(
        code=x.code,
        name=x.name,
        description=x.description,
        title=x.title,
        field_errors=x.field_errors,
        business_errors=x.business_errors
    )


###########################
# HTTP Exceptions         #
###########################
"""
HTTP_STATUS_CODES = {
    # Flask lib standards
    400: "Bad Request",
    401: "Unauthorized",
    402: "Payment Required",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Acceptable",
    407: "Proxy Authentication Required",
    408: "Request Timeout",
    409: "Conflict",
    410: "Gone",
    411: "Length Required",
    412: "Precondition Failed",
    413: "Request Entity Too Large",
    414: "Request URI Too Long",
    415: "Unsupported Media Type",
    416: "Requested Range Not Satisfiable",
    417: "Expectation Failed",
    418: "I'm a teapot",  # see RFC 2324
    421: "Misdirected Request",  # see RFC 7540
    422: "Unprocessable Entity",
    423: "Locked",
    424: "Failed Dependency",
    425: "Too Early",  # see RFC 8470
    426: "Upgrade Required",
    428: "Precondition Required",  # see RFC 6585
    429: "Too Many Requests",
    431: "Request Header Fields Too Large",
    449: "Retry With",  # proprietary MS extension
    451: "Unavailable For Legal Reasons",
    500: "Internal Server Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
    505: "HTTP Version Not Supported",
    506: "Variant Also Negotiates",  # see RFC 2295
    507: "Insufficient Storage",
    508: "Loop Detected",  # see RFC 5842
    510: "Not Extended",
    511: "Network Authentication Failed",  # see RFC 6585
    
    # Custom
    440: "Session expired",
    460: "Payment failed",
    461: "Payment in progress',
    480: "Resource not found",  # The requested resource (object not url) doesn't exist
    520: "Payment Gateway error",
}
"""


class BaseHTTPError(werk_excep.HTTPException):
    """
       This class just help determining whether the http exception raised is custom created by me and not the default one
       that flask provides.

       Every exception (either custom made by me or default flask http exceptions) will have the following fields
       - code (int)
       - name (str)
       - description. (str)
       Custom created http exceptions may choose to override this property

       Apart from the above fields custom created exceptions will also have the following fields:
       - title (str)
       - field_errors (json)
       - business_errors (json)
       """

    title = None
    field_errors = None
    business_errors = None

    def __init__(self, title, field_errors=None, business_errors=None):
        self.title = title
        self.field_errors = field_errors
        self.business_errors = business_errors


# FLASK STANDARD HTTP ERRORS
class BadRequestError(werk_excep.BadRequest, BaseHTTPError):
    def __init__(self, *args, **kwargs):
        BaseHTTPError.__init__(self, *args, **kwargs)


class UnauthorizedError(werk_excep.Unauthorized, BaseHTTPError):
    def __init__(self, *args, **kwargs):
        BaseHTTPError.__init__(self, *args, **kwargs)


class ForbiddenError(werk_excep.Forbidden, BaseHTTPError):
    def __init__(self, *args, **kwargs):
        BaseHTTPError.__init__(self, *args, **kwargs)


class NotFoundError(werk_excep.Forbidden, BaseHTTPError):
    def __init__(self, *args, **kwargs):
        BaseHTTPError.__init__(self, *args, **kwargs)


class GoneError(werk_excep.Gone, BaseHTTPError):
    def __init__(self, *args, **kwargs):
        BaseHTTPError.__init__(self, *args, **kwargs)


class ServerError(werk_excep.InternalServerError, BaseHTTPError):
    def __init__(self, *args, **kwargs):
        BaseHTTPError.__init__(self, *args, **kwargs)


# CUSTOM HTTP ERRORS
class SessionTimedOutError(BaseHTTPError):
    code = 440
    description = "Your session has expired. Log in again."

    def __init__(self, *args, **kwargs):
        BaseHTTPError.__init__(self, *args, **kwargs)

    @property
    def name(self):
        """The status name."""
        return "Session expired"


class PaymentFailedError(BaseHTTPError):
    code = 460
    description = "Payment failed. Please try again"

    def __init__(self, *args, **kwargs):
        BaseHTTPError.__init__(self, *args, **kwargs)

    @property
    def name(self):
        """The status name."""
        return "Payment failed"


class PaymentProgressError(BaseHTTPError):
    code = 461
    description = "Payment in progress. Please try again"

    def __init__(self, *args, **kwargs):
        BaseHTTPError.__init__(self, *args, **kwargs)

    @property
    def name(self):
        """The status name."""
        return "Payment in progress"


class ResourceNotFoundError(BaseHTTPError):
    code = 480
    description = "The requested resource doesn't exist"

    def __init__(self, *args, **kwargs):
        BaseHTTPError.__init__(self, *args, **kwargs)

    @property
    def name(self):
        """The status name."""
        return "Resource not found"


class PaymentGatewayError(BaseHTTPError):
    code = 480
    description = "Some error occurred while communicating with the payment gateway"

    def __init__(self, *args, **kwargs):
        BaseHTTPError.__init__(self, *args, **kwargs)

    @property
    def name(self):
        """The status name."""
        return "Payment Gateway error"


if __name__ == '__main__':
    a = SessionTimedOutError(title="An error", field_errors=[], business_errors=[])
    print(a.code)
    print(a.name)
    print(a.description)
    print(a.title)
    print(a.field_errors)
    print(a.business_errors)

