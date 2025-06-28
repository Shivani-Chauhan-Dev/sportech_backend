from flask import Blueprint 

bp = Blueprint("aichat" , __name__)

from . import routes