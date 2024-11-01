from ..models.platform import Platform
from ..repository import Repository


class PlatformRepository(Repository[Platform]):
    repository_model = Platform