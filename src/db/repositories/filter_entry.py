from ..models.filter_entry import FilterEntry
from ..repository import Repository


class FilterEntryRepository(Repository[FilterEntry]):
    repository_model = FilterEntry