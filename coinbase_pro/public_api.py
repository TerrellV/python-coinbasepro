from coinbase_pro.api import API


class CBProPublic():
    def __init__(self, sandbox_mode=False):
        LIVE_URL = 'https://api.pro.coinbase.com/'
        SANDBOX_URL = 'https://api-public.sandbox.pro.coinbase.com/'

        base_url = SANDBOX_URL if sandbox_mode else LIVE_URL

        self.api = API(base_url)
    
    def get_asset_usd_price(self, currency):
        endpoint = f'products/{currency.upper()}-USD/ticker'
        price = self.api.get(endpoint).json()['price']
        return price