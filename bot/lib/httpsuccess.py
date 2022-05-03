from flask import jsonify, make_response


#######################
# For JSON Responses  #
#######################
# Success handler
def success_response(success):
    """
     Common Json response
    {
        code: num (http code),
        name: str (http name),
        desc: str (http description),

        title: str (Short text describing the result),
        msg: str (Detailed text describing the result),
        data: json (The data to be returned)
    }
    """

    return make_response(jsonify({
        'code': success.code, 'name': success.name, 'desc': success.description,
        'title': success.title, 'msg': success.msg, 'data': success.data
    }), success.code), success.code


############################
# HTTP Success             #
############################
"""
HTTP_STATUS_CODES = {
    100: "Continue",
    101: "Switching Protocols",
    102: "Processing",
    103: "Early Hints",  # see RFC 8297
    200: "OK",
    201: "Created",
    202: "Accepted",
    203: "Non Authoritative Information",
    204: "No Content",
    205: "Reset Content",
    206: "Partial Content",
    207: "Multi Status",
    208: "Already Reported",  # see RFC 5842
    226: "IM Used",  # see RFC 3229
    300: "Multiple Choices",
    301: "Moved Permanently",
    302: "Found",
    303: "See Other",
    304: "Not Modified",
    305: "Use Proxy",
    306: "Switch Proxy",  # unused
    307: "Temporary Redirect",
    308: "Permanent Redirect",
}
"""


class BaseHTTPSuccess:
    """Not to be raised directly; raise sub-class instances instead"""
    code = None
    name = None
    description = None

    title = None
    msg = None
    data = None

    def __init__(self, title, msg, data=None):
        self.title = title
        self.msg = msg
        self.data = data


class Ok(BaseHTTPSuccess):
    code = 200
    name = 'Ok'
    title = "Request succeeded"
    description = "The request has succeeded"


class Created(BaseHTTPSuccess):
    code = 201
    name = 'Created'
    title = "Request succeeded and resource created"
    description = "The request has succeeded and a new resource has been created as a result. "


class Accepted(BaseHTTPSuccess):
    code = 202
    name = 'Request accepted'
    description = "The request has been received but not yet acted upon."
