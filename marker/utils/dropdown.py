from enum import Enum


class Dd(Enum):
    SORT = 1
    ORDER = 2


class Dropdown:
    def __init__(
        self, request, items, typ, q, _sort=None, _order=None
    ):
        self.request = request
        self.items = items
        self.typ = typ
        self.q = q
        self._sort = _sort
        self._order = _order

    @property
    def title(self):
        _ = self.request.translate
        match self.typ:
            case Dd.SORT:
                return _("Sort")
            case Dd.ORDER:
                return _("Order")

    @property
    def current_item(self):
        match self.typ:
            case Dd.SORT:
                return self._sort
            case Dd.ORDER:
                return self._order

    @property
    def icon(self):
        match self.typ:
            case Dd.SORT:
                match self._order:
                    case "asc":
                        return '<i class="bi bi-sort-alpha-down"></i>'
                    case "desc":
                        return '<i class="bi bi-sort-alpha-down-alt"></i>'
            case Dd.ORDER:
                match self._order:
                    case "asc":
                        return '<i class="bi bi-caret-up-fill"></i>'
                    case "desc":
                        return '<i class="bi bi-caret-down-fill"></i>'
