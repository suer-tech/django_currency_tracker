from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache

from tinkoff.invest import (
    CandleInstrument,
    Client,
    SubscriptionInterval,
)
from tinkoff.invest.market_data_stream.market_data_stream_manager import MarketDataStreamManager
from .config import token


def get_usd_price():
    with Client(token) as client:
        market_data_stream: MarketDataStreamManager = client.create_market_data_stream()
        market_data_stream.candles.waiting_close().subscribe(
            [
                CandleInstrument(
                    figi='BBG0013HGFT4',
                    interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                )
            ]
        )
        for marketdata in market_data_stream:
            if marketdata.candle:
                last_price = marketdata.candle.close
                last_price_units = last_price.units
                last_price_nano = last_price.nano
                numeric_value = float(f"{last_price_units}.{last_price_nano}")
                return numeric_value


@csrf_exempt
def get_current_usd(request):
    if request.method == 'GET':
        usd_price = get_usd_price()
        cache.set('usd_price', usd_price, timeout=60)

        last_10_prices = cache.get('last_10_prices', [])
        last_10_prices.append(usd_price)
        last_10_prices = last_10_prices[-10:]
        cache.set('last_10_prices', last_10_prices)

        response_data = {
            'usd_price': usd_price,
            'last_10_prices': last_10_prices,
        }
        return JsonResponse(response_data)


def index(request):
    return render(request, 'index.html')
