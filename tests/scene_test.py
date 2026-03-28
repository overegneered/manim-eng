from unittest import mock

import manim as mn
import pytest

from manim_eng import EngScene, Wire
from manim_eng.circuits.base import WireBase
from manim_eng.circuits.circuit import Circuit

from .utils.dummy_component import DummyComponent
from .utils.pin_mocked_parent import PinMockedParent


@pytest.fixture
def scene(monkeypatch: pytest.MonkeyPatch) -> EngScene:
    monkeypatch.setattr(mn.config, "renderer", mn.RendererType.CAIRO)
    return EngScene(renderer=mn.CairoRenderer())


def test_add_wire_marks_wire_visible(scene: EngScene, wire: Wire) -> None:
    scene.add(wire)

    assert wire.is_visible() is True


def test_add_previously_hidden_wire_marks_wire_visible(
    scene: EngScene, wire: Wire
) -> None:
    wire._set_hidden()

    scene.add(wire)

    assert wire.is_visible() is True


def test_add_non_wire_mobject_does_not_crash(scene: EngScene) -> None:
    mob = mn.VMobject()

    scene.add(mob)


def test_add_mixed_mobjects_marks_only_wires_visible(
    scene: EngScene, wire: Wire
) -> None:
    mob = mn.VMobject()
    wire._set_hidden()

    scene.add(wire, mob)

    assert wire.is_visible() is True


def test_add_returns_self(scene: EngScene, wire: Wire) -> None:
    result = scene.add(wire)

    assert result is scene


def test_remove_wire_marks_wire_hidden(scene: EngScene, wire: Wire) -> None:
    scene.add(wire)

    scene.remove(wire)

    assert wire.is_visible() is False


def test_remove_non_wire_mobject_does_not_crash(scene: EngScene) -> None:
    mob = mn.VMobject()
    scene.add(mob)

    scene.remove(mob)


def test_remove_mixed_mobjects_marks_only_wires_hidden(
    scene: EngScene, wire: Wire
) -> None:
    mob = mn.VMobject()
    scene.add(wire, mob)

    scene.remove(wire, mob)

    assert wire.is_visible() is False


def test_remove_returns_self(scene: EngScene, wire: Wire) -> None:
    scene.add(wire)

    result = scene.remove(wire)

    assert result is scene


def test_bring_to_back_wire_keeps_wire_visible(scene: EngScene, wire: Wire) -> None:
    # bring_to_back calls remove() internally; without the override this would
    # leave the wire marked hidden even though it is still on screen.
    scene.add(wire)

    scene.bring_to_back(wire)

    assert wire.is_visible() is True


def test_bring_to_back_non_wire_does_not_crash(scene: EngScene) -> None:
    mob = mn.VMobject()
    scene.add(mob)

    scene.bring_to_back(mob)


def test_clear_wire_in_mobjects_marks_wire_hidden(scene: EngScene, wire: Wire) -> None:
    scene.add(wire)

    scene.clear()

    assert wire.is_visible() is False


def test_clear_wire_in_foreground_marks_wire_hidden(
    scene: EngScene, wire: Wire
) -> None:
    # Tests the foreground_mobjects path -- this catches the extend() -> None bug.
    scene.add_foreground_mobjects(wire)
    wire._set_visible()

    scene.clear()

    assert wire.is_visible() is False


def test_clear_empty_scene_does_not_crash(scene: EngScene) -> None:
    scene.clear()


def test_clear_returns_self(scene: EngScene) -> None:
    result = scene.clear()

    assert result is scene


def test_replace_old_wire_marks_wire_hidden(scene: EngScene, wire: Wire) -> None:
    replacement = mn.VMobject()
    scene.add(wire)

    scene.replace(wire, replacement)

    assert wire.is_visible() is False


def test_replace_with_new_wire_marks_wire_visible(scene: EngScene, wire: Wire) -> None:
    placeholder = mn.VMobject()
    scene.add(placeholder)

    scene.replace(placeholder, wire)

    assert wire.is_visible() is True


def test_replace_wire_with_wire_old_hidden_new_visible(scene: EngScene) -> None:
    start_a = PinMockedParent(mn.LEFT * 2, mn.LEFT)
    end_a = PinMockedParent(mn.RIGHT * 2, mn.RIGHT)
    wire_a = Wire(start_a, end_a)

    start_b = PinMockedParent(mn.LEFT * 3, mn.LEFT)
    end_b = PinMockedParent(mn.RIGHT * 3, mn.RIGHT)
    wire_b = Wire(start_b, end_b)

    scene.add(wire_a)

    scene.replace(wire_a, wire_b)

    assert wire_a.is_visible() is False
    assert wire_b.is_visible() is True


def test_replace_non_wire_with_non_wire_does_not_crash(scene: EngScene) -> None:
    mob_a = mn.VMobject()
    mob_b = mn.VMobject()
    scene.add(mob_a)

    scene.replace(mob_a, mob_b)


