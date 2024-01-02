from flask import Blueprint

bp = Blueprint('errors', __name__)
from app.core import handlers  # nopep8 # noqa
