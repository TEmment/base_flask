from flask import Blueprint

bp = Blueprint('auth', __name__)
from app.core import routes  # nopep8 # noqa
