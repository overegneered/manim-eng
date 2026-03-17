"""Contains the Circuit class."""

from typing import Any, Callable, Self, Sequence, cast

import manim as mn

__all__ = ["Circuit"]

from manim_eng.circuits.wire import Wire
from manim_eng.components.base.component import Component
from manim_eng.components.base.pin import Pin
from manim_eng.components.node import Node


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

    def connect(self, start: Pin, end: Pin) -> Self:
        """Connect two pins together.

        Parameters
        ----------
        start : Pin
            The pin the connecting wire should start at.
        end : Pin
            The pin the connecting wire should end at.

        Raises
        ------
        ValueError
            If the two pins passed are identical.
        ValueError
            If either pin doesn't belong to a component in this circuit.
        """
        self.__check_pins_all_belong_to_this_circuit([start, end])
        wire = Wire(start, end)
        wire._mark_shown()
        self.wires.add(wire)
        # Nodes will potentially change their appearance on wire attachment using an
        # updater, but it needs kicking into gear
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
            wire._mark_hidden()
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
            wire._mark_hidden()
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

    @mn.override_animate(connect)
    def __animate_connect(
        self,
        start: Pin,
        end: Pin,
        anim_args: dict[str, Any] | None = None,
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}

        self.__check_pins_all_belong_to_this_circuit([start, end])
        new_wire = Wire(start, end)
        self.wires.add(new_wire)
        animation = mn.Create(new_wire, **anim_args)
        # This call has to be here so that the wire is properly attached when the update
        # is done
        self.nodes.update()
        return animation

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
            wire._mark_hidden()
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
            wire._mark_hidden()
        animations = [mn.Uncreate(wire, **anim_args) for wire in to_remove]
        self.wires.remove(*to_remove)

        node_update_animation = self.nodes.animate(**anim_args).update().build()
        animations.append(node_update_animation)

        return mn.AnimationGroup(*animations)
