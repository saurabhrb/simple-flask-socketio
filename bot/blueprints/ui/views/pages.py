import os

from flask import (
    Blueprint,
    current_app as app,
    redirect,
    request,
    url_for,
    render_template,
    send_from_directory
)

from bot.lib.util_str import is_empty


ui_bp = Blueprint('ui', __name__, url_prefix='/')
web_dir = 'static/app'


@ui_bp.route('/', defaults={'path': ''})
@ui_bp.route('/<path:path>')
def catch_all(path):
    if is_empty(path):
        path = "index.html"
    return send_from_directory(f'{web_dir}', path)
