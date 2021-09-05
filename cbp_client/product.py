

class Product:
    def __init__(self, **kwargs):
        for arg_name, arg_value in kwargs.items():
            setattr(self, arg_name, arg_value)


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
