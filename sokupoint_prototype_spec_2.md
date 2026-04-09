# 即ポイントクラブ プロトタイプ 仕様書 v0.2

**プロジェクト所属**: オールワン配下（かなでシステムとは別管理）
**プロジェクトID**: `p003_sokupoint`
**バージョン**: 0.3 (プロトタイプ / デモンストレーション版)
**作成日**: 2026-04-09
**目的**: 企画書「即ポイントクラブ」の社内デモ・企画通し用プロトタイプ
**デプロイ先**: ローカル開発 → VPSサーバー（関係者閲覧用）
**予定URL**: https://p003.vpsk.net

---

## 1. プロジェクト概要

### 1.1 何を作るか
風俗業界向け会員参加型ポイントサイトのデモ版。関係者がVPS上のデモサイトを実際に触って「毎日訪れたくなる体験」を体感できるプロトタイプ。

### 1.2 プロトタイプの位置付け
- **社内＋関係者デモ用**: VPSにデプロイして関係者にURLを共有し、スマホ/PC双方から触れる状態にする
- **管理画面付き**: 企画レビュー中に「ゲームの差替」「ロゴ変更」「バナー差替」「クーポン追加」などを即座に反映できるよう、簡易管理画面を併設
- **データは使い捨て**: SQLite + ローカル画像ストレージで完結

### 1.3 デモシナリオ
1. 関係者にURLを共有 → 18歳確認ゲート → デモユーザー選択画面（3名）
2. 「VIP会員 太郎」でログイン → ダッシュボード
3. ログインボーナス受取 → ポイント加算
4. 1日1回のミニゲームを引く → 当選演出
5. エントリー式クーポンに応募
6. 「来店チェックイン」ボタンで模擬チェックイン
7. トロフィー獲得通知
8. マイページでランク・ポイント・トロフィー・履歴確認
9. 別ユーザー（ブロンズ会員）に切替 → 見え方の違いを確認
10. **管理画面(`/admin`)でゲームを別種類に差替えて再デモ**

---

## 2. 技術スタック

| 項目 | 採用技術 | 理由 |
|---|---|---|
| 言語 | Python 3.12 | オールワン配下の新規アプリ。構成はかなでシステムのa013等を参考にしつつ独立管理 |
| フレームワーク | Flask + Blueprint | 実績ある構成を踏襲 |
| DB | SQLite | プロトに十分・ファイル1本で運用楽 |
| ORM | SQLAlchemy | 将来のPG移行を考慮 |
| マイグレーション | Flask-Migrate (Alembic) | スキーマ変更の追跡 |
| テンプレート | Jinja2 | Flask標準 |
| フロント | HTML + Tailwind CSS (CDN) + 素のJS | ビルド不要・レスポンシブが楽 |
| アイコン | Lucide Icons (CDN) | **絵文字は使わず単色SVGアイコンで統一** |
| フォーム | Flask-WTF | 管理画面のCSRF対策 |
| 画像アップロード | Pillow | リサイズ処理 |
| 本番サーバー | Gunicorn + Nginx (Ubuntu VPS) | VPS上の独立アプリとしてデプロイ |
| 認証（一般） | デモユーザー固定切替 | プロト用モック |
| 認証（管理画面） | Basic認証 or 簡易パスワード | 関係者に触られない保護 |

---

## 3. ディレクトリ構成

