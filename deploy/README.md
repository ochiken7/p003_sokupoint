# p003_sokupoint デプロイ手順

## 前提
- Ubuntu VPS (Nginx + Gunicorn)
- Python 3.12
- ドメイン: p003.vpsk.net
- GitHub: ochiken7

---

## 1. 初回セットアップ (VPS)

```bash
# アプリディレクトリ作成
sudo mkdir -p /var/www/p003_sokupoint
sudo chown www-data:www-data /var/www/p003_sokupoint

# リポジトリクローン
cd /var/www
sudo -u www-data git clone https://github.com/ochiken7/p003_sokupoint.git

# Python仮想環境
cd /var/www/p003_sokupoint
sudo -u www-data python3 -m venv venv
sudo -u www-data ./venv/bin/pip install -r requirements.txt

# .env設定
sudo -u www-data cp .env.example .env
sudo -u www-data nano .env
# SECRET_KEY, ADMIN_PASSWORD を本番用に変更
# FLASK_ENV=production に設定

# DB初期化 + シードデータ
sudo -u www-data ./venv/bin/python -m flask db upgrade
sudo -u www-data ./venv/bin/python scripts/seed.py

# uploadsディレクトリ作成
sudo -u www-data mkdir -p static/uploads/{logo,banners,games}
```

## 2. systemd サービス登録

```bash
sudo cp deploy/p003_sokupoint.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable p003_sokupoint
sudo systemctl start p003_sokupoint
sudo systemctl status p003_sokupoint
```

## 3. Nginx設定

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/p003_sokupoint
sudo ln -s /etc/nginx/sites-available/p003_sokupoint /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 4. SSL証明書 (Let's Encrypt)

```bash
sudo certbot --nginx -d p003.vpsk.net
```

## 5. DNS設定

p003.vpsk.net の Aレコードを VPS の IPアドレスに向ける。

---

## デプロイ更新手順

```bash
cd /var/www/p003_sokupoint
sudo -u www-data git pull origin main
sudo -u www-data ./venv/bin/pip install -r requirements.txt
sudo -u www-data ./venv/bin/python -m flask db upgrade
sudo systemctl restart p003_sokupoint
```

注意: `instance/sokupoint.db` と `static/uploads/` は git pull で上書きされません (.gitignore済)。

---

## トラブルシューティング

```bash
# サービスログ確認
sudo journalctl -u p003_sokupoint -f

# Gunicorn直接起動テスト
cd /var/www/p003_sokupoint
sudo -u www-data ./venv/bin/gunicorn -c gunicorn_config.py wsgi:app

# DBリセット (データ初期化)
sudo -u www-data ./venv/bin/python scripts/seed.py
```
