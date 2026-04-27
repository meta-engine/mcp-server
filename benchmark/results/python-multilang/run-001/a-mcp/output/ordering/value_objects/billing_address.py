"""BillingAddress value object."""
class BillingAddress:
    def __init__(self, street: str, city: str, country: str, postal_code: str):
        self.street = street
        self.city = city
        self.country = country
        self.postal_code = postal_code

