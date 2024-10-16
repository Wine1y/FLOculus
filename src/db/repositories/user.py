from ..models.user import User
from ..repository import Repository


class UserRepository(Repository[User]):
    repository_model = User