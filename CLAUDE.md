# p003_sokupoint - 即ポイントクラブ

このプロジェクトはオールワン配下の p003_sokupoint です。
かなでシステム(a0XX)とは完全に独立したアプリとして管理してください。
仕様書は sokupoint_prototype_spec_2.md を参照。

## 概要
風俗業界向け会員参加型ポイントサイトのデモ版プロトタイプ。
Flask + SQLAlchemy + Tailwind CSS で構築。

## クイックスタート
```bash
cd D:\allone\p003_sokupoint
.\venv\Scripts\python scripts\seed.py   # デモデータ投入
.\venv\Scripts\python app.py             # サーバー起動 (port 5003)
```
- 一般画面: http://localhost:5003
- 管理画面: http://localhost:5003/admin/login (admin / demo1234)

## 環境
- ローカル: Windows 11, Python 3.12.10
- サーバー: Ubuntu VPS (Nginx + Gunicorn + Flask)
- バージョン管理: Git + GitHub (アカウント: ochiken7)
- デプロイフロー: ローカル -> GitHub -> VPS (git pull)

## 技術スタック
- Python 3.12 / Flask / SQLAlchemy / Flask-Migrate / Flask-WTF
- Tailwind CSS (CDN) / Lucide Icons (CDN) / Noto Sans JP + Inter
- SQLite (instance/sokupoint.db)

## ディレクトリ構成
- `app.py` - アプリケーションファクトリ
- `extensions.py` - db, migrate, csrf の定義
- `config.py` - 設定クラス
- `models/` - 全DBモデル
- `blueprints/` - 一般画面 + admin/配下に管理画面
- `services/` - ビジネスロジック (point, rank, trophy, game_engine, asset)
- `templates/` - Jinja2テンプレート
- `static/` - CSS, JS, uploads
- `scripts/` - seed.py, reset_db.py
- `deploy/` - systemd, nginx設定サンプル

## お約束
- プログラム初心者向けに専門用語は使わないでください
- 日本語で回答してください
- 絵文字は使用禁止。アイコンはLucide Iconsで統一
- デザインカラー: 赤(#E63946) x ピンク(#EF476F) x 白基調

## github
- ユーザー名: ochiken7
- 予定URL: https://p003.vpsk.net

## よく使うツール
- Claude Code / claude.ai / Cowork
- Stream Deck (ショートカット操作用)
