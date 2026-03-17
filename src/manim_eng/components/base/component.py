"""Contains the Component base class."""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Any, Self, cast

import manim as mn
import manim.typing as mnt
import numpy as np

from manim_eng import config_eng
from manim_eng._base.anchor import AnnotationAnchor, CentreAnchor, LabelAnchor
from manim_eng._base.mark import Mark
from manim_eng._base.markable import Markable
from manim_eng.circuits.voltage import Voltage
from manim_eng.components.base.pin import Pin

if TYPE_CHECKING:
    from manim_eng.components.base.monopole import Monopole
    from manim_eng.components.node import Node

__all__ = ["Component"]


class Component(Markable, metaclass=abc.ABCMeta):
    """Base class for all components.

    Parameters
    ----------
    pins : list[Pin]
        The pins of the component. Management of pins is handled by the constructor, and
        they do not need to be added beforehand or afterwards.
    label : str | None, optional
        A label to set. Takes a TeX math mode string.
    annotation : str | Value | None, optional
        An annotation to set. Takes a TeX math mode string, or a ``Value`` to be typeset
         as a math mode string.
    """

    def __init__(
        self,
        pins: list[Pin],
        label: str | None = None,
        annotation: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            stroke_width=config_eng.symbol.component_stroke_width, **kwargs
        )

        self._pins = mn.VGroup(*pins)
        self._body = mn.VGroup()
        self.add(self._body)

        self._construct()

        self._body.add(self._pins)

        self._centre_anchor = CentreAnchor()
        self._label_anchor = LabelAnchor()
        self._annotation_anchor = AnnotationAnchor()
        self.__set_up_anchors()

        self._label = Mark(self._label_anchor, self._centre_anchor, label)
        self._annotation = Mark(
            self._annotation_anchor, self._centre_anchor, annotation
        )
        self.add(self._label, self._annotation)

    def _construct(self) -> None:
        """Construct the shape of the component.

        Code to build the component's symbol goes in here  and *not* in ``__init__()``
        (contrary to Manim's standard). This is because the base ``Component`` class
        has to perform initialisation both before (to set up the groups etc.) and after
        (to set the anchor positions for annotations) the component's shape setup.

        :meta public:
        """

    @property
    def pins(self) -> list[Pin]:
        """The list of terminals of the component."""
        return cast(list[Pin], self._pins.submobjects)

    @property
    def label(self) -> Mark:
        """A handle to the label of the component."""
        return self._label

    @property
    def annotation(self) -> Mark:
        """A handle to the annotation of the component."""
        return self._annotation

    def get_center(self) -> mnt.Point3D:
        """Get the centre of the components.

        **This is not necessarily the exact centre of the box the component symbol
        occupies**. It is rather the point about which it is most logical to rotate
        the component. For bipoles, it will be at the midpoint of the line between the
        two terminals.

        Returns
        -------
        Point3D
            The centre of the components.
        """
        return self._centre_anchor.get_center()

    def align_pin(
        self,
        pin: Pin | str,
        other: Pin | mnt.Point3D | Node | Monopole,
        direction: mnt.Vector3D | None = None,
    ) -> Self:
        """Align a component pin with a point or another component.

        Moves this component along the line perpendicular to ``direction`` such that the
        line between the end of ``pin`` and ``other`` has direction vector
        ``direction``.

        Parameters
        ----------
        pin : Pin | str
             Either a ``Pin`` belonging to this component, or a string representing
            an attribute of this component that returns a pin (e.g. ``"right"``).
        other : Pin | Point3D | Node | Monopole
            A ``Pin`` belonging to another component, a ``Node``, a ``Monopole``
            (for which its single pin is selected), or a point in space.
        direction : Vector3D | None
            The direction to align the pins in. If not supplied, uses
            ``pin``'s direction.

        Raises
        ------
        ValueError
            If a ``Pin`` passed to ``pin`` does not belong to this component.
        AttributeError
            If a string passed to ``pin`` does not represent an existing attribute on
            this component.
        ValueError
            If a string passed to ``pin`` does not represent an attribute of this
            component that produces a ``Pin`` instance.
        ValueError
            If ``other`` belongs to this component (if it is a ``Pin``)
            or if ``other`` *is* this component (if it is a ``Node`` or
            ``Monopole``).

        Notes
        -----
        In geometric terms, the component in moved such that the end of ``pin`` is at
        the intersection of the lines that

        - Have direction vector perpendicular to ``direction`` and go through the
            current position of the end of ``pin``; and
        - Have direction vector ``direction`` and go through the end of ``other`` (in
            the case that it is a ``Pin``) or through ``other`` (in the case that it is
            a point).
        """
        from manim_eng.components.base.monopole import Monopole
        from manim_eng.components.node import Node

        pin = self._get_or_check_pin(pin)
        if isinstance(other, Pin):
            if other in self.pins:
                raise ValueError(
                    "Pin passed to `other` belongs to this component. "
                    "`other` should be a pin of another component, "
                    "a point, or a separate Node or Monopole."
                )
            other = other.tip
        elif isinstance(other, Node):
            if other == self:
                raise ValueError(
                    "Node passed to `other` is this component. "
                    "`other` should be a pin of another component, "
                    "a point, or a separate Node or Monopole."
                )
            other = other.get_center()
        elif isinstance(other, Monopole):
            if other == self:
                raise ValueError(
                    "Monopole passed to `other` is this component. "
                    "`other` should be a terminal of another component, "
                    "a point, or a separate Node or Monopole."
                )
            other = other.pin.tip

        if direction is None:
            direction = pin.direction

        movement_direction = np.cross(direction, mn.OUT)
        target_position = mn.find_intersection(
            [pin.tip],
            [movement_direction],
            [other],
            [direction],
        )[0]

        self.shift(target_position - pin.tip)
        return self

    def voltage(
        self,
        start: Pin | str,
        end: Pin | str,
        *args: Any,
        **kwargs: Any,
    ) -> Voltage:
        """Return a voltage arrow across the component.

        Convenience method for creating a voltage arrow across two pins of this
        component. Returns the created ``Voltage`` object. This method automatically
        sets the component is it called upon in the ``avoid`` argument of ``Voltage``
        (and as such overrides this argument).

        Parameters
        ----------
        start : Pin | str
            Either a ``Pin`` belonging to this component, or a string representing
            an attribute of this component that returns a pin (e.g. ``"right"``).
        end : Pin | str
            Either a ``Pin`` belonging to this component, or a string representing
            an attribute of this component that returns a pin (e.g. ``"left"``).
        *args
            Positional arguments to be passed to the ``Voltage`` constructor.
        **kwargs
            Keyword arguments to be passed to the ``Voltage`` constructor. Any keyword
            argument with the key ``avoid`` will be ignored.

        Returns
        -------
        Voltage
            The voltage arrow resulting from the specification given.

        Raises
        ------
        ValueError
            If a passed ``Pin`` does not belong to this component.
        AttributeError
            If a string passed for either pin does not represent an existing attribute.
        ValueError
            If a string passed for either pin does not represent an attribute of this
            component that produces a ``Pin`` instance.
        ValueError
            If the pins specified for both ``start`` and ``end`` are the same.
        """
        start = self._get_or_check_pin(start)
        end = self._get_or_check_pin(end)

        if start == end:
            raise ValueError(
                "The pins specified through `start` and `end` are "
                "the same. They must be different."
            )

        kwargs["avoid"] = self

        return Voltage(start, end, *args, **kwargs)

    def _get_or_check_pin(self, pin: Pin | str | None) -> Pin:
        """Get a pin from a string or check a passed pin belongs to this component.

        Parameters
        ----------
        pin : Pin | str | None
            The string to use as a pin identifier, a ``Pin`` instance to verify belongs
            to this component, or ``None``, in which case the first pin on the component
            will be selected.

        Returns
        -------
        Pin
            The pin identified.

        Raises
        ------
        AttributeError
            If the string passed for the pin doesn't exist as an attribute on this
            component.
        ValueError
            If the attribute identified by the string isn't an instance of ``Pin``.
        ValueError
            If the pin passed doesn't belong to this component.
        """
        if pin is None:
            return self.pins[0]

        if isinstance(pin, Pin):
            if pin not in self.pins:
                raise ValueError("Passed pin does not belong to this component.")
            return pin

        to_return = getattr(self, pin)
        if not isinstance(to_return, Pin):
            raise ValueError(
                f"Attribute `{pin}` of `{self.__class__.__name__}` " f"is not a pin."
            )
        return to_return

    def __set_up_anchors(self) -> None:
        # A small amount is added to each of these anchors to make sure that they are
        # never directly over the centre anchor, as this causes problems.
        self._label_anchor.shift(self._body.get_top() + 0.01 * mn.UP)
        self._annotation_anchor.shift(self._body.get_bottom() + 0.01 * mn.DOWN)
        self.add(self._centre_anchor, self._label_anchor, self._annotation_anchor)