```
p003_sokupoint/
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── CLAUDE.md
├── .env.example
├── .gitignore
├── instance/
│   └── sokupoint.db
├── migrations/                    # Flask-Migrate
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── point.py
│   ├── login_bonus.py
│   ├── game.py                    # Game(マスタ), GamePlayLog
│   ├── coupon.py
│   ├── checkin.py
│   ├── trophy.py
│   └── site_asset.py              # SiteAsset(ロゴ/バナー管理)
├── blueprints/
│   ├── __init__.py
│   ├── auth.py
│   ├── home.py
│   ├── login_bonus.py
│   ├── game.py
│   ├── coupon.py
│   ├── rank.py
│   ├── checkin.py
│   ├── trophy.py
│   └── admin/                     # 管理画面
│       ├── __init__.py
│       ├── dashboard.py
│       ├── games.py
│       ├── coupons.py
│       ├── users.py
│       ├── trophies.py
│       └── assets.py              # ロゴ/バナー差替
├── services/
│   ├── point_service.py
│   ├── rank_service.py
│   ├── trophy_service.py
│   ├── game_engine.py             # ゲームタイプ別の実行エンジン
│   └── asset_service.py           # 画像アップロード処理
├── templates/
│   ├── base.html
│   ├── _partials/
│   │   ├── header.html
│   │   ├── tab_bar.html
│   │   └── flash.html
│   ├── age_gate.html
│   ├── user_switch.html
│   ├── home.html
│   ├── login_bonus.html
│   ├── game/
│   │   ├── play.html              # 全ゲーム共通コンテナ
│   │   ├── types/                 # ゲームタイプ別テンプレート
│   │   │   ├── scratch.html
│   │   │   ├── roulette.html
│   │   │   └── quiz.html
│   │   └── result.html
│   ├── coupon/
│   ├── rank.html
│   ├── checkin.html
│   ├── trophy/
│   ├── me.html
│   └── admin/
│       ├── base.html
│       ├── dashboard.html
│       ├── games/
│       │   ├── list.html
│       │   ├── create.html
│       │   └── edit.html
│       ├── coupons/
│       ├── users/
│       ├── trophies/
│       └── assets.html
├── static/
│   ├── css/
│   │   └── custom.css             # Tailwindで足りない部分
│   ├── js/
│   │   ├── scratch.js
│   │   ├── roulette.js
│   │   └── quiz.js
│   └── uploads/                   # ユーザーアップロード画像(gitignore)
│       ├── logo/
│       ├── banners/
│       └── games/
└── scripts/
    ├── seed.py                    # デモデータ投入
    └── reset_db.py
```

---

## 4. データベース設計

### 4.1 users（会員）
| カラム | 型 | 備考 |
|---|---|---|
| id | INTEGER PK | |
| nickname | TEXT | 「太郎」等 |
| rank_code | TEXT | BRONZE/SILVER/GOLD/VIP |
| total_points | INTEGER | 保有ポイント |
| lifetime_points | INTEGER | 累計獲得ポイント |
| consecutive_login_days | INTEGER | 連続ログイン日数 |
| last_login_at | DATETIME | |
| created_at | DATETIME | |

### 4.2 ranks（ランクマスタ）
| カラム | 型 | 備考 |
|---|---|---|
| code | TEXT PK | |
| name | TEXT | |
| min_lifetime_points | INTEGER | |
| color | TEXT | |
| bonus_multiplier | REAL | |

### 4.3 point_histories
| カラム | 型 | 備考 |
|---|---|---|
| id | INTEGER PK | |
| user_id | FK | |
| amount | INTEGER | |
| source | TEXT | login_bonus/game/coupon/checkin/trophy |
| description | TEXT | |
| created_at | DATETIME | |

### 4.4 login_bonus_logs
| カラム | 型 | 備考 |
|---|---|---|
| id | INTEGER PK | |
| user_id | FK | |
| received_date | DATE | UNIQUE(user_id, date) |
| points_awarded | INTEGER | |
| consecutive_day | INTEGER | |

### 4.5 games（ゲームマスタ）★管理画面で管理
| カラム | 型 | 備考 |
|---|---|---|
| id | INTEGER PK | |
| name | TEXT | 「今日のスクラッチ」等の表示名 |
| game_type | TEXT | scratch / roulette / quiz |
| description | TEXT | |
| is_active | BOOLEAN | 現在公開中か |
| priority | INTEGER | 複数アクティブ時の表示順 |
| win_rate | REAL | 当選率 0.0-1.0 |
| points_on_win_min | INTEGER | 当選時最小P |
| points_on_win_max | INTEGER | 当選時最大P |
| points_on_lose | INTEGER | 外れ時参加賞P |
| config_json | TEXT | ゲームタイプ別の追加設定(JSON) |
| thumbnail_path | TEXT | 一覧画面用サムネ |
| created_at | DATETIME | |
| updated_at | DATETIME | |

