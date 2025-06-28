from flask import Blueprint 

bp = Blueprint("verify_otp" , __name__)

from . import routes