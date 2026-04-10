"""デモデータ投入スクリプト"""
import sys
import os
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from models import (
    User, Rank, Game, QuizQuestion, Coupon, Store, Trophy, SiteAsset
)


def seed():
    app = create_app()
    with app.app_context():
        # 既存データ削除
        db.drop_all()
        db.create_all()

        # === ランクマスタ ===
        ranks = [
            Rank(code='BRONZE', name='ブロンズ', min_lifetime_points=0, color='#E5B0A5', bonus_multiplier=1.0),
            Rank(code='SILVER', name='シルバー', min_lifetime_points=1000, color='#D0D0D0', bonus_multiplier=1.2),
            Rank(code='GOLD', name='ゴールド', min_lifetime_points=5000, color='#F5C542', bonus_multiplier=1.5),
            Rank(code='VIP', name='VIP', min_lifetime_points=10000, color='#E63946', bonus_multiplier=2.0),
        ]
        db.session.add_all(ranks)

        # === デモユーザー（3名） ===
        users = [
            User(id=1, nickname='太郎（VIP）', rank_code='VIP',
                 total_points=12000, lifetime_points=15000,
                 consecutive_login_days=30, last_login_at=datetime.utcnow()),
            User(id=2, nickname='次郎（GOLD）', rank_code='GOLD',
                 total_points=4500, lifetime_points=6000,
                 consecutive_login_days=12, last_login_at=datetime.utcnow()),
            User(id=3, nickname='三郎（BRONZE）', rank_code='BRONZE',
                 total_points=200, lifetime_points=200,
                 consecutive_login_days=1, last_login_at=datetime.utcnow()),
        ]
        db.session.add_all(users)

        # === ゲーム（3種） ===
        games = [
            Game(
                name='今日のスクラッチ', game_type='scratch',
                description='カードを削って当たりを狙おう!',
                is_active=True, priority=1,
                win_rate=0.3, points_on_win_min=10, points_on_win_max=100,
                points_on_lose=1,
            ),
            Game(
                name='ルーレットチャンス', game_type='roulette',
                description='ルーレットを回してポイントGET!',
                is_active=True, priority=2,
                win_rate=0.25, points_on_win_min=20, points_on_win_max=200,
                points_on_lose=1,
                config_json=json.dumps({
                    'segments': [
                        {'label': '20P', 'color': '#EF476F'},
                        {'label': 'ハズレ', 'color': '#6B7280'},
                        {'label': '50P', 'color': '#E63946'},
                        {'label': 'ハズレ', 'color': '#6B7280'},
                        {'label': '100P', 'color': '#F5C542'},
                        {'label': 'ハズレ', 'color': '#6B7280'},
                        {'label': '200P', 'color': '#10B981'},
                        {'label': 'ハズレ', 'color': '#6B7280'},
                    ]
                }),
            ),
            Game(
                name='クイズに挑戦', game_type='quiz',
                description='3問正解でボーナスポイント!',
                is_active=True, priority=3,
                win_rate=1.0,  # クイズは正解判定で決まるので win_rate=1.0
                points_on_win_min=50, points_on_win_max=50,
                points_on_lose=5,
                config_json=json.dumps({'shuffle': True}),
            ),
        ]
        db.session.add_all(games)
        db.session.flush()  # IDを確定

        # === クイズ問題（3問） ===
        quiz_game = games[2]
        questions = [
            QuizQuestion(
                game_id=quiz_game.id,
                question_text='日本で一番高い山は?',
                choice_1='富士山', choice_2='北岳', choice_3='奥穂高岳', choice_4='槍ヶ岳',
                correct_choice=1, explanation='富士山は標高3,776mで日本一です。',
            ),
            QuizQuestion(
                game_id=quiz_game.id,
                question_text='「ポイント」の英語での意味として正しいものは?',
                choice_1='点・得点', choice_2='線', choice_3='面', choice_4='角',
                correct_choice=1, explanation='Pointは「点」や「得点」を意味します。',
            ),
            QuizQuestion(
                game_id=quiz_game.id,
                question_text='1年で最も日が長い日を何という?',
                choice_1='冬至', choice_2='春分', choice_3='夏至', choice_4='秋分',
                correct_choice=3, explanation='夏至は1年で最も昼が長い日です。',
            ),
        ]
        db.session.add_all(questions)

        # === クーポン（4件） ===
        now = datetime.utcnow()
        coupons = [
            Coupon(title='VIP限定 プレミアムクーポン', description='VIP会員だけの特別クーポン',
                   required_rank='VIP', entry_start=now, entry_end=now + timedelta(days=30),
                   winner_count=1, is_active=True,
                   body_html='<p>VIP会員様限定の特別クーポンです。当選された方には、プレミアムコース60分が無料でご利用いただけます。</p><p>このチャンスをお見逃しなく!</p>'),
            Coupon(title='GOLD以上 特別割引', description='ゴールド会員以上が応募可能',
                   required_rank='GOLD', entry_start=now, entry_end=now + timedelta(days=14),
                   winner_count=3, is_active=True,
                   body_html='<p>ゴールド会員以上の方が応募できる割引クーポンです。</p><p>当選者には次回ご利用時に使える <strong>3,000円割引クーポン</strong> をお届けします。3名様に当たります!</p>'),
            Coupon(title='全員参加OK! ドリンク無料券', description='ランク不問で応募できます',
                   required_rank='BRONZE', entry_start=now, entry_end=now + timedelta(days=7),
                   winner_count=10, is_active=True,
                   body_html='<p>ランク不問! どなたでも応募できるキャンペーンです。</p><p>当選された10名様に <strong>ドリンク無料券</strong> をプレゼント。応募するだけで10Pも獲得できます。</p>'),
            Coupon(title='期間終了クーポン（参考用）', description='既に期間が終了したクーポン',
                   required_rank='BRONZE', entry_start=now - timedelta(days=30), entry_end=now - timedelta(days=1),
                   winner_count=5, is_active=False),
        ]
        db.session.add_all(coupons)

        # === 店舗（3件） ===
        import uuid
        stores = [
            Store(name='渋谷本店', area='渋谷', qr_token=uuid.uuid4().hex[:12], is_active=True),
            Store(name='新宿店', area='新宿', qr_token=uuid.uuid4().hex[:12], is_active=True),
            Store(name='池袋店', area='池袋', qr_token=uuid.uuid4().hex[:12], is_active=True),
        ]
        db.session.add_all(stores)

        # === トロフィー（10種） ===
        trophies = [
            Trophy(code='LOGIN_3', name='3日連続ログイン', description='3日連続でログインボーナスを受け取った',
                   icon_name='calendar-check', condition_type='login_streak', condition_value=3, points_reward=50),
            Trophy(code='LOGIN_7', name='1週間ログイン', description='7日連続でログインボーナスを受け取った',
                   icon_name='calendar-heart', condition_type='login_streak', condition_value=7, points_reward=100),
            Trophy(code='LOGIN_30', name='30日連続ログイン', description='30日間毎日ログイン!',
                   icon_name='crown', condition_type='login_streak', condition_value=30, points_reward=500),
            Trophy(code='GAME_1', name='はじめてのゲーム', description='ゲームを初めてプレイした',
                   icon_name='gamepad-2', condition_type='game_play_count', condition_value=1, points_reward=30),
            Trophy(code='GAME_10', name='ゲーム10回', description='ゲームを10回プレイした',
                   icon_name='trophy', condition_type='game_play_count', condition_value=10, points_reward=200),
            Trophy(code='GAME_50', name='ゲームマスター', description='ゲームを50回プレイした',
                   icon_name='medal', condition_type='game_play_count', condition_value=50, points_reward=500),
            Trophy(code='CHECKIN_1', name='初来店', description='初めてチェックインした',
                   icon_name='map-pin', condition_type='checkin_count', condition_value=1, points_reward=50),
            Trophy(code='CHECKIN_10', name='常連さん', description='10回チェックインした',
                   icon_name='star', condition_type='checkin_count', condition_value=10, points_reward=300),
            Trophy(code='POINT_1000', name='1000P達成', description='累計1,000ポイントを獲得した',
                   icon_name='coins', condition_type='lifetime_points', condition_value=1000, points_reward=100),
            Trophy(code='POINT_10000', name='10000P達成', description='累計10,000ポイントを獲得した',
                   icon_name='gem', condition_type='lifetime_points', condition_value=10000, points_reward=1000),
        ]
        db.session.add_all(trophies)

        # === サイトアセット初期値 ===
        assets = [
            SiteAsset(slot_key='logo_header', alt_text='即ポイントクラブ'),
            SiteAsset(slot_key='banner_home_1', alt_text='上部バナー1 (PC)'),
            SiteAsset(slot_key='banner_home_1_sp', alt_text='上部バナー1 (SP)'),
            SiteAsset(slot_key='banner_home_2', alt_text='上部バナー2 (PC)'),
            SiteAsset(slot_key='banner_home_2_sp', alt_text='上部バナー2 (SP)'),
            SiteAsset(slot_key='banner_home_3', alt_text='タスク下バナー'),
            # お知らせ下バナー (600x300 x 2枠)
            SiteAsset(slot_key='banner_news_1', alt_text='お知らせ下バナー左'),
            SiteAsset(slot_key='banner_news_2', alt_text='お知らせ下バナー右'),
            # フッター上バナー (300x150 x 8枠)
            SiteAsset(slot_key='banner_ft_1', alt_text='フッターバナー1'),
            SiteAsset(slot_key='banner_ft_2', alt_text='フッターバナー2'),
            SiteAsset(slot_key='banner_ft_3', alt_text='フッターバナー3'),
            SiteAsset(slot_key='banner_ft_4', alt_text='フッターバナー4'),
            SiteAsset(slot_key='banner_ft_5', alt_text='フッターバナー5'),
            SiteAsset(slot_key='banner_ft_6', alt_text='フッターバナー6'),
            SiteAsset(slot_key='banner_ft_7', alt_text='フッターバナー7'),
            SiteAsset(slot_key='banner_ft_8', alt_text='フッターバナー8'),
            # カスタム記事エリア (5エリア)
            SiteAsset(slot_key='article_wide', alt_text='記事エリア(全幅)'),
            SiteAsset(slot_key='article_half_1', alt_text='記事エリア左上'),
            SiteAsset(slot_key='article_half_2', alt_text='記事エリア右上'),
            SiteAsset(slot_key='article_half_3', alt_text='記事エリア左下'),
            SiteAsset(slot_key='article_half_4', alt_text='記事エリア右下'),
            SiteAsset(slot_key='favicon', alt_text='Favicon'),
        ]
        db.session.add_all(assets)

        db.session.commit()
        print('シードデータの投入が完了しました。')
        print(f'  ランク: {len(ranks)}件')
        print(f'  ユーザー: {len(users)}件')
        print(f'  ゲーム: {len(games)}件')
        print(f'  クイズ問題: {len(questions)}件')
        print(f'  クーポン: {len(coupons)}件')
        print(f'  店舗: {len(stores)}件')
        print(f'  トロフィー: {len(trophies)}件')
        print(f'  サイトアセット: {len(assets)}件')


if __name__ == '__main__':
    seed()
