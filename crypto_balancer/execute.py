def execute_order(exch, order):  # pragma: no cover
    direction = order.direction.lower()
    return exch.create_order(order.pair, 'limit', direction,
                             order.amount, order.price)
