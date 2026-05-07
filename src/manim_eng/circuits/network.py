"""Contains the Network utility class."""

from typing import Iterator, Self, cast

import manim as mn
import manim.typing as mnt
import numpy as np

from manim_eng.circuits.base.wire import WireBase
from manim_eng.circuits.node import Node
from manim_eng.components.base.pin import Pin


# TODO: add feedthrough to allow Network to pass manim methods on to the underlying
#       mobjects
class Network:
    """Construct the network of pins, wires, and nodes reachable from ``start``.

    The network is formed by following wires and nodes, starting from the given pin,
    wire, or node. It is essentially the parts of wiring that, according to circuit
    theory, would have the same voltage. Note however that this does **not** follow
    components like :class:`~.Switch`es — this is primarily a utility for wiring
    management, not part of a circuit simulation system.

    While following nodes, all pins attached to that node are included in
    :attr:`~.Network.pins` (unless ``exclude_nodal_pins`` is ``True``).

    **No guarantees** are made about the ordering of the collections returned.

    **Does not update on the fly — this is *only* correct at time of generation**.

    Parameters
    ----------
    start : Pin | WireBase | Node
        The pin, wire, or node to start from.
    exclude_nodal_pins: bool
        If set to ``True``, pins attached to nodes will **not** be included in
        :attr:`~.Network.pins`.

    Examples
    --------
    .. code-block:: python

        r = Resistor()
        net = Network(r.left)
        for wire in net.wires:
            wire.set_color(RED)

    ``Network`` also implements ``__iter__`` so it can be unpacked directly:

    .. code-block:: python

        r = Resistor()
        pins, wires, nodes = Network(r.left)
    """

    def __init__(
        self, start: Pin | WireBase | Node, exclude_nodal_pins: bool = False
    ) -> None:
        self.pins: set[Pin] = set()
        self.wires: set[WireBase] = set()
        self.nodes: set[Node] = set()

        if isinstance(start, Pin):
            pin = start
        elif isinstance(start, WireBase):
            pin = start.start
        elif isinstance(start, Node):
            if len(start.pins) > 0 and not exclude_nodal_pins:
                pin = start.pins[0]
            else:
                self.nodes.add(start)
                return
        else:
            raise TypeError(
                "`start` must be a `Pin`, `WireBase` instance (e.g. `Wire` or "
                "`ManualWire`), or `Node`."
            )

        self.__build_network(exclude_nodal_pins, pin)

    def __build_network(self, exclude_nodal_pins: bool, start: Pin) -> None:
        self.pins.add(start)
        stack: list[Pin] = [start]
        while len(stack) > 0:
            current = stack.pop()
            if isinstance(current.parent, Node) and current.parent not in self.nodes:
                node = current.parent
                self.nodes.add(node)
                for sibling in node.pins:
                    if sibling not in self.pins:
                        self.pins.add(sibling)
                        stack.append(sibling)

            wire = current.attached_wire
            if wire is not None and wire not in self.wires:
                self.wires.add(wire)

                # Since a wire is attached, other_end must exist
                other_end = cast(Pin, current.other_end)
                if other_end not in self.pins:
                    self.pins.add(other_end)
                    stack.append(other_end)

        if exclude_nodal_pins:
            for node in self.nodes:
                self.pins.difference_update(node.pins)

    def get_point_closest_to(self, point: mnt.Point3D | Pin) -> mnt.Point3D:
        """Get the point in the network closest to ``point``.

        For networks without wires, pins are represented by their
        :attr:`~.Pin.base` point and nodes by their centre.

        Raises
        ------
        ValueError
            If the network is empty (no wires, pins, or nodes).
        """
        if isinstance(point, Pin):
            point = point.tip

        closest_point: mnt.Point3D = mn.ORIGIN
        sq_distance: float = np.inf

        for wire in self.wires:
            current_closest_point = wire.get_point_closest_to(point)
            vec = point - current_closest_point
            current_sq_distance = np.dot(vec, vec)
            if current_sq_distance < sq_distance:
                closest_point = current_closest_point
                sq_distance = current_sq_distance
        if len(self.wires) == 0:
            # No wires, therefore network consists of a single pin or node
            if len(self.pins) > 0:
                closest_point = next(iter(self.pins)).base
            elif len(self.nodes) > 0:
                closest_point = next(iter(self.nodes)).get_center()
            else:
                raise ValueError("Cannot find closest point: network is empty.")

        return closest_point

    def get_closest_points_with(
        self, other: Self | WireBase
    ) -> tuple[mnt.Point3D, mnt.Point3D]:
        """Get the closest pair of points between the network and ``other``.

        Parameters
        ----------
        other: Network | WireBase
            The other network or wire to find the closest point to.

        For networks without wires, pins are represented by their
        :attr:`~.Pin.base` point and nodes by their centre.

        Returns
        -------
        tuple[Point3D, Point3D]
            A tuple containing the pair of closest points, with the one for this network
            first and the one for the other network or wire second.

        Raises
        ------
        ValueError
            If this network is empty (no wires, pins, or nodes).
        """
        closest_points: tuple[mnt.Point3D, mnt.Point3D] = (mn.ORIGIN, mn.ORIGIN)
        sq_distance: float = np.inf

        for wire in self.wires:
            if isinstance(other, WireBase):
                current_closest_points = wire.get_closest_points_with(other)
            else:
                a, b = other.get_closest_points_with(wire)
                current_closest_points = (b, a)
            vec = current_closest_points[1] - current_closest_points[0]
            current_sq_distance = np.dot(vec, vec)
            if current_sq_distance < sq_distance:
                sq_distance = current_sq_distance
                closest_points = current_closest_points

        if len(self.wires) == 0:
            # No wires, therefore network consists of a single pin or node
            if len(self.pins) > 0:
                point = next(iter(self.pins)).base
            elif len(self.nodes) > 0:
                point = next(iter(self.nodes)).get_center()
            else:
                raise ValueError("Cannot find closest points: network is empty.")
            closest_points = (point, other.get_point_closest_to(point))

        return closest_points

    def __iter__(self) -> Iterator[set[Pin] | set[WireBase] | set[Node]]:
        """Yield the pins, wires, and nodes in sequence.

        Designed to allow things like

        .. code-block:: python

            r = Resistor()
            pins, wires, nodes = Network(r.left)
        """
        yield self.pins
        yield self.wires
        yield self.nodes
