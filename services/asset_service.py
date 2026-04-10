from models.site_asset import SiteAsset


def get_asset(slot_key):
    """テンプレートから呼び出してサイト画像・記事情報を取得する"""
    asset = SiteAsset.query.filter_by(slot_key=slot_key).first()
    if asset and (asset.file_path or asset.content_html):
        return asset
    return None
