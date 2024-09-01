from typing import Any, Self

import manim as mn
import manim.typing as mnt
import numpy as np

from manim_eng._base.mark import Mark, Markable
from manim_eng._config import config_eng
from manim_eng._debug.anchor import Anchor
from manim_eng._utils import utils


class CurrentArrow(mn.Triangle):
    def __init__(self, position: mnt.Vector3D, rotation: float = 0) -> None:
        super().__init__(
            radius=config_eng.symbol.current_arrow_radius,
            start_angle=0,
            color=mn.WHITE,
            fill_color=mn.WHITE,
            fill_opacity=1,
        )
        self.move_to(position).rotate(rotation, about_point=position)


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
        start = position - (direction * config_eng.symbol.terminal_length)
        self.line = mn.Line(
            start=position,
            end=start,
            stroke_width=config_eng.symbol.wire_stroke_width,
        )
        self.add(self.line)

        self._centre_anchor: Anchor = Anchor(config_eng.anchor.centre_colour).move_to(
            self.line.get_center()
        )
        self._end_anchor: Anchor = Anchor(config_eng.anchor.terminal_colour).move_to(
            position
        )

        self._current_arrow: CurrentArrow
        self._current_arrow_showing: bool = False
        self._current_arrow_pointing_out: bool = False
        self.__rebuild_current_arrow()

        arrow_half_height = self._current_arrow.height / 2
        self._top_anchor = Anchor(config_eng.anchor.current_colour).move_to(
            self._centre_anchor.pos + np.array([0, arrow_half_height, 0])
        )
        self._bottom_anchor = Anchor(config_eng.anchor.current_colour).move_to(
            self._centre_anchor.pos + np.array([0, -arrow_half_height, 0])
        )

        self.add(
            self._centre_anchor, self._end_anchor, self._top_anchor, self._bottom_anchor
        )

        self._current: Mark = Mark(self._top_anchor, self._centre_anchor)
        self._current_mark_anchored_below: bool = False

    @property
    def direction(self) -> mnt.Vector3D:
        return utils.normalised(self._end_anchor.pos - self._centre_anchor.pos)

    @property
    def end(self) -> mnt.Point3D:
        return self._end_anchor.pos

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
            self.__rebuild_current_arrow()
            self.add(self._current_arrow)
            self._current_arrow_showing = True

        if out != self._current_arrow_pointing_out:
            self._current_arrow.rotate(mn.PI, about_point=self._centre_anchor.pos)
            self._current_arrow_pointing_out = out

        if below != self._current_mark_anchored_below:
            self._current.change_anchors(
                self._bottom_anchor if below else self._top_anchor,
                self._centre_anchor,
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

    def __rebuild_current_arrow(self) -> None:
        """Rebuild the current arrow.

        Useful after an Uncreate or a rotation when the arrow wasn't in the scene (and
        therefore wasn't rotated).
        """
        angle_to_rotate = mn.angle_of_vector(self.direction)
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
            self.__rebuild_current_arrow()
            self.add(self._current_arrow)
            self._current_arrow_showing = True
            if rotation_needed:
                self._current_arrow.rotate(mn.PI, about_point=self._centre_anchor.pos)
            self._current_arrow_pointing_out = out
            arrow_animation = mn.Create(self._current_arrow, **anim_args)
            animations.append(arrow_animation)

        elif rotation_needed:
            arrow_animation = mn.Rotate(
                self._current_arrow,
                mn.PI,
                about_point=self._centre_anchor.pos,
                **anim_args,
            )
            self._current_arrow_pointing_out = out
            animations.append(arrow_animation)

        if below != self._current_mark_anchored_below:
            self._current.change_anchors(
                self._bottom_anchor if below else self._top_anchor,
                self._centre_anchor,
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
