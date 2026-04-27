from identity.aggregates.user import User

"""TokenService service."""
class TokenService:
    def create(self, input: User) -> User:
        raise NotImplementedError('not implemented')
    def findById(self, id: str) -> User | None:
        raise NotImplementedError('not implemented')
    def list(self, limit: float) -> list[User]:
        raise NotImplementedError('not implemented')
    def delete(self, id: str) -> None:
        raise NotImplementedError('not implemented')

