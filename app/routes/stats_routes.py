from flask import Blueprint, render_template
from app.services.statistics_service import get_statistics

stats_bp = Blueprint('stats', __name__, url_prefix='/stats')

@stats_bp.route('/')
def stats_page():
    statistics_data = get_statistics()
    return render_template('stats.html', statistics=statistics_data)
