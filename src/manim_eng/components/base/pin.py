"""Contains Pin class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self

import manim as mn
import manim.typing as mnt
import numpy as np

from manim_eng._base.anchor import PinAnchor
from manim_eng._base.markable import Markable
from manim_eng._config import config_eng
from manim_eng.circuits.current import CurrentArrow

if TYPE_CHECKING:
    from manim_eng.circuits.base.wire import WireBase
    from manim_eng.circuits.network import Network
    from manim_eng.circuits.node import Node
    from manim_eng.components.base.component import Component

__all__ = ["Pin"]


class Pin(Markable):
    """Pin for a circuit component (i.e. the bit other wires connect to).

    Parameters
    ----------
    position : manim.Point3D
        The point at which the pin meets the body of the component.
    direction : manim.Vector3D
        A vector pointing in the direction of the pin (away from the body).
    parent : Component
        A handle to the parent component.
    length : float, optional
        The length the pin should have. If left unspecified, takes the value
        ``config_eng.symbol.pin_length``.
    """

    def __init__(
        self,
        position: mnt.Point3D,
        direction: mnt.Vector3D,
        parent: Component,
        length: float | None = None,
    ):
        super().__init__()
        direction = mn.normalize(direction)

        self._parent = parent

        if length is None:
            length = config_eng.symbol.pin_length

        self._body_anchor = PinAnchor().move_to(position)
        self._end_anchor = PinAnchor().move_to(position + direction * length)

        self.add(self._body_anchor, self._end_anchor)

        self._attached_wire: WireBase | None = None

    @property
    def base(self) -> mnt.Point3D:
        """The point at which the pin connects to the component body."""
        return self._body_anchor.pos

    @property
    def tip(self) -> mnt.Point3D:
        """The point at which the pin connects to external wires."""
        return self._end_anchor.pos

    @property
    def direction(self) -> mnt.Vector3D:
        """A unit vector pointing out of the pin (towards the end)."""
        return mn.normalize(self.tip - self.base)

    @property
    def length(self) -> float:
        """The length of the pin (the distance between the start and end)."""
        return float(np.linalg.norm(self.tip - self.base))

    @property
    def attached_wire(self) -> WireBase | None:
        """A reference to the wire attached to this pin, if one exists."""
        return self._attached_wire

    @property
    def other_end(self) -> Self | None:
        """A reference to the pin on the other end of an attached wire, if one exists.

        Returns
        -------
        Self | None
            ``Self`` if a wire is attached, ``None`` otherwise.
        """
        if self._attached_wire is None:
            return None

        if self._attached_wire.start == self:
            return self._attached_wire.end
        return self._attached_wire.start

    @property
    def parent(self) -> "Component":
        """The parent component of this pin."""
        return self._parent

    @property
    def current(self) -> CurrentArrow:
        """A handle to the current arrow on the wire attached to this pin.

        Raises
        ------
        AttributeError
            If no wire is attached to this pin.
        """
        if self._attached_wire is None:
            raise AttributeError("No wire attached to this pin.")
        return self._attached_wire.current

    def get_network(self, *args: Any, **kwargs: Any) -> Network:
        """Get the wire network this pin is part of.

        The network is formed by following wires and nodes, starting from this pin. It
        is essentially the parts of wiring that, according to circuit theory, would have
        the same voltage.

        While following nodes, only pins that for an active part of the network are
        included (i.e. pins that have wires attached to themselves).

        **No guarantees** are made about the ordering of the collections returned.

        Parameters
        ----------
        *args : Any
            Positional arguments passed to :class:`~.Network`'s constructor.
        **kwargs : Any
            Keyword arguments passed to :class:`~.Network`'s constructor.

        Returns
        -------
        Network
            A ``Network`` object containing all pins, wires, and nodes logically
            reachable from this pin. Includes this pin.

        See Also
        --------
        get_connected_pins
        get_connected_wires
        get_connected_nodes
        """
        # Import has to be here to avoid circular import
        from manim_eng.circuits.network import Network  # noqa: PLC0415

        return Network(self, *args, **kwargs)

    def get_connected_pins(
        self, exclude_nodal_pins: bool = False, exclude_self: bool = False
    ) -> set[Pin]:
        """Get the pins connected electrically to this pin.

        This will traverse nodes to follow the line of electrical connection. Will
        **not** traverse components like closed switches.

        Parameters
        ----------
        exclude_nodal_pins : bool, optional
            If set to ``True``, pins attached to nodes traversed will be excluded from
            the returned set.
        exclude_self : bool, optional
            If set to ``True``, the returned set will not contain the pin whose call
            created the set. Defaults to ``False`` (i.e. the pin the method is called on
            will be included).

        Returns
        -------
        set[Pin]
            A set containing all pins electrically connected to this pin.

        See Also
        --------
        get_network
        get_connected_wires
        get_connected_nodes
        """
        pins = self.get_network(exclude_nodal_pins=exclude_nodal_pins).pins
        if exclude_self:
            pins.remove(self)
        return pins

    def get_connected_wires(self) -> set[WireBase]:
        """Get the wires connected electrically to this pin.

        This will traverse nodes to follow the line of electrical connection. Will
        **not** traverse components like closed switches.

        Returns
        -------
        set[WireBase]
            A set containing all wires electrically connected to this pin.

        See Also
        --------
        get_network
        get_connected_pins
        get_connected_nodes
        """
        return self.get_network().wires

    def get_connected_nodes(self) -> set[Node]:
        """Get the nodes connected electrically to this pin.

        This will traverse nodes to follow the line of electrical connection. Will
        **not** traverse components like closed switches.

        Returns
        -------
        set[Node]
            A set containing all nodes electrically connected to this pin.

        See Also
        --------
        get_network
        get_connected_wires
        get_connected_nodes
        """
        return self.get_network().nodes

    def attach_wire(self, wire: "WireBase") -> Self:
        """Register that a wire is attached to this pin.

        Does nothing if the wire is already attached.

        Parameters
        ----------
        wire : WireBase
            The wire to be attached.

        Raises
        ------
        AttributeError
            If a wire not equal to ``wire`` is already attached to this pin.
        """
        if self._attached_wire is not None and self._attached_wire != wire:
            raise AttributeError(
                "A pin can only have one wire attached at any given "
                "time. Please add a node to handle wire junctions."
            )
        self._attached_wire = wire
        return self

    def detach_wire(self) -> Self:
        """Register that the attached wire has been detached.

        Does nothing if no wire was attached in the first place.
        """
        self._attached_wire = None
        return self

    def is_visible(self) -> bool:
        """Return whether the pin appears drawn on screen, to the best of its knowledge.

        Returns
        -------
        bool
            ``True`` if the pin is visible, ``False`` otherwise.
        """
        if self._attached_wire is None:
            return False
        return self._attached_wire.is_visible()

    def wire_currently_attached(self) -> bool:
        """Return whether a wire is currently attached to this pin."""
        return self._attached_wire is not None
