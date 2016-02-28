from flask import Blueprint, jsonify
from drip.models import Story, Event

bp = Blueprint('routes', __name__)


@bp.route('/events')
def events():
    """most recent events"""
    events = Event.query.order_by(Event.created_at.desc()).limit(50).all()
    return jsonify(result=[e.as_dict() for e in events])


@bp.route('/events/<int:id>')
def event(id):
    """most recent events"""
    event = Event.query.get_or_404(id)
    return jsonify(result=event.as_dict())


@bp.route('/stories')
def stories():
    """most recent stories"""
    stories = Story.query.order_by(Story.created_at.desc()).limit(50)
    return jsonify(result=[s.as_dict() for s in stories])