### 4.6 quiz_questions（クイズ問題マスタ）
game_type='quiz' のゲームに紐づく問題。管理画面から登録。

| カラム | 型 | 備考 |
|---|---|---|
| id | INTEGER PK | |
| game_id | FK → games.id | |
| question_text | TEXT | |
| image_path | TEXT | 問題画像(シルエット等) |
| choice_1 | TEXT | |
| choice_2 | TEXT | |
| choice_3 | TEXT | |
| choice_4 | TEXT | |
| correct_choice | INTEGER | 1-4 |
| explanation | TEXT | 解説 |

### 4.7 game_play_logs
| カラム | 型 | 備考 |
|---|---|---|
| id | INTEGER PK | |
| user_id | FK | |
| game_id | FK | |
| played_date | DATE | UNIQUE(user_id, game_id, date) |
| result | TEXT | win / lose |
| points_awarded | INTEGER | |
| played_at | DATETIME | |

### 4.8 coupons（クーポンマスタ）★管理画面で管理
| カラム | 型 | 備考 |
|---|---|---|
| id | INTEGER PK | |
| title | TEXT | |
| description | TEXT | |
| required_rank | TEXT | |
| entry_start | DATETIME | |
| entry_end | DATETIME | |
| winner_count | INTEGER | |
| image_path | TEXT | アップロード画像 |
| is_active | BOOLEAN | |

### 4.9 coupon_entries
| カラム | 型 | 備考 |
|---|---|---|
| id | INTEGER PK | |
| user_id | FK | |
| coupon_id | FK | |
| entered_at | DATETIME | |
| is_winner | BOOLEAN | |

### 4.10 stores（店舗マスタ）★管理画面で管理
| カラム | 型 | 備考 |
|---|---|---|
| id | INTEGER PK | |
| name | TEXT | |
| area | TEXT | |
| qr_token | TEXT | |
| is_active | BOOLEAN | |

### 4.11 checkins
| カラム | 型 | 備考 |
|---|---|---|
| id | INTEGER PK | |
| user_id | FK | |
| store_id | FK | |
| checked_in_at | DATETIME | |
| points_awarded | INTEGER | |

### 4.12 trophies（トロフィーマスタ）★管理画面で管理
| カラム | 型 | 備考 |
|---|---|---|
| id | INTEGER PK | |
| code | TEXT UNIQUE | |
| name | TEXT | |
| description | TEXT | |
| icon_name | TEXT | Lucideアイコン名（例: trophy, star, medal） |
| condition_type | TEXT | login_streak/game_play_count/checkin_count等 |
| condition_value | INTEGER | 条件値 |
| points_reward | INTEGER | |
| is_active | BOOLEAN | |

### 4.13 user_trophies
| カラム | 型 | 備考 |
|---|---|---|
| id | INTEGER PK | |
| user_id | FK | |
| trophy_id | FK | |
| unlocked_at | DATETIME | |

### 4.14 site_assets（サイト画像設定）★管理画面で管理
ロゴ・バナー等の差替用。1レコード1スロット。

| カラム | 型 | 備考 |
|---|---|---|
| id | INTEGER PK | |
| slot_key | TEXT UNIQUE | logo_header / banner_home_1 / banner_home_2 / favicon |
| file_path | TEXT | アップロードファイルパス |
| alt_text | TEXT | |
| link_url | TEXT | バナーのリンク先(任意) |
| updated_at | DATETIME | |

---

## 5. デモ用シードデータ

### 5.1 デモユーザー（3名固定）
| ID | ニックネーム | ランク | 保有P | 連続ログイン |
|---|---|---|---|---|
| 1 | 太郎（VIP） | VIP | 12,000 | 30日 |
| 2 | 次郎（GOLD） | GOLD | 4,500 | 12日 |
| 3 | 三郎（BRONZE） | BRONZE | 200 | 1日 |

