from unittest import mock

import manim as mn
import pytest

from manim_eng._base.mark import Mark
from manim_eng._base.markable import Markable
from manim_eng.units import HOUR, KILO, VOLT


class SubclassesMarkable(Markable):
    def __init__(self) -> None:
        super().__init__()
        self.mark = mock.MagicMock(Mark)


@pytest.fixture
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

        patched_add.assert_called_once()
    markable_dummy.mark.set_text.assert_has_calls(
        [mock.call(label_old), mock.call(label_new)]
    )


def test_set_mark_with_value(markable_dummy: SubclassesMarkable) -> None:
    value = 4.5 * KILO * VOLT / HOUR

    with mock.patch.object(mn.VGroup, "add") as patched_add:
        markable_dummy._set_mark(markable_dummy.mark, value)

        patched_add.assert_called_once()
    markable_dummy.mark.set_text.assert_called_once_with(value.to_latex())


def test_clear_mark(markable_dummy: SubclassesMarkable) -> None:
    markable_dummy._set_mark(markable_dummy.mark, "D")

    with mock.patch.object(mn.VGroup, "remove") as patched_remove:
        markable_dummy._clear_mark(markable_dummy.mark)

        patched_remove.assert_called_once_with(markable_dummy.mark)


def test_add_with_mark(
    markable_dummy: SubclassesMarkable, mark_mocked_anchors: Mark
) -> None:
    markable_dummy.add(mark_mocked_anchors)
    assert markable_dummy._Markable__marks[0] == mark_mocked_anchors

    with mock.patch.object(mn.VGroup, "add") as patched_add:
        markable_dummy.add(mark_mocked_anchors)

        patched_add.assert_called_once_with(mark_mocked_anchors)


def test_add_to_back_with_mark(
    markable_dummy: SubclassesMarkable, mark_mocked_anchors: Mark
) -> None:
    markable_dummy.add_to_back(mark_mocked_anchors)
    assert markable_dummy._Markable__marks[0] == mark_mocked_anchors

    with mock.patch.object(mn.VGroup, "add_to_back") as patched_add_to_back:
        markable_dummy.add_to_back(mark_mocked_anchors)

        patched_add_to_back.assert_called_once_with(mark_mocked_anchors)


def test_remove_with_mark(
    markable_dummy: SubclassesMarkable, mark_mocked_anchors: Mark
) -> None:
    markable_dummy.add(mark_mocked_anchors)

    markable_dummy.remove(mark_mocked_anchors)
    assert len(markable_dummy._Markable__marks) == 0

    with mock.patch.object(mn.VGroup, "remove") as patched_remove:
        markable_dummy.remove(mark_mocked_anchors)

        patched_remove.assert_called_once_with(mark_mocked_anchors)
