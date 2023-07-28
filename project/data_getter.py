import requests
from binance import Client

headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Content-Length": "123",
    "content-type": "application/json",
    "Host": "p2p.binance.com",
    "Origin": "https://p2p.binance.com",
    "Pragma": "no-cache",
    "TE": "Trailers",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Referer": "https://p2p.binance.com/en/trade/all-payments/USDT?fiat=RUB"
}


class Getter(object):

    def get_p2p(asset, fiat, tradeType, tradePay, transAmount):
        data = {
            "asset": asset,
            "fiat": fiat,
            "merchantCheck": False,
            "page": 1,
            "tradeType": tradeType,
            "payTypes": tradePay,
            "publisherType": None,
            "rows": 20,
            "tradeType": tradeType,
            "transAmount": transAmount
        }

        post_xhr = requests.post(
            'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search',
            headers=headers,
            json=data
        )

        users = post_xhr.json()['data']
        if users != []:
            user_info = {
                'userNo': users[0]['advertiser']['userNo'],
                'sellerNameP2P': users[0]['advertiser']['nickName'],
                'sellerPriceP2P': users[0]['adv']['price'],
                'tradeMethod': tradePay[0]
            }
            return user_info
        else:
            return None

    def get_spot(symb):
        client = Client()
        symbolInfo = client.get_symbol_ticker(symbol=symb)
        return symbolInfo


class Bundle(object):

    def get_p2p_info(first_coin, second_coin, fiat, input_bank, withdrawal_bank, amount):
        p2p_buy = Getter.get_p2p(
            asset=first_coin,
            fiat=fiat,
            tradeType="buy",
            tradePay=[input_bank],
            transAmount=amount
        )

        # получает ордел p2p usdt к rub на продажу
        p2p_sell = Getter.get_p2p(
            asset=second_coin,
            fiat=fiat,
            tradeType="sell",
            tradePay=[withdrawal_bank],
            transAmount=amount
        )

        # цена btcusdt
        pair = first_coin.upper() + second_coin.upper()
        spot_price = Getter.get_spot(pair)

        returner = {'p2p_buy': p2p_buy, 'spot': spot_price, 'p2p_sell': p2p_sell}
        return returner

    def get_diff(curr_input='BTC', curr_out='USDT', curr_fiat='RUB', bank_in='TinkoffNew', bank_out='TinkoffNew',
                 amount=10000,
                 source_value=1) -> dict:
        collect = Bundle.get_p2p_info(first_coin=curr_input,
                                      second_coin=curr_out,
                                      fiat=curr_fiat,
                                      input_bank=bank_in,
                                      withdrawal_bank=bank_out,
                                      amount=amount)

        user_no = str(collect['p2p_buy']['userNo'])  # id первого p2p продавца
        name_p2p_seller = str(collect['p2p_buy']['sellerNameP2P'])  # номер первого p2p продавца

        val_p2p_first = float(collect['p2p_buy']['sellerPriceP2P'])  # вход закуп за фиат (1-й p2p продавец)
        val_spot = float(collect['spot']['price'])  # свап spot
        val_p2p_second = float(collect['p2p_sell']['sellerPriceP2P'])  # закрытие продажа за фиат (2-й продавец)

        k = source_value * val_p2p_first
        a = val_p2p_second * (source_value * val_spot)
        diff = a - k
        percent = diff / (k / 100)

        big_list = {
            'difference': diff,
            'start_value': k,
            'finish_value': a,
            'percent': percent,
            'name_seller': name_p2p_seller,
            'user_no': user_no,
            'spot_price': val_spot,
            'price_p2p_first': val_p2p_first,
            'price_p2p_second': val_p2p_second
        }

        return big_list