### 5.2 ランク定義
| コード | 名前 | 必要累計P | 倍率 | 色(テーマに合わせピンク基調) |
|---|---|---|---|---|
| BRONZE | ブロンズ | 0 | 1.0 | #E5B0A5 |
| SILVER | シルバー | 1,000 | 1.2 | #D0D0D0 |
| GOLD | ゴールド | 5,000 | 1.5 | #F5C542 |
| VIP | VIP | 10,000 | 2.0 | #E63946 |

### 5.3 初期ゲーム（3つ、管理画面から差替可能）
1. スクラッチ（当選率30%、10〜100P）
2. ルーレット（当選率25%、20〜200P）
3. クイズ（問題3問、正解時50P）

### 5.4 クーポン・店舗・トロフィー
前版と同じ（クーポン4件/店舗3件/トロフィー10種）

---

## 6. 画面一覧（ルーティング）

### 6.1 一般ユーザー画面
| # | 画面 | URL | 概要 |
|---|---|---|---|
| 1 | 年齢確認ゲート | `/age-gate` | 18歳以上ですか？ |
| 2 | デモユーザー選択 | `/demo/switch` | 3名から選択 |
| 3 | ダッシュボード | `/` | ランク・P・本日のタスク・バナー |
| 4 | ログインボーナス | `/bonus` | 受取ボタン |
| 5 | ゲーム一覧 | `/games` | アクティブなゲーム一覧 |
| 6 | ゲームプレイ | `/games/<id>/play` | ゲームタイプに応じて分岐 |
| 7 | クーポン一覧 | `/coupons` | |
| 8 | クーポン応募 | `/coupons/<id>/entry` | |
| 9 | ランクページ | `/rank` | |
| 10 | チェックイン | `/checkin` | |
| 11 | トロフィー一覧 | `/trophies` | |
| 12 | マイページ | `/me` | |

### 6.2 管理画面
| # | 画面 | URL | 概要 |
|---|---|---|---|
| A1 | 管理ログイン | `/admin/login` | 簡易パスワード認証 |
| A2 | 管理ダッシュボード | `/admin` | 統計サマリ |
| A3 | ゲーム一覧 | `/admin/games` | CRUD |
| A4 | ゲーム新規/編集 | `/admin/games/new`, `/admin/games/<id>/edit` | |
| A5 | クイズ問題管理 | `/admin/games/<id>/questions` | クイズ型のみ |
| A6 | クーポン一覧/編集 | `/admin/coupons` | CRUD |
| A7 | 店舗一覧/編集 | `/admin/stores` | CRUD |
| A8 | ユーザー一覧 | `/admin/users` | デモユーザー情報確認・ポイント調整 |
| A9 | トロフィー管理 | `/admin/trophies` | CRUD |
| A10 | サイト画像設定 | `/admin/assets` | ロゴ・バナー差替 |

---

## 7. 機能別仕様

### 7.1 ログインボーナス
- 当日未受取なら受取ボタン、受取済なら次回までカウントダウン
- 付与量: 基本50P、7日目100P、14日目200P、30日目500P（ランク倍率適用）
- 7日連続で該当トロフィー解放

### 7.2 ミニゲーム（プラガブル設計）
**重要**: ゲームは「games」テーブルで管理され、管理画面から自由に追加・編集・有効/無効切替ができる。

#### 7.2.1 ゲーム一覧画面（`/games`）
- `is_active=True` のゲームを `priority` 順で表示
- 各ゲームに「本日プレイ済」バッジ

#### 7.2.2 ゲームプレイ画面（`/games/<id>/play`）
- `game_engine.py` がゲームタイプを判別し、対応するテンプレート(`game/types/scratch.html` 等)を動的に読込
- 1日1回制限は `game_play_logs` でチェック

#### 7.2.3 ゲームタイプ（初期3種）
| タイプ | テンプレート | JS | 設定項目(config_json) |
|---|---|---|---|
| scratch | scratch.html | scratch.js | - |
| roulette | roulette.html | roulette.js | segments: [{label, color}] |
| quiz | quiz.html | quiz.js | shuffle: true/false |

