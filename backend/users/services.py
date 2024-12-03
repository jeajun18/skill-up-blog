from core.base_service import BaseService
from users.models import User


class UserService(BaseService[User]):
    model = User

    def get_by_email(self, email: str) -> User | None:
        return self.get(email=email) 