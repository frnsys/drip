from flask import Blueprint, jsonify
from drip.models.event import Event

bp = Blueprint('routes', __name__)


@bp.route('/')
def index():
    events = Event.query.filter(Event.articles.count() > 3).order_by(Event.created_at.desc()).limit(10)
    return jsonify(events)
