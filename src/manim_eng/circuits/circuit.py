"""Contains the Circuit class."""

from typing import Any, Callable, Self, Sequence, cast

import manim as mn

__all__ = ["Circuit"]

from manim_eng.circuits.wire import Wire
from manim_eng.components.base.component import Component
from manim_eng.components.base.terminal import Terminal
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

    def connect(self, start: Terminal, end: Terminal) -> Self:
        """Connect two terminals together.

        Parameters
        ----------
        start : Terminal
            The terminal the connecting wire should start at.
        end : Terminal
            The terminal the connecting wire should end at.

        Raises
        ------
        ValueError
            If the two terminals passed are identical.
        ValueError
            If either terminal doesn't belong to a component in this circuit.
        """
        self.__check_terminals_all_belong_to_this_circuit([start, end])
        self.wires.add(Wire(start, end).attach())
        # Nodes will potentially change their appearance on wire attachment using an
        # updater, but it needs kicking into gear
        self.nodes.update()
        return self

    def disconnect(self, *components_or_terminals: Component | Terminal) -> Self:
        """Disconnect the given components and/or terminals from one another.

        Each wire is checked to see if *both* the start *and* end terminals have been
        passed or belong to a component that was passed. If this is the case, the wire
        will be removed.

        Parameters
        ----------
        *components_or_terminals : Component | Terminal
            The group of components and terminals to disconnect from one another.

        Raises
        ------
        ValueError
            If any passed terminal does not belong to a component in this circuit.

        See Also
        --------
        isolate : Remove a wire if either of its ends is specified.
        """
        terminals = self._collapse_components_and_terminals_to_terminals(
            components_or_terminals
        )
        self.__check_terminals_all_belong_to_this_circuit(terminals)
        to_remove = self.__get_wires_from_terminal_condition(
            terminals, lambda start, end: start and end
        )
        self.wires.remove(*to_remove)
        for wire in to_remove:
            wire.detach()
        # Nodes will potentially change their appearance on wire detachment using an
        # updater, but it needs kicking into gear
        self.nodes.update()
        return self

    def isolate(self, *components_or_terminals: Component | Terminal) -> Self:
        """Remove all wires attached to each given terminal or component.

        Each wire is checked to see if either of its ends is a passed terminal or a
        terminal on a passed component. If this is the case, the wire will be removed.

        Parameters
        ----------
        *components_or_terminals : Component | Terminal
            The components and terminals to completely disconnect from the circuit.

        Raises
        ------
        ValueError
            If any passed terminal does not belong to a component in this circuit.

        See Also
        --------
        disconnect : Remove a wire if both its ends are specified.
        """
        terminals = self._collapse_components_and_terminals_to_terminals(
            components_or_terminals
        )
        self.__check_terminals_all_belong_to_this_circuit(terminals)
        to_remove = self.__get_wires_from_terminal_condition(
            terminals, lambda start, end: start or end
        )
        self.wires.remove(*to_remove)
        # Nodes will potentially change their appearance on wire detachment using an
        # updater, but it needs kicking into gear
        self.nodes.update()
        return self

    @staticmethod
    def _collapse_components_and_terminals_to_terminals(
        components_or_terminals: Sequence[Component | Terminal],
    ) -> list[Terminal]:
        terminals = []
        for component_or_terminal in components_or_terminals:
            if isinstance(component_or_terminal, Component):
                terminals.extend(component_or_terminal.terminals)
            else:
                terminals.append(component_or_terminal)
        # Remove duplicate entries
        return list(set(terminals))

    def __get_wires_from_terminal_condition(
        self, terminals: Sequence[Terminal], condition: Callable[[bool, bool], bool]
    ) -> list[Wire]:
        """Return a list of wires from the circuit based on a given condition.

        Iterates through all connections and calculates if each end of the wire is in
        ``terminals``. Whether each one is in ``terminals`` is passed to ``condition``,
        which is expected

        Parameters
        ----------
        terminals : Sequence[Terminal]
            The terminals to check all wires for.
        condition : Callable[[bool, bool], bool]
            The condition to use to determine whether a wire should be returned. Will be
            passed two booleans, whether the start or end of the wire is in
            ``terminals``, respectively, and should return ``True`` if the wire should
            be returned and ``False`` otherwise.

        Returns
        -------
        list[Wire]
            The list of wires selected by the condition.
        """
        to_remove = []
        for wire in cast(list[Wire], self.wires.submobjects):
            if condition(
                wire.start in terminals,
                wire.end in terminals,
            ):
                to_remove.append(wire)
        return to_remove

    def __check_terminals_all_belong_to_this_circuit(
        self, terminals: list[Terminal]
    ) -> None:
        terminal_set = set(terminals)
        owned_terminal_set = set()
        for component in self.elements:
            owned_terminal_set.update(component.terminals)

        terminals_not_owned = terminal_set.difference(owned_terminal_set)
        if len(terminals_not_owned) != 0:
            raise ValueError(
                f"At least one passed terminal does not "
                f"belong to any component in this circuit. "
                f"Problem terminals have the following end coordinates: "
                f"{[tuple(terminal.end) for terminal in terminals_not_owned]}"
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
        start: Terminal,
        end: Terminal,
        anim_args: dict[str, Any] | None = None,
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}

        self.__check_terminals_all_belong_to_this_circuit([start, end])
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
        *components_or_terminals: Component | Terminal,
        anim_args: dict[str, Any] | None = None,
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}

        terminals = self._collapse_components_and_terminals_to_terminals(
            components_or_terminals
        )
        self.__check_terminals_all_belong_to_this_circuit(terminals)
        to_remove = self.__get_wires_from_terminal_condition(
            terminals, lambda start, end: start and end
        )
        animations = [mn.Uncreate(wire, **anim_args) for wire in to_remove]
        self.wires.remove(*to_remove)

        node_update_animation = self.nodes.animate(**anim_args).update().build()
        animations.append(node_update_animation)

        return mn.AnimationGroup(*animations)

    @mn.override_animate(isolate)
    def __animate_isolate(
        self,
        *components_or_terminals: Component | Terminal,
        anim_args: dict[str, Any] | None = None,
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}

        terminals = self._collapse_components_and_terminals_to_terminals(
            components_or_terminals
        )
        self.__check_terminals_all_belong_to_this_circuit(terminals)
        to_remove = self.__get_wires_from_terminal_condition(
            terminals, lambda start, end: start or end
        )
        animations = [mn.Uncreate(wire, **anim_args) for wire in to_remove]
        self.wires.remove(*to_remove)

        node_update_animation = self.nodes.animate(**anim_args).update().build()
        animations.append(node_update_animation)

        return mn.AnimationGroup(*animations)