def test_restructure_mobjects_marks_wire_hidden(scene: EngScene, wire: Wire) -> None:
    scene.add(wire)

    scene.restructure_mobjects([wire])

    assert wire.is_visible() is False


def test_restructure_mobjects_non_wire_does_not_crash(scene: EngScene) -> None:
    mob = mn.VMobject()
    scene.add(mob)

    scene.restructure_mobjects([mob])


def test_restructure_mobjects_returns_self(scene: EngScene, wire: Wire) -> None:
    scene.add(wire)

    result = scene.restructure_mobjects([wire])

    assert result is scene


def test_restructure_mobjects_extract_families_false_marks_wire_hidden(
    scene: EngScene, wire: Wire
) -> None:
    # When extract_families=False is passed, __set_visibility still uses
    # get_family() internally, so wires in to_remove are still discovered and
    # marked hidden correctly.
    scene.add(wire)

    scene.restructure_mobjects([wire], extract_families=False)

    assert wire.is_visible() is False


def test_add_wire_triggers_update_mobjects(scene: EngScene, wire: Wire) -> None:
    with mock.patch.object(scene, "update_mobjects") as patched:
        scene.add(wire)

    # Manim's own add() may also call update_mobjects; we only assert our code
    # triggered at least one call with (0).
    patched.assert_called_with(0)


def test_remove_wire_triggers_update_mobjects(scene: EngScene, wire: Wire) -> None:
    scene.add(wire)

    with mock.patch.object(scene, "update_mobjects") as patched:
        scene.remove(wire)

    # Manim's own remove() may also call update_mobjects; we only assert our
    # code triggered at least one call with (0).
    patched.assert_called_with(0)


def test_add_non_wire_does_not_trigger_update_mobjects(scene: EngScene) -> None:
    mob = mn.VMobject()

    with mock.patch.object(scene, "update_mobjects") as patched:
        scene.add(mob)

    patched.assert_not_called()


def test_add_vgroup_containing_wire_marks_nested_wire_visible(
    scene: EngScene, wire: Wire
) -> None:
    # __set_visibility uses get_family() to recurse into submobjects, so wires
    # nested inside a VGroup are discovered and marked visible.
    wire._set_hidden()
    group = mn.VGroup(wire)

    scene.add(group)

    assert wire.is_visible() is True


def test_bring_to_front_wire_keeps_wire_visible(scene: EngScene, wire: Wire) -> None:
    # bring_to_front calls self.add() internally, which routes through EngScene.add.
    scene.add(wire)

    scene.bring_to_front(wire)

    assert wire.is_visible() is True


def test_add_foreground_mobjects_marks_wire_visible(
    scene: EngScene, wire: Wire
) -> None:
    # add_foreground_mobjects calls self.add() internally, so the override fires.
    wire._set_hidden()

    scene.add_foreground_mobjects(wire)

    assert wire.is_visible() is True


def test_add_foreground_mobject_marks_wire_visible(scene: EngScene, wire: Wire) -> None:
    # Single-argument form — same routing through EngScene.add.
    wire._set_hidden()

    scene.add_foreground_mobject(wire)

    assert wire.is_visible() is True


def test_remove_foreground_mobjects_wire_still_in_mobjects_stays_visible(
    scene: EngScene, wire: Wire
) -> None:
    # add_foreground_mobjects puts the wire in both self.mobjects and
    # self.foreground_mobjects.  Demoting it from the foreground should not mark
    # it hidden because it is still present in self.mobjects and on screen.
    scene.add_foreground_mobjects(wire)

    scene.remove_foreground_mobjects(wire)

    assert wire.is_visible() is True


def test_remove_foreground_mobject_wire_still_in_mobjects_stays_visible(
    scene: EngScene, wire: Wire
) -> None:
    # Single-argument form of the same scenario.
    scene.add_foreground_mobjects(wire)

    scene.remove_foreground_mobject(wire)

    assert wire.is_visible() is True


def test_remove_foreground_mobjects_wire_not_in_mobjects_marks_wire_hidden(
    scene: EngScene, wire: Wire
) -> None:
    # Wire is in foreground_mobjects only (not self.mobjects). After removal from
    # the foreground list it is no longer on screen so it should be marked hidden.
    # We bypass EngScene.add to avoid it ending up in self.mobjects.
    scene.foreground_mobjects.append(wire)
    wire._set_visible()

    scene.remove_foreground_mobjects(wire)

    assert wire.is_visible() is False


def test_add_circuit_marks_nested_wires_visible(scene: EngScene) -> None:
    # __set_visibility recurses into submobjects via get_family(), so wires
    # nested inside a Circuit are discovered and marked visible.
    component_1 = DummyComponent()
    component_2 = DummyComponent()
    circuit = Circuit(component_1, component_2)
    circuit.connect(component_1.right, component_2.left)

    nested_wire = circuit.wires.submobjects[0]
    assert isinstance(nested_wire, WireBase)

    # Force hidden so we can assert add() makes it visible.
    nested_wire._set_hidden()
    scene.add(circuit)

    assert nested_wire.is_visible() is True
