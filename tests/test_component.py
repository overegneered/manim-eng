import pytest
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

    assert dummy_component._label.tex_strings == [label]


def test_set_label_existing_label(dummy_component: Component) -> None:
    dummy_component.set_label("old")
    new_label_text = "new"

    dummy_component.set_label(new_label_text)

    assert dummy_component._label.tex_strings == [new_label_text]


def test_set_annotation_no_existing_annotation(dummy_component: Component) -> None:
    annotation = r"12 \Omega"

    dummy_component.set_annotation(annotation)

    assert dummy_component._annotation.tex_strings == [annotation]


def test_set_annotation_existing_annotation(dummy_component: Component) -> None:
    dummy_component.set_annotation("old")
    new_annotation_text = "new"

    dummy_component.set_annotation(new_annotation_text)

    assert dummy_component._annotation.tex_strings == [new_annotation_text]


def test_label_via_constructor_argument_works() -> None:
    dummy_component = DummyComponent(label="R")

    assert dummy_component._label.tex_strings == ["R"]


def test_annotation_via_constructor_argument_works() -> None:
    dummy_component = DummyComponent(annotation=r"12 \Omega")

    assert dummy_component._annotation.tex_strings == [r"12 \Omega"]


def test_label_and_annotation_via_constructor_argument_works() -> None:
    dummy_component = DummyComponent(label="Z", annotation=r"(2 + j4) \,\Omega")

    assert dummy_component._label.tex_strings == ["Z"]
    assert dummy_component._annotation.tex_strings == [r"(2 + j4) \,\Omega"]
