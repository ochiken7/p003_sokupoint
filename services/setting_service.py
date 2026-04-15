from extensions import db
from models.site_setting import SiteSetting


def get_setting(key, default=None):
    s = SiteSetting.query.get(key)
    if s and s.value is not None:
        return s.value
    return default


def get_setting_int(key, default=0):
    val = get_setting(key)
    if val is None:
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def set_setting(key, value):
    s = SiteSetting.query.get(key)
    if not s:
        s = SiteSetting(key=key)
        db.session.add(s)
    s.value = str(value) if value is not None else None
    db.session.commit()
