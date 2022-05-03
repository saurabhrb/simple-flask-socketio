from functools import wraps

from flask import request

from bot.lib import httperrors


def request_get_args_req(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        errtitle = "Arguments missing"
        errdesc = "No arguments are provided with the request"
        try:
            request_dict = request.args
        except Exception as e:
            raise httperrors.BadRequestError(title=errtitle, business_errors=[errdesc])

        if request_dict is None:
            raise httperrors.BadRequestError(title=errtitle, business_errors=[errdesc])

        return f(request_dict, *args, **kwargs)

    return wrap


def request_get_args_opt(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        request_dict = None
        try:
            request_dict = request.args
        except Exception as e:
            pass

        if request_dict is None:
            request_dict = dict()

        return f(request_dict, *args, **kwargs)

    return wrap


def request_post_json_req(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        errtitle = "JSON input required"
        errdesc = "No json data provided with the request"
        try:
            request_json = request.json
        except Exception as e:
            raise httperrors.BadRequestError(title=errtitle, business_errors=[errdesc])

        if request_json is None:
            raise httperrors.BadRequestError(title=errtitle, business_errors=[errdesc])

        return f(request_json, *args, **kwargs)

    return wrap
