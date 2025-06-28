from flask import Blueprint 

bp = Blueprint("meeting" , __name__)

from . import routes
