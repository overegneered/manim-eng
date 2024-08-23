from unittest import mock

import numpy as np
import pytest
from manim_eng._debug.anchor import Anchor
from manim_eng.components._component import MARK_FONT_SIZE
from manim_eng.components._component.mark import Mark


def mock_anchor(x: float, y: float, z: float) -> Anchor:
    anchor_mock = mock.MagicMock(Anchor)
    anchor_mock.pos = np.array([x, y, z])
    return anchor_mock


@pytest.fixture()
def anchor_mock() -> Anchor:
    return mock_anchor(1, 0, 0)


@pytest.fixture()
def centre_reference_mock() -> Anchor:
    return mock_anchor(0, 0, 0)


@pytest.fixture()
def mark_mocked_anchors(anchor_mock: Anchor, centre_reference_mock: Anchor) -> Mark:
    return Mark(anchor_mock, centre_reference_mock)


def test_mark_defaults_to_default_font_size(mark_mocked_anchors: Mark) -> None:
    mark_mocked_anchors.set_text("A")

    assert mark_mocked_anchors.mathtex is not None
    assert np.isclose(mark_mocked_anchors.mathtex.font_size, MARK_FONT_SIZE)


def test_mark_can_have_other_font_size_set(mark_mocked_anchors: Mark) -> None:
    font_size = 34.2

    mark_mocked_anchors.set_text("B", font_size=font_size)

    assert mark_mocked_anchors.mathtex is not None
    assert np.isclose(mark_mocked_anchors.mathtex.font_size, font_size)


def test_mark_attach_requires_anchor_and_centre_reference_to_be_different(
    anchor_mock: Anchor,
) -> None:
    with pytest.raises(
        ValueError, match="`anchor` and `centre_reference` cannot be the same."
    ):
        _ = Mark(anchor_mock, anchor_mock)


def test_set_text_nothing_set_already(mark_mocked_anchors: Mark) -> None:
    mark_text = "C"
    add_patcher = mock.patch.object(Mark, "add")
    remove_patcher = mock.patch.object(Mark, "remove")
    patched_add = add_patcher.start()
    patched_remove = remove_patcher.start()

    mark_mocked_anchors.set_text(mark_text)

    patched_add.assert_called_once()
    patched_remove.assert_not_called()
    assert mark_mocked_anchors.tex_strings == [mark_text]

    add_patcher.stop()
    remove_patcher.stop()


def test_set_text_text_set_already(mark_mocked_anchors: Mark) -> None:
    mark_text_old = "D"
    mark_text_new = "E"
    mark_mocked_anchors.set_text(mark_text_old)
    add_patcher = mock.patch.object(Mark, "add")
    remove_patcher = mock.patch.object(Mark, "remove")
    patched_add = add_patcher.start()
    patched_remove = remove_patcher.start()

    mark_mocked_anchors.set_text(mark_text_new)

    patched_add.assert_called_once()
    patched_remove.assert_called_once()
    assert mark_mocked_anchors.tex_strings == [mark_text_new]

    add_patcher.stop()
    remove_patcher.stop()
