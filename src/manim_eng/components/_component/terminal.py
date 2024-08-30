from typing import Any, Self

import manim as mn
import manim.typing as mnt
import numpy as np

from ..._config import config_eng
from ..._debug.anchor import Anchor
from .mark import Mark, Markable


class CurrentArrow(mn.Triangle):
    def __init__(self, position: mnt.Vector3D, rotation: float = 0) -> None:
        super().__init__(
            radius=config_eng.symbol.current_arrow_radius,
            start_angle=rotation,
            color=mn.WHITE,
            fill_color=mn.WHITE,
            fill_opacity=1,
        )
        self.move_to(position)


class Terminal(Markable):
    """Terminal for a circuit component.

    Parameters
    ----------
    position : Vector3D
        The position of the *end* of the terminal, i.e. the bit that other components or
        wires would attach to.
    direction : Vector3D
        The direction the terminal 'points', i.e. the direction you get by walking from
        the point on the component body where the terminal attaches to the end of the
        terminal.
    """

    def __init__(self, position: mnt.Vector3D, direction: mnt.Vector3D) -> None:
        super().__init__()

        direction /= np.linalg.norm(direction)
        end = position - (direction * config_eng.symbol.terminal_length)
        self.line = mn.Line(
            start=position,
            end=end,
            stroke_width=config_eng.symbol.wire_stroke_width,
        )
        self.add(self.line)

        self.position = position
        self.direction = direction

        self._current_anchor: Anchor = Anchor(config_eng.anchor.current_colour)
        self._centre_anchor: Anchor = Anchor(config_eng.anchor.centre_colour).move_to(
            self.get_center()
        )

        self._current_arrow: CurrentArrow
        self._current_arrow_showing: bool = False
        self._current_arrow_pointing_out: bool = False
        # Set to true so that the `__rebuild_current_arrow_if_necessary()` will rebuild
        # the arrow (in this case, initialise it)
        self._current_arrow_uncreated: bool = True
        self.__rebuild_current_arrow_if_necessary()

        self._current_anchor.move_to(self._current_arrow.get_top())
        self._current_mark_anchored_below: bool = False

        self._current: Mark = Mark(self._current_anchor, self._centre_anchor)

        self.add(self._centre_anchor, self._current_anchor)

    def set_current(self, label: str, out: bool = False, below: bool = False) -> Self:
        """Set the current annotation of the terminal.

        Parameters
        ----------
        label : str
            The current label to set. Takes a TeX math mode string.
        out : bool
            Whether the arrow accompanying the annotation should point out (away from
            the body of the component to which the terminal is attached), or in (towards
            the component, this is the default).
        below : bool
            Whether the annotation should be placed below the current arrow, or above it
            (which is the default). Note that 'below' here is for when the component is
            unrotated.

        Returns
        -------
        Self
            The (modified) terminal on which the method was called.
        """
        if not self._current_arrow_showing:
            self.__rebuild_current_arrow_if_necessary()
            self.add(self._current_arrow)
            self._current_arrow_showing = True

        if out != self._current_arrow_pointing_out:
            self._current_arrow.rotate(mn.PI)
            self._current_arrow_pointing_out = out

        if below != self._current_mark_anchored_below:
            self._current_anchor.move_to(
                self._current_arrow.get_bottom()
                if below
                else self._current_arrow.get_top()
            )
            self._current_mark_anchored_below = below

        self._set_mark(self._current, label)
        return self

    def clear_current(self) -> Self:
        """Clear the current annotation of the terminal.

        Returns
        -------
        Self
            The (modified) terminal on which the method was called.
        """
        self.remove(self._current_arrow)
        self._current_arrow_showing = False
        self._clear_mark(self._current)
        return self

    def __rebuild_current_arrow_if_necessary(self) -> None:
        if self._current_arrow_uncreated:
            angle_to_rotate = np.arccos(np.dot(self.direction, np.array([1, 0, 0])))
            if not self._current_arrow_pointing_out:
                angle_to_rotate += np.pi
            self._current_arrow = CurrentArrow(self._centre_anchor.pos, angle_to_rotate)
            self._current_arrow_uncreated = False

    @mn.override_animate(set_current)
    def __animate_set_current(
        self,
        label: str,
        out: bool = False,
        below: bool = False,
        anim_args: dict[str, Any] | None = None,
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}

        animations: list[mn.Animation] = []

        rotation_needed = out != self._current_arrow_pointing_out

        if not self._current_arrow_showing:
            self.__rebuild_current_arrow_if_necessary()
            self.add(self._current_arrow)
            self._current_arrow_showing = True
            if rotation_needed:
                self._current_arrow.rotate(mn.PI)
            self._current_arrow_pointing_out = out
            arrow_animation = mn.Create(self._current_arrow, **anim_args)
            animations.append(arrow_animation)

        elif rotation_needed:
            arrow_animation = mn.Rotate(self._current_arrow, mn.PI, **anim_args)
            self._current_arrow_pointing_out = out
            animations.append(arrow_animation)

        if below != self._current_mark_anchored_below:
            self._current_anchor.move_to(
                self._current_arrow.get_bottom()
                if below
                else self._current_arrow.get_top()
            )
            self._current_mark_anchored_below = below

        label_animation = (
            self.animate(**anim_args)._set_mark(self._current, label).build()
        )
        animations.append(label_animation)

        return mn.AnimationGroup(*animations)

    @mn.override_animate(clear_current)
    def __animate_clear_current(
        self, anim_args: dict[str, Any] | None = None
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}

        arrow_animation = mn.Uncreate(self._current_arrow, *anim_args)
        self._current_arrow_showing = False
        self._current_arrow_uncreated = True

        return mn.AnimationGroup(
            arrow_animation,
            self.animate(**anim_args)._clear_mark(self._current).build(),
        )
