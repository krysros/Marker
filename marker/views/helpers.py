from enum import Enum


class Dd(Enum):
    FILTER = 1
    SORT = 2
    ORDER = 3


class Dropdown:
    def __init__(self, items, typ, filter=None, sort=None, order=None):
        self.items = items
        self.typ = typ
        self.filter = filter
        self.sort = sort
        self.order = order

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
            return self.filter
        elif self.typ == Dd.SORT:
            return self.sort
        elif self.typ == Dd.ORDER:
            return self.order

    @property
    def icon(self):
        if self.typ == Dd.FILTER:
            return '<i class="bi bi-filter"></i>'
        elif self.typ == Dd.SORT:
            if self.order == 'asc':
                return '<i class="bi bi-sort-alpha-down"></i>'
            elif self.order == 'desc':
                return '<i class="bi bi-sort-alpha-down-alt"></i>'
        elif self.typ == Dd.ORDER:
            if self.order == 'asc':
                return '<i class="bi bi-caret-up-fill"></i>'
            elif self.order == 'desc':
                return '<i class="bi bi-caret-down-fill"></i>'
