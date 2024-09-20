from unittest import mock

import manim as mn
import pytest
from manim_eng._base.mark import Mark, Markable


class SubclassesMarkable(Markable):
    def __init__(self) -> None:
        super().__init__()
        self.mark = mock.MagicMock(Mark)


@pytest.fixture()
def markable_dummy() -> SubclassesMarkable:
    return SubclassesMarkable()


def test_set_mark_not_already_added(markable_dummy: SubclassesMarkable) -> None:
    label = "A"

    with mock.patch.object(mn.VGroup, "add") as patched_add:
        markable_dummy._set_mark(markable_dummy.mark, label)

        patched_add.assert_called_once()
    markable_dummy.mark.set_text.assert_called_once_with(label)


def test_set_mark_already_added(markable_dummy: SubclassesMarkable) -> None:
    label_old, label_new = "B", "C"
    markable_dummy._set_mark(markable_dummy.mark, label_old)

    with mock.patch.object(mn.VGroup, "add") as patched_add:
        markable_dummy._set_mark(markable_dummy.mark, label_new)

        patched_add.assert_not_called()
    markable_dummy.mark.set_text.assert_has_calls(
        [mock.call(label_old), mock.call(label_new)]
    )


def test_clear_mark_mark_present(markable_dummy: SubclassesMarkable) -> None:
    markable_dummy._set_mark(markable_dummy.mark, "D")

    with mock.patch.object(mn.VGroup, "remove") as patched_remove:
        markable_dummy._clear_mark(markable_dummy.mark)

        patched_remove.assert_called_once_with(markable_dummy.mark)


def test_clear_mark_mark_not_present(markable_dummy: SubclassesMarkable) -> None:
    with mock.patch.object(mn.VGroup, "remove") as patched_remove:
        markable_dummy._clear_mark(markable_dummy.mark)

        patched_remove.assert_not_called()
