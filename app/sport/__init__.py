from flask import Blueprint 

bp = Blueprint("sport" , __name__)

from . import routes
