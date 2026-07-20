from flask import Blueprint, render_template
from utils.decorators import login_required, email_verified_required

help_bp = Blueprint('help', __name__)

@help_bp.route('/help')
@login_required
@email_verified_required
def index():
    return render_template('help.html')
