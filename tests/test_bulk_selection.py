from dataclasses import dataclass

from marker.views import update_selected_items


@dataclass
class _Item:
    id: int


def test_update_selected_items_adds_only_missing_items():
    selected_items = [_Item(1), _Item(3)]
    items = [_Item(1), _Item(2), _Item(4)]

    update_selected_items(selected_items, items, checked=True)

    assert [item.id for item in selected_items] == [1, 3, 2, 4]


def test_update_selected_items_removes_matching_ids():
    selected_items = [_Item(1), _Item(2), _Item(3), _Item(4)]
    items = [_Item(2), _Item(4)]

    update_selected_items(selected_items, items, checked=False)

    assert [item.id for item in selected_items] == [1, 3]


def test_update_selected_items_ignores_duplicates_in_items_input():
    selected_items = [_Item(1)]
    items = [_Item(2), _Item(2), _Item(3)]

    update_selected_items(selected_items, items, checked=True)

    assert [item.id for item in selected_items] == [1, 2, 3]
