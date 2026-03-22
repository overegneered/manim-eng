import re

import manim as mn
import manim.typing as mnt
import numpy as np
import pytest

from manim_eng import config_eng
from manim_eng.circuits.node import Node
from manim_eng.components.base.component import Component
from manim_eng.components.base.monopole import Monopole

from .utils.dummy_component import DummyComponent


@pytest.mark.parametrize(
    ("direction", "expected_tip"),
    [
        pytest.param(
            None,
            np.array([1, 2, 0]) + config_eng.symbol.pin_length * mn.RIGHT,
            id="No direction specified takes component pin direction",
        ),
        pytest.param(
            mn.RIGHT,
            np.array([1, 2, 0]) + config_eng.symbol.pin_length * mn.RIGHT,
            id="Aligning in the x-direction",
        ),
        pytest.param(
            mn.UP,
            np.array([2, 0, 0]),
            id="Aligning in the y-direction",
        ),
        pytest.param(
            np.array([1, 1, 0]),
            np.array([0.7, 0.7, 0]),
            id="Aligning in the north-east direction",
        ),
    ],
)
def test_align_pins(
    dummy_component: Component,
    direction: mnt.Vector3D | None,
    expected_tip: mnt.Point3D,
) -> None:
    alignment_point = np.array([2, 2, 0])

    dummy_component.align_pin(
        dummy_component.right, alignment_point, direction=direction
    )

    assert np.allclose(dummy_component.right.tip, expected_tip)


def test_align_value_errors_if_pin_belongs_to_same_component(
    dummy_component: Component,
) -> None:
    with pytest.raises(
        ValueError,
        match=re.escape("Pin passed to `other` belongs to this component."),
    ):
        dummy_component.align_pin(dummy_component.right, dummy_component.right)


def test_align_value_errors_if_node_passed_itself() -> None:
    node = Node()
    with pytest.raises(
        ValueError,
        match=re.escape("Node passed to `other` is this component."),
    ):
        node.align_pin(node.right, node)


def test_align_value_errors_if_monopole_passed_itself() -> None:
    monopole = Monopole(mn.UP)
    with pytest.raises(
        ValueError,
        match=re.escape("Monopole passed to `other` is this component."),
    ):
        monopole.align_pin(monopole.pin, monopole)


def test_set_label_no_existing_label(dummy_component: Component) -> None:
    label = "R"

    dummy_component.label.set(label)

    assert dummy_component.label.tex_strings == [label]


def test_set_label_existing_label(dummy_component: Component) -> None:
    dummy_component.label.set("old")
    new_label_text = "new"

    dummy_component.label.set(new_label_text)

    assert dummy_component.label.tex_strings == [new_label_text]


def test_set_annotation_no_existing_annotation(dummy_component: Component) -> None:
    annotation = r"12 \Omega"

    dummy_component.annotation.set(annotation)

    assert dummy_component.annotation.tex_strings == [annotation]


def test_set_annotation_existing_annotation(dummy_component: Component) -> None:
    dummy_component.annotation.set("old")
    new_annotation_text = "new"

    dummy_component.annotation.set(new_annotation_text)

    assert dummy_component.annotation.tex_strings == [new_annotation_text]


def test_label_via_constructor_argument_works() -> None:
    dummy_component = DummyComponent(label="R")

    assert dummy_component.label.tex_strings == ["R"]


def test_annotation_via_constructor_argument_works() -> None:
    dummy_component = DummyComponent(annotation=r"12 \Omega")

    assert dummy_component.annotation.tex_strings == [r"12 \Omega"]


def test_label_and_annotation_via_constructor_argument_works() -> None:
    dummy_component = DummyComponent(label="Z", annotation=r"(2 + j4) \,\Omega")

    assert dummy_component.label.tex_strings == ["Z"]
    assert dummy_component.annotation.tex_strings == [r"(2 + j4) \,\Omega"]


