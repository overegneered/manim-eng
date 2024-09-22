import manim as mn
import pytest
from manim_eng import ManualWire, Wire
from manim_eng._base.terminal import Terminal


def test_wire_throws_value_error_if_terminals_are_identical() -> None:
    terminal = Terminal(mn.ORIGIN, mn.LEFT)

    with pytest.raises(
        ValueError,
        match=r"`from_terminal` and `to_terminal` are identical\. "
        r"Wires must have different terminals at each end\.",
    ):
        Wire(terminal, terminal)


def test_manual_wire_throws_value_error_if_terminals_are_identical() -> None:
    terminal = Terminal(mn.ORIGIN, mn.LEFT)

    with pytest.raises(
        ValueError,
        match=r"`from_terminal` and `to_terminal` are identical\. "
        r"Wires must have different terminals at each end\.",
    ):
        ManualWire(terminal, terminal, [])
