import os
from flask import Flask
from extensions import db, migrate, csrf


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # instance / uploads ディレクトリ作成
    os.makedirs(app.instance_path, exist_ok=True)
    for sub in ['logo', 'banners', 'games']:
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], sub), exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # モデル読み込み（マイグレーション用）
    from models import user, point, login_bonus, game, coupon, checkin, trophy, site_asset, home_banner, site_setting  # noqa: F401

    # Blueprint 登録
    from blueprints.auth import auth_bp
    from blueprints.home import home_bp
    from blueprints.login_bonus import login_bonus_bp
    from blueprints.game import game_bp
    from blueprints.rank import rank_bp
    from blueprints.coupon import coupon_bp
    from blueprints.checkin import checkin_bp
    from blueprints.trophy import trophy_bp
    from blueprints.me import me_bp
    from blueprints.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(login_bonus_bp)
    app.register_blueprint(game_bp)
    app.register_blueprint(rank_bp)
    app.register_blueprint(coupon_bp)
    app.register_blueprint(checkin_bp)
    app.register_blueprint(trophy_bp)
    app.register_blueprint(me_bp)
    app.register_blueprint(admin_bp)

    # テンプレートにアセット取得関数を注入
    from services.asset_service import get_asset
    app.jinja_env.globals['get_asset'] = get_asset

    # テンプレートにcurrent_userを注入
    @app.context_processor
    def inject_current_user():
        from flask import session
        from models.user import User
        current_user = None
        if 'user_id' in session:
            current_user = User.query.get(session['user_id'])
        return dict(current_user=current_user)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5003)
