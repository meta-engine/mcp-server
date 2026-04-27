from identity.aggregates.user import User

"""UserRepository service."""
class UserRepository:
    def create(self, input: User) -> User:
        raise NotImplementedError('not implemented')
    def findById(self, id: str) -> User | None:
        raise NotImplementedError('not implemented')
    def list(self, limit: float) -> list[User]:
        raise NotImplementedError('not implemented')
    def delete(self, id: str) -> None:
        raise NotImplementedError('not implemented')

