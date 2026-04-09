"""DB初期化 + シードデータ投入"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.seed import seed

if __name__ == '__main__':
    print('DBをリセットしてシードデータを投入します...')
    seed()
