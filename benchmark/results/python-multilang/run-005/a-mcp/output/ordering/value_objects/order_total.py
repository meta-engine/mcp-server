"""OrderTotal value object."""
class OrderTotal:
    def __init__(self, amount: int, currency: str):
        self.amount = amount
        self.currency = currency