#### 7.2.4 結果判定（共通）
- `game_engine.determine_result(game, user)` が `win_rate` に基づき勝敗判定
- 当選時は `points_on_win_min`〜`points_on_win_max` の範囲でランダム付与
- 外れ時は `points_on_lose` を付与
- `game_play_logs` に記録

#### 7.2.5 新ゲームタイプの追加手順（将来拡張）
1. `game_engine.py` に新タイプ用の判定ロジック追加
2. `templates/game/types/<new>.html` 作成
3. `static/js/<new>.js` 作成
4. `games` テーブルのgame_type enumに追加

### 7.3 エントリー式クーポン
- 一覧: 応募期間内 + 自ランクで参加可能なクーポンのみ
- 応募ボタンで `coupon_entries` に追加 + 10P付与
- 当落はプロトではランダム

### 7.4 会員ランク制度
- 現在ランク表示 + プログレスバー + 特典一覧
- `lifetime_points` 変動時に `rank_service.check_rank_up()` で自動昇格判定

### 7.5 来店チェックイン
- 店舗選択→ボタンで模擬チェックイン（同日同店舗不可）
- 300P付与 + トロフィー判定

### 7.6 トロフィー
- 取得済カラー / 未取得グレーアウト
- 解放条件は `trophies.condition_type` + `condition_value` で汎用化
- 各アクション後に `trophy_service.check_and_unlock(user_id)` を呼ぶ

### 7.7 管理画面（NEW）

#### 7.7.1 認証
- `/admin/*` はBasic認証または簡易パスワード認証
- `.env` で `ADMIN_USERNAME`, `ADMIN_PASSWORD` を設定
- セッションで保持

#### 7.7.2 管理ダッシュボード
- 登録ユーザー数、総プレイ数、総応募数などの簡易統計
- 「今すぐ差替したい画像・ゲームのショートカット」

#### 7.7.3 ゲーム管理
- 一覧: タイトル、タイプ、有効/無効、当選率、操作ボタン
- 新規作成/編集フォーム:
  - 名前、タイプ選択、説明、サムネアップロード
  - 当選率、当選時ポイント範囲、外れ時ポイント
  - 有効/無効トグル、表示順
  - クイズタイプの場合は保存後に問題管理画面へ誘導
- クイズ問題管理: 問題文、画像、選択肢4つ、正解、解説

#### 7.7.4 クーポン管理
- CRUD（タイトル、説明、画像、期間、参加可能ランク、当選枠）

#### 7.7.5 店舗管理
- CRUD（名前、エリア、QRトークン自動生成）

#### 7.7.6 トロフィー管理
- CRUD（条件タイプ/値、アイコン選択、リワードP）

#### 7.7.7 ユーザー管理
- デモユーザー一覧、ポイント手動調整、ランク変更、履歴閲覧

#### 7.7.8 サイト画像設定（ロゴ・バナー差替）
- スロットベースUI:
  - ヘッダーロゴ
  - ホーム上部バナー①
  - ホーム上部バナー②
  - Favicon
- 各スロットで画像アップロード、alt文言、リンク先URL編集
- アップロードファイルは `static/uploads/` に保存、Pillowでリサイズ（推奨サイズをUIに明記）
- 差替後は即座にサイトに反映

---

## 8. 共通サービス層

### 8.1 `services/point_service.py`
```python
def add_points(user_id, amount, source, description):
    # ランク倍率適用 → users更新 → 履歴記録 → ランク判定 → トロフィー判定
```

### 8.2 `services/rank_service.py`
```python
def check_rank_up(user_id): ...
```

### 8.3 `services/trophy_service.py`
```python
def check_and_unlock(user_id):
    # 全未取得トロフィーについて condition_type を評価
```

### 8.4 `services/game_engine.py`
```python
def get_template(game): ...        # ゲームタイプ別テンプレートパス
def determine_result(game, user):  # 勝敗判定と付与ポイント計算
def can_play_today(user, game):    # 1日1回制限チェック
```

