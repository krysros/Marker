from enum import Enum


class Dd(Enum):
    FILTER = 1
    SORT = 2
    ORDER = 3


class Dropdown:
    def __init__(self, items, typ, _filter=None, _sort=None, _order=None):
        self.items = items
        self.typ = typ
        self._filter = _filter
        self._sort = _sort
        self._order = _order

    @property
    def title(self):
        if self.typ == Dd.FILTER:
            return "Filtruj"
        elif self.typ == Dd.SORT:
            return "Sortuj"
        elif self.typ == Dd.ORDER:
            return "Kolejność"

    @property
    def current_item(self):
        if self.typ == Dd.FILTER:
            return self._filter
        elif self.typ == Dd.SORT:
            return self._sort
        elif self.typ == Dd.ORDER:
            return self._order

    @property
    def icon(self):
        if self.typ == Dd.FILTER:
            return '<i class="bi bi-filter"></i>'
        elif self.typ == Dd.SORT:
            if self._order == "asc":
                return '<i class="bi bi-sort-alpha-down"></i>'
            elif self._order == "desc":
                return '<i class="bi bi-sort-alpha-down-alt"></i>'
        elif self.typ == Dd.ORDER:
            if self._order == "asc":
                return '<i class="bi bi-caret-up-fill"></i>'
            elif self._order == "desc":
                return '<i class="bi bi-caret-down-fill"></i>'
