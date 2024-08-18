from unittest import mock

import manim as mn
import numpy as np
import pytest
from manim_eng.components._component import MARK_FONT_SIZE
from manim_eng.components._component.component import Component


class DummyComponent(Component):
    def _construct(self) -> None:
        pass


@pytest.fixture()
def dummy_component() -> Component:
    return DummyComponent()


def test_set_label_no_existing_label(dummy_component: Component) -> None:
    label = "R"

    dummy_component.set_label(label)

    assert dummy_component._label is not None
    assert dummy_component._label.tex_string == label
    assert dummy_component._marks.submobjects == [dummy_component._label]
    assert np.isclose(dummy_component._label.font_size, MARK_FONT_SIZE)


def test_set_label_existing_label(dummy_component: Component) -> None:
    dummy_component._label = mn.MathTex("old")
    dummy_component._marks.submobjects = [dummy_component._label]
    new_label_text = "new"

    dummy_component.set_label(new_label_text)

    assert dummy_component._label is not None
    assert dummy_component._label.tex_string == new_label_text
    assert dummy_component._marks.submobjects == [dummy_component._label]
    assert np.isclose(dummy_component._label.font_size, MARK_FONT_SIZE)


def test_clear_label_label_exists(dummy_component: Component) -> None:
    dummy_component._label = mn.MathTex("old")
    dummy_component._marks.submobjects = [dummy_component._label]

    dummy_component.clear_label()

    assert dummy_component._label is None
    assert dummy_component._marks.submobjects == []


def test_clear_label_label_does_not_exist(dummy_component: Component) -> None:
    dummy_component._marks.remove = mock.MagicMock(mn.VGroup)

    dummy_component.clear_label()

    assert dummy_component._label is None
    assert dummy_component._marks.submobjects == []
    dummy_component._marks.remove.assert_not_called()


def test_set_annotation_no_existing_annotation(dummy_component: Component) -> None:
    annotation = r"12 \Omega"

    dummy_component.set_annotation(annotation)

    assert dummy_component._annotation is not None
    assert dummy_component._annotation.tex_string == annotation
    assert dummy_component._marks.submobjects == [dummy_component._annotation]
    assert np.isclose(dummy_component._annotation.font_size, MARK_FONT_SIZE)


def test_set_annotation_existing_annotation(dummy_component: Component) -> None:
    dummy_component._annotation = mn.MathTex("old")
    dummy_component._marks.submobjects = [dummy_component._annotation]
    new_annotation_text = "new"

    dummy_component.set_annotation(new_annotation_text)

    assert dummy_component._annotation is not None
    assert dummy_component._annotation.tex_string == new_annotation_text
    assert dummy_component._marks.submobjects == [dummy_component._annotation]
    assert np.isclose(dummy_component._annotation.font_size, MARK_FONT_SIZE)


def test_clear_annotation_annotation_exists(dummy_component: Component) -> None:
    dummy_component._annotation = mn.MathTex("old")
    dummy_component._marks.submobjects = [dummy_component._annotation]

    dummy_component.clear_annotation()

    assert dummy_component._annotation is None
    assert dummy_component._marks.submobjects == []


def test_clear_annotation_annotation_does_not_exist(dummy_component: Component) -> None:
    dummy_component._marks.remove = mock.MagicMock(mn.VGroup)

    dummy_component.clear_annotation()

    assert dummy_component._annotation is None
    assert dummy_component._marks.submobjects == []
    dummy_component._marks.remove.assert_not_called()


def test_label_via_constructor_argument_works() -> None:
    dummy_component = DummyComponent(label="R")

    assert dummy_component._label is not None
    assert dummy_component._label.tex_string == "R"
    assert dummy_component._marks.submobjects == [dummy_component._label]
    assert np.isclose(dummy_component._label.font_size, MARK_FONT_SIZE)


def test_annotation_via_constructor_argument_works() -> None:
    dummy_component = DummyComponent(annotation=r"12 \Omega")

    assert dummy_component._annotation is not None
    assert dummy_component._annotation.tex_string == r"12 \Omega"
    assert dummy_component._marks.submobjects == [dummy_component._annotation]
    assert np.isclose(dummy_component._annotation.font_size, MARK_FONT_SIZE)


def test_label_and_annotation_via_constructor_argument_works() -> None:
    dummy_component = DummyComponent(label="Z", annotation=r"(2 + j4) \,\Omega")

    assert dummy_component._label is not None
    assert dummy_component._annotation is not None
    assert dummy_component._label.tex_string == "Z"
    assert dummy_component._annotation.tex_string == r"(2 + j4) \,\Omega"
    # Using a set means that order doesn't matter. We only care that it is exactly these
    # two objects in _marks, we don't care what order they're in.
    assert set(dummy_component._marks.submobjects) == {
        dummy_component._label,
        dummy_component._annotation,
    }
    assert np.isclose(dummy_component._label.font_size, MARK_FONT_SIZE)
    assert np.isclose(dummy_component._annotation.font_size, MARK_FONT_SIZE)


def test_supplying_neither_label_nor_annotation_via_constructor_argument_does_nothing(
    dummy_component: DummyComponent,
) -> None:
    assert dummy_component._label is None
    assert dummy_component._annotation is None
    assert len(dummy_component._marks.submobjects) == 0
