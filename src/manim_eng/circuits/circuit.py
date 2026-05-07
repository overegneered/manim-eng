"""Contains the Circuit class."""

import itertools
from typing import Any, Callable, Self, Sequence, cast

import manim as mn
import manim.typing as mnt
import numpy as np

from manim_eng._utils import utils
from manim_eng.circuits.base import WireBase
from manim_eng.circuits.network import Network
from manim_eng.circuits.node import Node
from manim_eng.circuits.wire import Wire
from manim_eng.components.base.component import Component
from manim_eng.components.base.pin import Pin

__all__ = ["Circuit"]


class Circuit(mn.VMobject):
    """Circuit manager to conveniently handle components and their connections.

    Parameters
    ----------
    *components : Component
        Components to add to the circuit at initialisation.
    """

    def __init__(self, *components: Component) -> None:
        super().__init__()

        self.nodes = mn.VGroup()
        self.components = mn.VGroup()
        self.wires = mn.VGroup()
        super().add(self.nodes, self.components, self.wires)

        self.add(*components)

    @property
    def elements(self) -> list[Component]:
        """Returns a list of all components (including nodes) in the circuit."""
        return cast(
            list[Component], self.components.submobjects + self.nodes.submobjects
        )

    def add(self, *components: Component) -> Self:
        """Add one or more components to the circuit.

        Parameters
        ----------
        *components : Component
            The component(s) to add.
        """
        for component in components:
            # Update here to make sure that all marks are properly aligned
            component.update()
            if isinstance(component, Node):
                self.nodes.add(component)
            else:
                self.components.add(component)
        return self

    def remove(self, *components: Component) -> Self:
        """Remove one or more components from the circuit.

        Parameters
        ----------
        *components : Component
            The component(s) to remove.
        """
        self.components.remove(*components)
        return self

    def connect(self, *pins: Pin) -> Self:
        """Connect a set of pins together.

        The pins are connected by creating wires between the networks attached to each
        pin. Wires are added between the closest points of the two closest networks
        until all pins in ``pins`` are in the same network.

        Two pins are considered to be in the same network if the circuit can be
        traversed from one pin to the other while only passing over wires or nodes.

        Parameters
        ----------
        *pins : Pin
            The pins to connect. Will be deduplicated internally. If there are fewer
            than two unique pins present, this method does nothing.

        Raises
        ------
        ValueError
            If any of the pins don't belong to a component in this circuit.
        """
        self.__check_pins_all_belong_to_this_circuit(list(pins))

        unique_pins = list(dict.fromkeys(pins))
        if len(unique_pins) < 2:  # noqa: PLR2004
            return self

        # Connect pins/wires according to the following algorithm:
        # 1. Connect the pair of objects (where an object is either a pin or a wire)
        #    that are closest to each other (based on the distance that separates their
        #    closest points) with a wire between their closest points
        # 2. Remove the original pins from consideration, but add the new wire into
        #    consideration
        # 3. Repeat until no pins remain unconnected

        # Keep references to wires that have been split so that their __del__ doesn't
        # fire mid-call and detach pins that are now owned by the replacement wires.
        _keep_alive: list[WireBase] = []

        while True:
            networks = self.__partition_into_networks(unique_pins)
            if len(networks) <= 1:
                break

            best_net_a, best_net_b = networks[0], networks[1]
            best_dist = np.inf
            best_pa: mnt.Point3D = mn.ORIGIN
            best_pb: mnt.Point3D = mn.ORIGIN

            for net_a, net_b in itertools.combinations(networks, 2):
                point_a, point_b = net_a.get_closest_points_with(net_b)
                dist = float(np.linalg.norm(point_b - point_a))
                if dist < best_dist:
                    best_dist = dist
                    best_net_a, best_net_b = net_a, net_b
                    best_pa, best_pb = point_a, point_b

            pin_a = self.__get_or_create_pin_at_point(
                best_pa,
                best_net_a.pins,
                best_net_a.wires,
                toward=best_pb,
                keep_alive=_keep_alive,
            )
            # TODO: determine if this is actually necessary
            # Re-derive best_net_b in case the previous call split a wire and mutated
            # the circuit (safe no-op when nothing changed).
            best_net_b = next(iter(best_net_b.pins)).get_network()
            pin_b = self.__get_or_create_pin_at_point(
                best_pb,
                best_net_b.pins,
                best_net_b.wires,
                toward=best_pa,
                keep_alive=_keep_alive,
            )

            new_wire = Wire(pin_a, pin_b)
            new_wire._set_visible()
            self.wires.add(new_wire)
            self.nodes.update()

        return self

    def disconnect(self, *components_or_pins: Component | Pin) -> Self:
        """Disconnect the given components and/or pins from one another.

        Each wire is checked to see if *both* the start *and* end pins have been
        passed or belong to a component that was passed. If this is the case, the wire
        will be removed.

        Parameters
        ----------
        *components_or_pins : Component | Pin
            The group of components and pins to disconnect from one another.

        Raises
        ------
        ValueError
            If any passed pin does not belong to a component in this circuit.

        See Also
        --------
        isolate : Remove a wire if either of its ends is specified.
        """
        pins = self._collapse_components_and_pins_to_pins(components_or_pins)
        self.__check_pins_all_belong_to_this_circuit(pins)
        to_remove = self.__get_wires_from_pin_condition(
            pins, lambda start, end: start and end
        )
        for wire in to_remove:
            wire._set_hidden()
        self.wires.remove(*to_remove)
        # Nodes will potentially change their appearance on wire detachment using an
        # updater, but it needs kicking into gear
        self.nodes.update()
        return self

    def isolate(self, *components_or_pins: Component | Pin) -> Self:
        """Remove all wires attached to each given pin or component.

        Each wire is checked to see if either of its ends is a passed pin or a
        pin on a passed component. If this is the case, the wire will be removed.

        Parameters
        ----------
        *components_or_pins : Component | Pin
            The components and pins to completely disconnect from the circuit.

        Raises
        ------
        ValueError
            If any passed pin does not belong to a component in this circuit.

        See Also
        --------
        disconnect : Remove a wire if both its ends are specified.
        """
        pins = self._collapse_components_and_pins_to_pins(components_or_pins)
        self.__check_pins_all_belong_to_this_circuit(pins)
        to_remove = self.__get_wires_from_pin_condition(
            pins, lambda start, end: start or end
        )
        for wire in to_remove:
            wire._set_hidden()
        self.wires.remove(*to_remove)
        # Nodes will potentially change their appearance on wire detachment using an
        # updater, but it needs kicking into gear
        self.nodes.update()
        return self

    @staticmethod
    def _collapse_components_and_pins_to_pins(
        components_or_pins: Sequence[Component | Pin],
    ) -> list[Pin]:
        pins = []
        for component_or_pin in components_or_pins:
            if isinstance(component_or_pin, Component):
                pins.extend(component_or_pin.pins)
            else:
                pins.append(component_or_pin)
        # Remove duplicate entries
        return list(set(pins))

    def __get_wires_from_pin_condition(
        self, pins: Sequence[Pin], condition: Callable[[bool, bool], bool]
    ) -> list[Wire]:
        """Return a list of wires from the circuit based on a given condition.

        Iterates through all connections and calculates if each end of the wire is in
        ``pins``. Whether each one is in ``pins`` is passed to ``condition``,
        which is expected to return ``True`` if the wire should be included.

        Parameters
        ----------
        pins : Sequence[Pin]
            The pins to check all wires for.
        condition : Callable[[bool, bool], bool]
            The condition to use to determine whether a wire should be returned. Will be
            passed two booleans, whether the start or end of the wire is in
            ``pins``, respectively, and should return ``True`` if the wire should
            be returned and ``False`` otherwise.

        Returns
        -------
        list[Wire]
            The list of wires selected by the condition.
        """
        to_remove = []
        for wire in cast(list[Wire], self.wires.submobjects):
            if condition(
                wire._start in pins,
                wire._end in pins,
            ):
                to_remove.append(wire)
        return to_remove

    def __check_pins_all_belong_to_this_circuit(self, pins: list[Pin]) -> None:
        pin_set = set(pins)
        owned_pin_set = set()
        for component in self.elements:
            owned_pin_set.update(component.pins)

        pins_not_owned = pin_set.difference(owned_pin_set)
        if len(pins_not_owned) != 0:
            raise ValueError(
                f"At least one passed pin does not "
                f"belong to any component in this circuit. "
                f"Problem pins have the following end coordinates: "
                f"{[tuple(pin.tip) for pin in pins_not_owned]}"
            )

    def __partition_into_networks(self, pins: list[Pin]) -> list[Network]:
        """Partition ``pins`` into groups that are already connected to each other.

        Parameters
        ----------
        pins : list[Pin]
            The pins to partition.

        Returns
        -------
        list[Network]
            The networks the pins belong to.
        """
        networks: list[Network] = []
        seen: set[Pin] = set()
        for pin in pins:
            if pin in seen:
                continue
            network = pin.get_network()
            seen.update(network.pins)
            networks.append(network)
        return networks

    def __get_or_create_pin_at_point(
        self,
        point: mnt.Point3D,
        net_pins: set[Pin],
        net_wires: set[WireBase],
        toward: mnt.Point3D,
        keep_alive: list[WireBase],
    ) -> Pin:
        """Return a free pin at ``point``, splitting a wire there if necessary.

        Parameters
        ----------
        point : Point3D
            The target point, which must be either a free pin tip or a point on one
            of the wires in the network.
        net_pins : set[Pin]
            All pins in the network.
        net_wires : set[WireBase]
            All wires in the network.
        toward : Point3D
            The point on the *other* network being connected; used to choose the
            outward direction of the node pin when a wire is split.
        keep_alive : list[WireBase]
            Accumulator for wires that have been removed from the circuit.  Keeping
            a reference here prevents their ``__del__`` from firing before the new
            wires and node have been fully set up.

        Returns
        -------
        Pin
            A free pin located at ``point``.

        Raises
        ------
        RuntimeError
            If ``point`` cannot be matched to a free pin tip or a wire segment.
        """
        for pin in net_pins:
            if not pin.wire_currently_attached() and np.allclose(pin.base, point):
                return pin

        for wire in net_wires:
            start_portion, node, end_portion = wire.split_at_point(point)
            keep_alive.append(wire)
            self.wires.remove(wire)
            self.wires.add(start_portion, end_portion)
            start_portion._set_visible()
            end_portion._set_visible()
            self.add(node)
            self.nodes.update()
            direction = utils.cardinalised(toward - node.get_center())
            return node.get(direction)

        raise RuntimeError(
            f"Could not locate a free pin or wire at point {point!r} in the network."
        )

    @mn.override_animate(add)
    def __animate_add(
        self, *components: Component, anim_args: dict[str, Any] | None = None
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}

        self.add(*components)
        return mn.AnimationGroup(
            *[mn.Create(component, **anim_args) for component in components]
        )

    @mn.override_animate(remove)
    def __animate_remove(
        self, *components: Component, anim_args: dict[str, Any] | None = None
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}

        self.remove(*components)
        return mn.AnimationGroup(
            *[mn.Uncreate(component, **anim_args) for component in components]
        )

    @mn.override_animate(disconnect)
    def __animate_disconnect(
        self,
        *components_or_pins: Component | Pin,
        anim_args: dict[str, Any] | None = None,
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}

        pins = self._collapse_components_and_pins_to_pins(components_or_pins)
        self.__check_pins_all_belong_to_this_circuit(pins)
        to_remove = self.__get_wires_from_pin_condition(
            pins, lambda start, end: start and end
        )
        for wire in to_remove:
            wire._set_hidden()
        animations = [mn.Uncreate(wire, **anim_args) for wire in to_remove]
        self.wires.remove(*to_remove)

        node_update_animation = self.nodes.animate(**anim_args).update().build()
        animations.append(node_update_animation)

        return mn.AnimationGroup(*animations)

    @mn.override_animate(isolate)
    def __animate_isolate(
        self,
        *components_or_pins: Component | Pin,
        anim_args: dict[str, Any] | None = None,
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}

        pins = self._collapse_components_and_pins_to_pins(components_or_pins)
        self.__check_pins_all_belong_to_this_circuit(pins)
        to_remove = self.__get_wires_from_pin_condition(
            pins, lambda start, end: start or end
        )
        for wire in to_remove:
            wire._set_hidden()
        animations = [mn.Uncreate(wire, **anim_args) for wire in to_remove]
        self.wires.remove(*to_remove)

        node_update_animation = self.nodes.animate(**anim_args).update().build()
        animations.append(node_update_animation)

        return mn.AnimationGroup(*animations)
