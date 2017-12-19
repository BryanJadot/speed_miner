class Wallets():
    @staticmethod
    def get_wallet_for(currency):
        currency = currency.strip().lower()
        if currency == "btc":
            return "188QXtDWqS1jNC5yWqgbnAgCiPEw7ESV3X"
        else:
            raise "Unsupported currency wallet"