def test_voltage_processes_pins_correctly(dummy_component: DummyComponent) -> None:
    voltage_1 = dummy_component.voltage(
        dummy_component.left,
        dummy_component.right,
        "V",
    )
    voltage_2 = dummy_component.voltage("left", dummy_component.right, "V")
    voltage_3 = dummy_component.voltage(dummy_component.left, "right", "V")
    voltage_4 = dummy_component.voltage("left", "right", "V")

    assert voltage_1.start == dummy_component.left
    assert voltage_1.end == dummy_component.right
    assert voltage_2.start == dummy_component.left
    assert voltage_2.end == dummy_component.right
    assert voltage_3.start == dummy_component.left
    assert voltage_3.end == dummy_component.right
    assert voltage_4.start == dummy_component.left
    assert voltage_4.end == dummy_component.right


def test_voltage_sets_component_it_is_called_on_as_avoid(
    dummy_component: DummyComponent,
) -> None:
    voltage = dummy_component.voltage("left", "right", "V")

    assert voltage.component_to_avoid == dummy_component


def test_voltage_errors_if_pins_are_the_same(
    dummy_component: DummyComponent,
) -> None:
    expected_message = (
        "The pins specified through `start` and `end` are the same. "
        "They must be different."
    )

    with pytest.raises(ValueError, match=expected_message):
        dummy_component.voltage(dummy_component.left, dummy_component.left)
    with pytest.raises(ValueError, match=expected_message):
        dummy_component.voltage("left", dummy_component.left)
    with pytest.raises(ValueError, match=expected_message):
        dummy_component.voltage(dummy_component.left, "left")
    with pytest.raises(ValueError, match=expected_message):
        dummy_component.voltage("left", "left")


def test_get_or_check_pin_non_belonging_pin() -> None:
    component = DummyComponent()
    other_component = DummyComponent()

    with pytest.raises(
        ValueError, match=re.escape("Passed pin does not belong to this component.")
    ):
        component._get_or_check_pin(other_component.left)


def test_get_or_check_pin_invalid_attribute(
    dummy_component: DummyComponent,
) -> None:
    with pytest.raises(AttributeError):
        dummy_component._get_or_check_pin("invalid_attribute")


def test_get_or_check_pin_valid_attribute_not_a_pin(
    dummy_component: DummyComponent,
) -> None:
    not_a_pin = "not_a_pin"

    with pytest.raises(
        ValueError,
        match=re.escape(f"Attribute `{not_a_pin}` of `DummyComponent` is not a pin."),
    ):
        dummy_component._get_or_check_pin(not_a_pin)


def test_get_or_check_pin_valid_pin(dummy_component: DummyComponent) -> None:
    result = dummy_component._get_or_check_pin(dummy_component.left)

    assert result == dummy_component.left


def test_get_or_check_pin_valid_string(dummy_component: DummyComponent) -> None:
    result = dummy_component._get_or_check_pin("left")

    assert result == dummy_component.left


def test_get_or_check_pin_pin_is_none(
    dummy_component: DummyComponent,
) -> None:
    result = dummy_component._get_or_check_pin(None)

    assert result == dummy_component.pins[0]


def test_align_pin_with_node_as_other_uses_node_center(
    dummy_component: DummyComponent,
) -> None:
    # Place a node at a known position and align the component's right pin to it.
    target_position = np.array([3.0, 1.0, 0.0])
    node = Node().move_to(target_position)

    dummy_component.align_pin(dummy_component.right, node)

    # After alignment, the right pin tip should lie on the line through the node
    # centre in the pin's direction (RIGHT). The component is moved perpendicular
    # to that direction (i.e. vertically) until the pin tip's y-coordinate matches
    # the node centre's y-coordinate.
    assert np.isclose(dummy_component.right.tip[1], node.get_center()[1], atol=1e-4)


def test_align_pin_with_monopole_as_other_uses_monopole_pin_tip(
    dummy_component: DummyComponent,
) -> None:
    # A Monopole facing UP has its pin tip above the origin.
    monopole = Monopole(mn.UP)
    monopole.move_to(np.array([2.0, 0.0, 0.0]))
    monopole_pin_tip = monopole.pin.tip.copy()

    # Align using the dummy component's right pin (facing RIGHT) towards the monopole.
    dummy_component.align_pin(dummy_component.right, monopole, direction=mn.UP)

    # The pin tip should be on the vertical line through the monopole's pin tip.
    assert np.isclose(dummy_component.right.tip[0], monopole_pin_tip[0], atol=1e-4)
