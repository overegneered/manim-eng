"""Module containing the Circuit class."""

from typing import Any, Callable, Self, Sequence, cast

import manim as mn

__all__ = ["Circuit"]

from manim_eng._base.component import Component
from manim_eng._base.terminal import Terminal
from manim_eng.circuit.wire import Wire


class Circuit(mn.VMobject):
    """Circuit manager to conveniently handle components and their connections.

    Parameters
    ----------
    *components : Component
        Components to add to the circuit at initialisation.
    """

    def __init__(self, *components: Component) -> None:
        super().__init__()

        self.components = mn.VGroup()
        self.connections = mn.VGroup()
        super().add(self.components, self.connections)

        self.add(*components)

    def add(self, *components: Component) -> Self:
        """Add one or more components to the circuit.

        Parameters
        ----------
        *components : Component
            The component(s) to add.

        Returns
        -------
        Self
            The circuit on which this method was called.
        """
        for component in components:
            # Update here to make sure that all marks are properly aligned
            component.update()
            self.components.add(component)
        return self

    def remove(self, *components: Component) -> Self:
        """Remove one or more components from the circuit.

        Parameters
        ----------
        *components : Component
            The component(s) to remove.

        Returns
        -------
        Self
            The circuit on which this method was called.
        """
        self.components.remove(*components)
        return self

    def connect(self, from_terminal: Terminal, to_terminal: Terminal) -> Self:
        """Connect two terminals together.

        Parameters
        ----------
        from_terminal : Terminal
            The terminal the connecting wire should start at.
        to_terminal : Terminal
            The terminal the connecting wire should end at.

        Returns
        -------
        Self
            The circuit on which this method was called.
        """
        self.connections.add(Wire(from_terminal, to_terminal))
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

        Returns
        -------
        Self
            The circuit on which this method was called.

        See Also
        --------
        isolate : Remove a wire if either of its ends is specified.
        """
        terminals = self.__collapse_components_and_terminals_to_terminals(
            components_or_terminals
        )
        to_remove = self.__get_wires_from_terminal_condition(
            terminals, lambda start, end: start and end
        )
        self.connections.remove(*to_remove)
        return self

    def isolate(self, *components_or_terminals: Component | Terminal) -> Self:
        """Remove all wires attached to each given terminal or component.

        Each wire is checked to see if either of its ends is a passed terminal or a
        terminal on a passed component. If this is the case, the wire will be removed.

        Parameters
        ----------
        *components_or_terminals : Component | Terminal
            The components and terminals to completely disconnect from the circuit.

        Returns
        -------
        Self
            The circuit on which this method was called.

        See Also
        --------
        disconnect : Remove a wire if both its ends are specified.
        """
        terminals = self.__collapse_components_and_terminals_to_terminals(
            components_or_terminals
        )
        to_remove = self.__get_wires_from_terminal_condition(
            terminals, lambda start, end: start or end
        )
        self.connections.remove(*to_remove)
        return self

    @staticmethod
    def __collapse_components_and_terminals_to_terminals(
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
        for connection in cast(list[Wire], self.connections.submobjects):
            if condition(
                connection.from_terminal in terminals,
                connection.to_terminal in terminals,
            ):
                to_remove.append(connection)
        return to_remove

    @mn.override_animate(connect)
    def __animate_connect(
        self,
        from_terminal: Terminal,
        to_terminal: Terminal,
        anim_args: dict[str, Any] | None = None,
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}

        new_wire = Wire(from_terminal, to_terminal)
        self.connections.add(new_wire)
        return mn.Create(new_wire, **anim_args)

    @mn.override_animate(disconnect)
    def __animate_disconnect(
        self,
        *components_or_terminals: Component | Terminal,
        anim_args: dict[str, Any] | None = None,
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}

        terminals = self.__collapse_components_and_terminals_to_terminals(
            components_or_terminals
        )
        to_remove = self.__get_wires_from_terminal_condition(
            terminals, lambda start, end: start and end
        )
        animations = [mn.Uncreate(wire, **anim_args) for wire in to_remove]
        self.connections.remove(*to_remove)

        return mn.AnimationGroup(*animations)

    @mn.override_animate(isolate)
    def __animate_isolate(
        self,
        *components_or_terminals: Component | Terminal,
        anim_args: dict[str, Any] | None = None,
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}

        terminals = self.__collapse_components_and_terminals_to_terminals(
            components_or_terminals
        )
        to_remove = self.__get_wires_from_terminal_condition(
            terminals, lambda start, end: start or end
        )
        animations = [mn.Uncreate(wire, **anim_args) for wire in to_remove]
        self.connections.remove(*to_remove)

        return mn.AnimationGroup(*animations)