### 8.5 `services/asset_service.py`
```python
def save_upload(file, slot_key):
    # 画像保存、Pillowでリサイズ、site_assetsテーブル更新
def get_asset(slot_key):
    # テンプレートから呼ぶ(base.htmlのロゴ表示等)
```

---

## 9. デザイン方針

### 9.1 カラーパレット
| 用途 | 色 | HEX |
|---|---|---|
| プライマリ（テーマ） | 赤 | `#E63946` |
| アクセント1 | ピンク濃 | `#EF476F` |
| アクセント2 | ピンク淡 | `#FFB4BA` |
| 背景（メイン） | 白 | `#FFFFFF` |
| 背景（セクション） | オフホワイト | `#FFF5F5` |
| 文字（主） | 濃グレー | `#1F2937` |
| 文字（副） | グレー | `#6B7280` |
| ボーダー | 薄ピンク | `#FCE4E8` |
| 成功 | グリーン | `#10B981` |
| 警告 | オレンジ | `#F59E0B` |

### 9.2 デザイン原則
- **背景は白基調**で清潔感を出しつつ、アクセントの赤ピンクで「楽しい・イベント感」を演出
- **ボタン**: プライマリはグラデ(`#E63946` → `#EF476F`)で立体感
- **カード**: 白背景 + 薄ピンクのボーダー(`#FCE4E8`) + 軽い影
- **絵文字は一切使用しない**。アイコンは**Lucide Icons**（単色SVG）で統一
- **アイコンカラー**: 基本は `#E63946`、サブは `#6B7280`
- **フォント**: 日本語は Noto Sans JP、英数字は Inter（Google Fonts CDN）

### 9.3 レスポンシブ設計
- **モバイルファースト**で設計し、ブレイクポイントで PC 対応
- Tailwindのブレイクポイント:
  - `sm`: 640px以上（大きめスマホ）
  - `md`: 768px以上（タブレット）
  - `lg`: 1024px以上（PC）
- **共通レイアウト**:
  - **SP (〜767px)**: 下部固定タブバー(5項目) + シンプルヘッダー（ロゴ + ポイント）
  - **PC (768px〜)**: 上部ヘッダー内にナビゲーション、下部タブバー非表示、コンテンツ幅最大 1024px でセンタリング
- **グリッド**: SP 1列 → タブレット 2列 → PC 3〜4列
- **画像**: `srcset` または CSS `object-fit: cover` でアスペクト調整
- **タップターゲット**: 最小 44px × 44px
- **管理画面も同様にレスポンシブ**（VPS上で関係者がスマホから確認する可能性あり）

### 9.4 共通レイアウト要素
- **ヘッダー（SP）**: ロゴ左 / ポイント＋ランクバッジ右
- **ヘッダー（PC）**: ロゴ左 / ナビメニュー中央 / ポイント＋ランクバッジ＋ユーザー切替右
- **下部タブバー（SPのみ）**: ホーム / ゲーム / クーポン / チェックイン / マイページ（各Lucideアイコン）
- **管理画面**: サイドバーナビ（PC）/ ハンバーガーメニュー（SP）

---

## 10. 実装ステップ（Claude Code向け推奨順序）

### フェーズ1: 基盤
1. **環境構築**: Flask + SQLAlchemy + Flask-Migrate + Flask-WTF セットアップ、`app.py`, `config.py`, `.env.example`
2. **DB設計**: 全モデル実装、初回マイグレーション実行
3. **シードスクリプト**: `scripts/seed.py`でデモデータ投入（ユーザー3名、ランク、ゲーム3種、クーポン、店舗、トロフィー、サイトアセット初期値）
4. **共通レイアウト**: `base.html` + Tailwind/Lucide CDN読込、ヘッダー・タブバー（レスポンシブ）、テーマカラー適用
5. **認証モック**: 年齢ゲート → デモユーザー切替 → セッション管理

