from unittest import mock

import numpy as np
import pytest
from manim_eng._debug.anchor import Anchor
from manim_eng.components._component import MARK_FONT_SIZE
from manim_eng.components._component.mark import AlreadyAttachedError, Mark


def mock_anchor(x: float, y: float, z: float) -> mock.MagicMock:
    anchor_mock = mock.MagicMock(Anchor)
    anchor_mock.pos = np.array([x, y, z])
    return anchor_mock


def test_mark_defaults_to_default_font_size() -> None:
    anchor = mock_anchor(1, 0, 0)
    centre_reference = mock_anchor(0, 0, 0)
    label = Mark(anchor, centre_reference).set_text("R")

    assert label.mathtex is not None
    assert np.isclose(label.mathtex.font_size, MARK_FONT_SIZE)


def test_mark_can_have_other_font_size_set() -> None:
    anchor = mock_anchor(1, 0, 0)
    centre_reference = mock_anchor(0, 0, 0)
    label = Mark(anchor, centre_reference)
    font_size = 34.2

    label.set_text("R", font_size=font_size)

    assert label.mathtex is not None
    assert np.isclose(label.mathtex.font_size, font_size)


def test_mark_attach_requires_anchor_and_centre_reference_to_be_different() -> None:
    anchor = mock_anchor(0, 0, 0)
    centre_reference = mock_anchor(0, 0, 0)

    with pytest.raises(
        ValueError, match="`anchor` and `centre_reference` cannot be the same."
    ):
        _ = Mark(anchor, centre_reference)
