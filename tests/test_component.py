from unittest import mock

import manim as mn
import pytest
from manim_eng.components._component.component import Component
from manim_eng.components._component.mark import Mark


class DummyComponent(Component):
    def _construct(self) -> None:
        pass


@pytest.fixture()
def dummy_component() -> Component:
    return DummyComponent()


def test_set_label_no_existing_label(dummy_component: Component) -> None:
    label = "R"

    dummy_component.set_label(label)

    assert dummy_component._label.tex_strings == [label]
    assert dummy_component._marks.submobjects == [dummy_component._label]


def test_set_label_existing_label(dummy_component: Component) -> None:
    dummy_component._label = Mark(
        dummy_component._label_anchor, dummy_component._centre_anchor
    ).set_text("old")
    dummy_component._marks.submobjects = [dummy_component._label]
    new_label_text = "new"

    dummy_component.set_label(new_label_text)

    assert dummy_component._label.tex_strings == [new_label_text]
    assert dummy_component._marks.submobjects == [dummy_component._label]


def test_clear_label_label_exists(dummy_component: Component) -> None:
    dummy_component._label = Mark(
        dummy_component._label_anchor, dummy_component._centre_anchor
    ).set_text("old")
    dummy_component._marks.submobjects = [dummy_component._label]

    dummy_component.clear_label()

    assert dummy_component._marks.submobjects == []


def test_clear_label_label_does_not_exist(dummy_component: Component) -> None:
    dummy_component._marks.remove = mock.MagicMock(mn.VGroup)

    dummy_component.clear_label()

    assert dummy_component._marks.submobjects == []
    dummy_component._marks.remove.assert_not_called()


def test_set_annotation_no_existing_annotation(dummy_component: Component) -> None:
    annotation = r"12 \Omega"

    dummy_component.set_annotation(annotation)

    assert dummy_component._annotation.tex_strings == [annotation]
    assert dummy_component._marks.submobjects == [dummy_component._annotation]


def test_set_annotation_existing_annotation(dummy_component: Component) -> None:
    dummy_component._annotation = Mark(
        dummy_component._annotation_anchor, dummy_component._centre_anchor
    ).set_text("old")
    dummy_component._marks.submobjects = [dummy_component._annotation]
    new_annotation_text = "new"

    dummy_component.set_annotation(new_annotation_text)

    assert dummy_component._annotation.tex_strings == [new_annotation_text]
    assert dummy_component._marks.submobjects == [dummy_component._annotation]


def test_clear_annotation_annotation_exists(dummy_component: Component) -> None:
    dummy_component._annotation = Mark(
        dummy_component._annotation_anchor, dummy_component._centre_anchor
    ).set_text("old")
    dummy_component._marks.submobjects = [dummy_component._annotation]

    dummy_component.clear_annotation()

    assert dummy_component._marks.submobjects == []


def test_clear_annotation_annotation_does_not_exist(dummy_component: Component) -> None:
    dummy_component._marks.remove = mock.MagicMock(mn.VGroup)

    dummy_component.clear_annotation()

    assert dummy_component._marks.submobjects == []
    dummy_component._marks.remove.assert_not_called()


def test_label_via_constructor_argument_works() -> None:
    dummy_component = DummyComponent(label="R")

    assert dummy_component._label.tex_strings == ["R"]
    assert dummy_component._marks.submobjects == [dummy_component._label]


def test_annotation_via_constructor_argument_works() -> None:
    dummy_component = DummyComponent(annotation=r"12 \Omega")

    assert dummy_component._annotation.tex_strings == [r"12 \Omega"]
    assert dummy_component._marks.submobjects == [dummy_component._annotation]


def test_label_and_annotation_via_constructor_argument_works() -> None:
    dummy_component = DummyComponent(label="Z", annotation=r"(2 + j4) \,\Omega")

    assert dummy_component._label.tex_strings == ["Z"]
    assert dummy_component._annotation.tex_strings == [r"(2 + j4) \,\Omega"]
    # Using a set means that order doesn't matter. We only care that it is exactly these
    # two objects in _marks, we don't care what order they're in.
    assert set(dummy_component._marks.submobjects) == {
        dummy_component._label,
        dummy_component._annotation,
    }


def test_supplying_neither_label_nor_annotation_via_constructor_argument_does_nothing(
    dummy_component: DummyComponent,
) -> None:
    assert len(dummy_component._marks.submobjects) == 0
