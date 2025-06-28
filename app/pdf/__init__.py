from flask import Blueprint

bp = Blueprint("pdf",__name__)

from . import routes