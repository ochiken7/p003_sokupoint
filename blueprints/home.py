from flask import Blueprint, render_template, session, redirect, url_for
from models.user import User

home_bp = Blueprint('home', __name__)


@home_bp.route('/')
def index():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.demo_switch'))
    user = User.query.get(user_id)
    if not user:
        session.pop('user_id', None)
        return redirect(url_for('auth.demo_switch'))
    return render_template('home.html', user=user)
