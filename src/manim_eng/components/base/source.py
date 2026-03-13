"""Base classes for creating sources."""

import abc
from typing import Any, Self

import manim as mn
import numpy as np

from manim_eng import config_eng
from manim_eng.components.base.bipole import SquareBipole
from manim_eng.components.base.terminal import Terminal

__all__ = [
    "CurrentSourceBase",
    "EuropeanCurrentSourceBase",
    "EuropeanVoltageSourceBase",
    "Source",
    "VoltageSourceBase",
]


class Source(SquareBipole, metaclass=abc.ABCMeta):
    """Base class of all sources."""

    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            **kwargs,
        )

    @property
    def negative(self) -> Terminal:
        """Return the negative (left-hand) terminal of the source."""
        return self.left

    @property
    def positive(self) -> Terminal:
        """Return the positive (right-hand) terminal of the source."""
        return self.right

    @property
    def anode(self) -> Terminal:
        """Return the anode (positive terminal) of the source."""
        return self.positive

    @property
    def cathode(self) -> Terminal:
        """Return the cathode (negative terminal) of the source."""
        return self.negative


class VoltageSourceBase(Source, metaclass=abc.ABCMeta):
    """Base class of all voltage sources."""

    def __init__(self, arrow: bool, voltage: str | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.should_arrow = arrow
        self.__arrow: mn.Arrow | None = None

        if voltage is not None:
            self.set_voltage(voltage)

    def set_voltage(self, voltage: str) -> Self:
        """Set the voltage of the source.

        Sets the voltage label of the source, using the label of the component to do so.
        For non-arrowed (American-style) sources there is no difference between using
        this and using `.set_label()`, however for arrowed sources an arrow is added
        only when calling this method. For portability between source types it is
        therefore recommended to use this method over `.set_label()`.

        Parameters
        ----------
        voltage : str
            The voltage label to set. Takes a TeX math mode string.
        """
        if self.should_arrow and self.__arrow is None:
            self.__construct_arrow()
        self.set_label(voltage)
        return self

    def clear_voltage(self) -> Self:
        """Clear the voltage label of the source.

        Clears the voltage label of the source (i.e. the label of the component). For
        non-arrowed (American-style) sources there is no difference between using this
        and using `.clear_label()`, however for European sources the arrow is removed
        only when calling this method. For portability between source types it is
        therefore recommended to use this method over `.clear_label()`.
        """
        if self.should_arrow:
            self.__clear_arrow()
        self.clear_label()
        return self

    def __construct_arrow(self) -> None:
        half_side_length = config_eng.symbol.square_bipole_side_length / 2

        direction_to_label_anchor = mn.normalize(
            self._label_anchor.pos - self._centre_anchor.pos
        )
        arrow_midpoint_distance = 1.4 * half_side_length
        arrow_midpoint = (
            self._centre_anchor.pos
            + direction_to_label_anchor * arrow_midpoint_distance
        )
        arrow_half_length = 0.9 * half_side_length
        arrow_direction = np.cross(direction_to_label_anchor, mn.OUT)

        self.__arrow = mn.Arrow(
            start=arrow_midpoint - arrow_half_length * arrow_direction,
            end=arrow_midpoint + arrow_half_length * arrow_direction,
            tip_length=config_eng.symbol.arrow_tip_length,
            buff=0,
        ).match_style(self)
        self._label_anchor.move_to(arrow_midpoint)
        self._body.add(self.__arrow)

    def __clear_arrow(self) -> None:
        # It's unnecessary to move the label anchor to its original position, as the
        # next setting of the label will only put it back where it is now
        self._body.remove(self.__arrow)
        self.__arrow = None

    @mn.override_animate(set_voltage)
    def __animate_set_voltage(
        self, label: str, anim_args: dict[str, Any] | None = None
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}

        label_animation = self.animate(**anim_args).set_label(label).build()
        animations = [label_animation]

        if self.should_arrow and self.__arrow is None:
            self.__construct_arrow()
            arrow_animation = mn.Create(self.__arrow, **anim_args)
            animations.append(arrow_animation)

        return mn.AnimationGroup(*animations)

    @mn.override_animate(clear_voltage)
    def __animate_clear_voltage(
        self, anim_args: dict[str, Any] | None = None
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}

        label_animation = self.animate(**anim_args).clear_label().build()
        animations = [label_animation]

        if self.should_arrow and self.__arrow is not None:
            arrow_animation = mn.Uncreate(self.__arrow, **anim_args)
            animations.append(arrow_animation)
        self.__clear_arrow()

        return mn.AnimationGroup(*animations)


class EuropeanVoltageSourceBase(VoltageSourceBase, metaclass=abc.ABCMeta):
    """Base class for all European voltage sources.

    Designed to be used in conjunction with the ``RoundOuter`` and ``DiamondOuter``
    modifiers, to produce standard and controlled sources.

    Parameters
    ----------
    voltage : str | None
        The voltage label to set initially. Takes a TeX math mode string.

    See Also
    --------
    modifiers.RoundOuter
    modifiers.DiamondOuter
    """

    def __init__(self, voltage: str | None = None, **kwargs: Any) -> None:
        super().__init__(arrow=True, voltage=voltage, **kwargs)

    def _construct(self) -> None:
        super()._construct()
        half_width = config_eng.symbol.square_bipole_side_length / 2
        self._body.add(
            mn.Line(
                start=mn.LEFT * half_width,
                end=mn.RIGHT * half_width,
                z_index=self.z_index + 0.1,
            ).match_style(self)
        )


class DCSourceBase(VoltageSourceBase):
    """Circuit symbol for a US-style direct-current source."""

    def __init__(self, voltage: str | None = None, **kwargs: Any) -> None:
        super().__init__(arrow=True, voltage=voltage, **kwargs)

    def _construct(self) -> None:
        super()._construct()
        plus = (
            mn.Text("+", font_size=config_eng.symbol.terminal_name_font_size)
            .match_style(self)
            .next_to(self.left, mn.RIGHT, buff=config_eng.symbol.terminal_name_buff)
        )
        minus = (
            mn.Text("-", font_size=config_eng.symbol.terminal_name_font_size)
            .match_style(self)
            .next_to(self.right, mn.LEFT, buff=config_eng.symbol.terminal_name_buff)
        )
        self._body.add(plus, minus)


class ACSourceBase(VoltageSourceBase):
    """Circuit symbol for a US-style alternating-current source."""

    def __init__(self, voltage: str | None = None, **kwargs: Any) -> None:
        super().__init__(arrow=True, voltage=voltage, **kwargs)

    def _construct(self) -> None:
        super()._construct()
        half_width = config_eng.symbol.square_bipole_side_length * 0.5
        half_size = 0.6 * half_width
        # Sine curve plotting references this article:
        # https://math.stackexchange.com/questions/4235124/getting-the-most-accurate-bezier-curve-that-plots-a-sine-wave
        sine_curve_x = 23 / 500
        sine_curve_y = 550 / 500
        squiggle = mn.VMobject()
        squiggle.start_new_path(half_size * mn.LEFT)
        squiggle.add_cubic_bezier_curve_to(
            (sine_curve_x * mn.LEFT + sine_curve_y * mn.UP) * half_size,
            (sine_curve_x * mn.RIGHT + sine_curve_y * mn.DOWN) * half_size,
            half_size * mn.RIGHT,
        )
        squiggle.match_style(self)
        self._body.add(squiggle)


class CurrentSourceBase(Source, metaclass=abc.ABCMeta):
    """Base class of all current sources."""

    def __init__(self, current: str | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if current is not None:
            self.set_current(current)


class EuropeanCurrentSourceBase(CurrentSourceBase, metaclass=abc.ABCMeta):
    """Base class for all European current sources.

    Implements the setting of current on the positive terminal that is unique to
    European sources, as well as the internal symbol of European current sources.

    Designed to be used in conjunction with the ``RoundOuter`` and ``DiamondOuter``
    modifiers, to produce standard and controlled sources.

    See Also
    --------
    modifiers.RoundOuter
    modifiers.DiamondOuter
    """

    def _construct(self) -> None:
        super()._construct()
        half_width = config_eng.symbol.square_bipole_side_length / 2
        self._body.add(
            mn.Line(
                start=mn.UP * half_width,
                end=mn.DOWN * half_width,
                z_index=self.z_index + 0.1,
            ).match_style(self)
        )
