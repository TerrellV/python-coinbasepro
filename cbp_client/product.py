from collections import namedtuple

Product = namedtuple(
    'Product',
    [
        'id',
        'display_name',
        'base_currency',
        'quote_currency',
        'base_increment',
        'quote_increment',
        'base_min_size',
        'base_max_size',
        'min_market_funds',
        'max_market_funds',
        'status',
        'status_message',
        'margin_enabled',
        'cancel_only',
        'limit_only',
        'post_only',
        'trading_disabled',
        'live',
        'fully_tradeable'
    ]
)


def is_fully_tradeable(product: dict):

    return all([
        product['status'].lower() == 'online',
        product['cancel_only'] is False,
        product['limit_only'] is False,
        product['post_only'] is False,
        product['trading_disabled'] is False
    ])


def is_live(product: dict):
    return product['status'].lower() == 'online'
