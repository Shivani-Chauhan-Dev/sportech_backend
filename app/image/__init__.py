from flask import Blueprint 

bp = Blueprint("image" , __name__)

# from app.customer import routes
from . import routes