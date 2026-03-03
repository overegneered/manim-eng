"""Utility components (buzzers, microphones, lamps, fuses, etc.)."""

from typing import Any

import manim as mn
import numpy as np

from manim_eng import config_eng
from manim_eng.components import node
from manim_eng.components.base.bipole import BiasedBipole, Bipole, SquareBipole
from manim_eng.components.base.monopole import Monopole
from manim_eng.components.base.terminal import Terminal


class Lamp(SquareBipole):
    """Circuit symbol for lamps."""

    def _construct(self) -> None:
        super()._construct()
        inv_sqrt_2 = 1 / np.sqrt(2)
        half_width = 0.5 * config_eng.symbol.square_bipole_side_length
        circle = mn.Circle(half_width).match_style(self)
        line1 = mn.Line(
            half_width * inv_sqrt_2 * (mn.UP + mn.LEFT),
            half_width * inv_sqrt_2 * (mn.DOWN + mn.RIGHT),
        ).match_style(self)
        line2 = mn.Line(
            half_width * inv_sqrt_2 * (mn.UP + mn.RIGHT),
            half_width * inv_sqrt_2 * (mn.DOWN + mn.LEFT),
        ).match_style(self)
        self._body.add(circle, line1, line2)


class Bell(BiasedBipole):
    """Circuit symbol for bells."""

    def _construct(self) -> None:
        super()._construct()
        half_width = 0.5 * config_eng.symbol.biased_bipole_width
        height = config_eng.symbol.biased_bipole_height
        line1 = mn.Line(
            np.array([-half_width, height - half_width, 0.0]),
            np.array([half_width, height - half_width, 0.0]),
        ).match_style(self)
        arc1 = mn.Arc(
            half_width, 0, mn.PI, arc_center=np.array([0.0, height - half_width, 0.0])
        ).match_style(self)
        wire = mn.VMobject()
        wire.start_new_path(half_width * mn.LEFT)
        wire.add_line_to(0.5 * half_width * mn.LEFT)
        wire.add_line_to(0.5 * half_width * mn.LEFT + (height - half_width) * mn.UP)
        wire.start_new_path(half_width * mn.RIGHT)
        wire.add_line_to(0.5 * half_width * mn.RIGHT)
        wire.add_line_to(0.5 * half_width * mn.RIGHT + (height - half_width) * mn.UP)
        wire.match_style(self)
        self._body.add(line1, arc1, wire)


class Buzzer(BiasedBipole):
    """Circuit symbol for buzzers."""

    def _construct(self) -> None:
        super()._construct()
        sqrt3_over_2 = np.sqrt(3) / 2
        half_width = 0.5 * config_eng.symbol.biased_bipole_width
        height = config_eng.symbol.biased_bipole_height
        line1 = mn.Line(
            np.array([-half_width, height, 0.0]), np.array([half_width, height, 0.0])
        ).match_style(self)
        arc1 = mn.Arc(
            half_width, -mn.PI, mn.PI, arc_center=np.array([0.0, height, 0.0])
        ).match_style(self)
        wire = mn.VMobject()
        wire.start_new_path(half_width * mn.LEFT)
        wire.add_line_to(0.5 * half_width * mn.LEFT)
        wire.add_line_to(
            0.5 * half_width * mn.LEFT + (height - sqrt3_over_2 * half_width) * mn.UP
        )
        wire.start_new_path(half_width * mn.RIGHT)
        wire.add_line_to(0.5 * half_width * mn.RIGHT)
        wire.add_line_to(
            0.5 * half_width * mn.RIGHT + (height - sqrt3_over_2 * half_width) * mn.UP
        )
        wire.match_style(self)
        self._body.add(line1, arc1, wire)


class Speaker(BiasedBipole):
    """Circuit symbol for speakers."""

    def __init__(self) -> None:
        half_bottom_width = 0.4 * config_eng.symbol.biased_bipole_width
        super().__init__(
            left=Terminal(position=half_bottom_width * mn.LEFT, direction=mn.LEFT),
            right=Terminal(position=half_bottom_width * mn.RIGHT, direction=mn.RIGHT),
        )

    def _construct(self) -> None:
        super()._construct()
        bottom_width = 0.8 * config_eng.symbol.biased_bipole_width
        height = config_eng.symbol.biased_bipole_height

        rectangle = mn.Rectangle(width=bottom_width, height=0.5 * height).match_style(
            self
        )

        path = mn.VMobject()
        path.start_new_path(0.5 * bottom_width * mn.LEFT + 0.25 * height * mn.UP)
        path.add_line_to(bottom_width * mn.LEFT + 0.75 * height * mn.UP)
        path.add_line_to(bottom_width * mn.RIGHT + 0.75 * height * mn.UP)
        path.add_line_to(0.5 * bottom_width * mn.RIGHT + 0.25 * height * mn.UP)
        path.match_style(self)

        self._body.add(rectangle, path)


class Microphone(SquareBipole):
    """Circuit symbol for microphones."""

    def _construct(self) -> None:
        super()._construct()
        half_width = 0.5 * config_eng.symbol.square_bipole_side_length
        circle = mn.Circle(half_width).match_style(self)
        # slightly extend the line to make it more visually appealing
        line = mn.Line(
            np.array([-1.1 * half_width, half_width, 0.0]),
            np.array([1.1 * half_width, half_width, 0.0]),
        )
        self._body.add(circle, line)


class Fuse(Bipole):
    """Circuit symbol for fuses."""

    def _construct(self) -> None:
        super()._construct()
        width = config_eng.symbol.bipole_width
        height = config_eng.symbol.bipole_height
        if config_eng.symbol.fuse_standard == "ANSI":
            # Draw two nodes and two arcs
            arc1 = mn.Arc(
                0.25 * width, 0, mn.PI, arc_center=0.25 * width * mn.LEFT
            ).match_style(self)
            arc2 = mn.Arc(
                0.25 * width, -mn.PI, mn.PI, arc_center=0.25 * width * mn.RIGHT
            ).match_style(self)
            left_node = node._create_node_blob(self, open_=True).move_to(
                0.5 * width * mn.LEFT
            )
            right_node = node._create_node_blob(self, open_=True).move_to(
                0.5 * width * mn.RIGHT
            )
            self._body.add(arc1, arc2, left_node, right_node)
        else:
            # IEC standard. Draw a box with two vertical lines near each end.
            box = mn.Rectangle(width=width, height=height).match_style(self)
            line1 = mn.Line(
                np.array([-0.35 * width, 0.5 * height, 0.0]),
                np.array([-0.35 * width, -0.5 * height, 0.0]),
            )
            line2 = mn.Line(
                np.array([0.35 * width, 0.5 * height, 0.0]),
                np.array([0.35 * width, -0.5 * height, 0.0]),
            )
            self._body.add(box, line1, line2)


class Antenna(Monopole):
    """Circuit symbol for antennae."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(direction=mn.DOWN, **kwargs)

    def _construct(self) -> None:
        super()._construct()

        half_width = 0.5 * config_eng.symbol.monopole_width
        height = config_eng.symbol.monopole_width

        line1 = mn.Line(mn.ORIGIN, height * mn.UP)
        line2 = mn.Line(0.3 * height * mn.UP, half_width * mn.LEFT + height * mn.UP)
        line3 = mn.Line(0.3 * height * mn.UP, half_width * mn.RIGHT + height * mn.UP)
        self._body.add(line1, line2, line3)
