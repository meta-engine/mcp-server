from identity.aggregates.user import User

"""UserService service."""
class UserService:
    def create(self, input: dict) -> User:
        raise NotImplementedError('not implemented')
    def find_by_id(self, id: str) -> User | None:
        raise NotImplementedError('not implemented')
    def list(self, limit: int) -> list[User]:
        raise NotImplementedError('not implemented')
    def delete(self, id: str) -> None:
        raise NotImplementedError('not implemented')

