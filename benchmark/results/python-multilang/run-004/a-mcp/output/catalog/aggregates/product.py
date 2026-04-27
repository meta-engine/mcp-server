from datetime import datetime

"""Product aggregate root for the catalog domain."""
class Product:
    def __init__(self, id: str, created_at: datetime, updated_at: datetime, name: str, description: str):
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.name = name
        self.description = description

