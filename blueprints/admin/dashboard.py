from flask import render_template
from blueprints.admin import admin_bp, admin_required
from models.user import User
from models.game import GamePlayLog
from models.coupon import CouponEntry
from models.checkin import Checkin
from models.trophy import UserTrophy


@admin_bp.route('/')
@admin_required
def dashboard():
    stats = {
        'user_count': User.query.count(),
        'play_count': GamePlayLog.query.count(),
        'entry_count': CouponEntry.query.count(),
        'checkin_count': Checkin.query.count(),
        'trophy_count': UserTrophy.query.count(),
    }
    return render_template('admin/dashboard.html', stats=stats)