### フェーズ2: 一般ユーザー機能
6. **ダッシュボード**: ユーザー情報表示、バナー表示（site_assetsから読込）
7. **ポイントサービス層**: `point_service.add_points()`
8. **ログインボーナス機能**
9. **ゲームエンジン + ゲーム一覧**: `game_engine.py` 実装、プラガブル設計の骨組み
10. **ゲームタイプ実装**: スクラッチ → ルーレット → クイズ の順
11. **ランクサービス + ランクページ**
12. **クーポン機能**
13. **チェックイン機能**
14. **トロフィーサービス + トロフィーページ**
15. **マイページ（履歴表示）**

### フェーズ3: 管理画面
16. **管理認証**: `/admin/login` + Basic認証風の簡易パスワード
17. **管理ダッシュボード**: 統計サマリ
18. **サイト画像設定画面**: ロゴ・バナー差替機能（最初に作ると他の機能のUIも豪華になる）
19. **ゲーム管理 CRUD**: 新規/編集/削除/有効無効切替
20. **クイズ問題管理**
21. **クーポン管理 CRUD**
22. **店舗管理 CRUD**
23. **トロフィー管理 CRUD**
24. **ユーザー管理**

### フェーズ4: デプロイ
25. **デモシナリオ通し確認**（ローカル）
26. **VPSデプロイ準備**: `.env` 設定、Gunicorn起動スクリプト、Nginx設定サンプル作成
27. **VPS配置**（`https://p003.vpsk.net`）

---

## 11. VPSデプロイ仕様

### 11.1 想定構成
- オールワン配下の独立アプリとしてVPSに配置
- 構成: Ubuntu + Nginx + Gunicorn + systemd
- ドメイン: **`https://p003.vpsk.net`**
- SSL: Let's Encrypt
- **かなでシステムの他アプリとはディレクトリ・プロセス・DBを完全分離**

### 11.2 Claude Codeに用意してもらうファイル
- `gunicorn_config.py`
- `systemd` サービスファイルサンプル(`deploy/p003_sokupoint.service`)
- `nginx` 設定サンプル(`deploy/nginx.conf`) — `server_name p003.vpsk.net;` を含む
- `deploy/README.md`(ローカル→VPS手順)

### 11.3 環境変数（`.env`）
```
FLASK_ENV=production
SECRET_KEY=xxx
DATABASE_URL=sqlite:///instance/sokupoint.db
ADMIN_USERNAME=admin
ADMIN_PASSWORD=xxx
UPLOAD_FOLDER=static/uploads
MAX_UPLOAD_MB=5
```

### 11.4 データ永続化
- `instance/sokupoint.db` と `static/uploads/` はVPS上で永続化
- デプロイ時に上書きしない(`git pull`時注意)

---

## 12. プロトタイプで割り切ること

- 本格的な一般ユーザー認証（メール/パスワード登録）
- 決済・ポイント換金
- カモフラージュUI（本番向けに別途仕様化）
- メール送信・プッシュ通知
- 実QRコードスキャン（チェックインはボタン代替、ただしトークンカラムは用意）
- SEO・アクセス解析
- 多言語対応

---

## 13. 本番移行時に差し替えるポイント

| プロト | 本番 |
|---|---|
| SQLite | PostgreSQL |
| デモユーザー固定 | メール認証/電話認証 |
| チェックインボタン | QRコードスキャン |
| Basic認証（管理画面） | ロール型認証 |
| ローカルファイル画像 | Cloudflare R2 |
| カモフラージュUIなし | 天気アプリ風UI切替 |

---

## 14. Claude Code 向け補足

- `CLAUDE.md` にこの仕様書の要約と「まずは`scripts/seed.py`を叩いて動作確認」と記載
- フェーズ単位で `git commit` を推奨
- UIはテーマカラー（赤ピンク×白）とLucideアイコンの統一を優先
- **絵文字は使用禁止**。アイコンが必要な箇所はLucide Iconsで統一
- レスポンシブは必ず SP / PC 両方で確認すること
- 管理画面の画像アップロードは保存先ディレクトリの存在チェックを忘れずに
- 不明点があれば実装を止めて質問すること

---

**以上。この仕様書でプロトタイプ構築を進めてください。**
