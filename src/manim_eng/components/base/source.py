"""Module containing base classes for creating sources."""

import abc
from typing import Any, Self

import manim as mn
import numpy as np

from manim_eng import config_eng
from manim_eng.components.base.bipole import Bipole
from manim_eng.components.base.terminal import Terminal


class Source(Bipole, metaclass=abc.ABCMeta):
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
        """Return the negative (left-hand) terminal of the component."""
        return self.left

    @property
    def positive(self) -> Terminal:
        """Return the positive (right-hand) terminal of the component."""
        return self.right


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

        Returns
        -------
        Self
            The (modified) voltage source on which the method was called.
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

        Returns
        -------
        Self
            The (modified) voltage source on which the method was called.
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
            stroke_width=config_eng.symbol.arrow_stroke_width,
            tip_length=config_eng.symbol.arrow_tip_length,
            buff=0,
        )
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

    Parameters
    ----------
    voltage : str | None
        The voltage label to set initially. Takes a TeX math mode string.
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
                stroke_width=config_eng.symbol.component_stroke_width,
            )
        )


class CurrentSourceBase(Source, metaclass=abc.ABCMeta):
    """Base class of all current sources."""

    def __init__(self, current: str | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if current is not None:
            self.set_current(current)

    @abc.abstractmethod
    def set_current(self, label: str) -> Self:
        """Set the current label.

        Sets the current label of the source. The underlying label used to display this
        differs by source type: European sources use the positive terminal's current
        label, American sources use the component's label. It is recommended to use this
        method over `.positive.set_current()` or `.set_label()` for portability between
        European and American source types.

        Parameters
        ----------
        label : str
            The current label to set. Takes a TeX math mode string.

        Returns
        -------
        Self
            The (modified) current source on which the method was called.
        """

    @abc.abstractmethod
    def clear_current(self) -> Self:
        """Clear the current label.

        Clears the current label of the source, being either the positive terminal's
        current label (for European sources) or the component's label (for American).
        It is recommended to use this method over `.positive.clear_current()` or
        `.clear_label()` for portability between European and American source types.

        Returns
        -------
        Self
            The (modified) current source on which the method was called.
        """


class EuropeanCurrentSourceBase(CurrentSourceBase, metaclass=abc.ABCMeta):
    """Base class for all European current sources.

    Implements the setting of current on the positive terminal that is unique to
    European sources.
    """

    def _construct(self) -> None:
        super()._construct()
        half_width = config_eng.symbol.square_bipole_side_length / 2
        self._body.add(
            mn.Line(
                start=mn.UP * half_width,
                end=mn.DOWN * half_width,
                stroke_width=config_eng.symbol.component_stroke_width,
            )
        )

    def set_current(self, label: str) -> Self:
        """Set the current of the source.

        Sets the current label of the source using the positive terminal's current
        label. Can be used in conjunction with `.positive.set_current()` and
        `.positive.clear_current()` methods, but for portability with the American
        current sources this is not recommended.

        Parameters
        ----------
        label : str
            The current label to set. Takes a TeX math mode string.

        Returns
        -------
        Self
            The (modified) current source on which the method was called.
        """
        self.positive.set_current(label, out=True)
        return self

    def clear_current(self) -> Self:
        """Clear the current label of the source.

        Clears the current label (which for European sources is that of the positive
        terminal).

        Returns
        -------
        Self
            The (modified) current source on which the method was called.
        """
        self.positive.clear_current()
        return self

    @mn.override_animate(set_current)
    def __animate_set_current(
        self, label: str, anim_args: dict[Any, str] | None = None
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}

        return self.positive.animate(**anim_args).set_current(label, out=True).build()

    @mn.override_animate(clear_current)
    def __animate_clear_current(
        self, anim_args: dict[Any, str] | None = None
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}

        return self.positive.animate(**anim_args).clear_current().build()
