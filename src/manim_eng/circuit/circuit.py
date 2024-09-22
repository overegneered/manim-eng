"""Module containing the Circuit class."""

from typing import Self

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

    def disconnect(self, *terminals: Terminal) -> Self:
        """Disconnect the given terminals from one another.

        Each wire is checked to see if *both* the start *and* end terminals are in the
        group of terminals passed. If this is the case, the wire will be removed.

        Parameters
        ----------
        *terminals : Terminal
            The group of terminals to disconnect from one another.

        Returns
        -------
        Self
            The circuit on which this method was called.

        See Also
        --------
        isolate : Remove a wire if either of its terminals is given.
        """
        for connection in self.connections.submobjects:
            if (
                connection.from_terminal in terminals
                and connection.to_terminal in terminals
            ):
                self.connections.remove(connection)
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
        disconnect : Remove a wire if both its terminals are given.
        """
        terminals_to_disconnect = []
        for component_or_terminal in components_or_terminals:
            if isinstance(component_or_terminal, Component):
                terminals_to_disconnect.extend(component_or_terminal.terminals)
            else:
                terminals_to_disconnect.append(component_or_terminal)

        # Remove duplicate entries
        terminals_to_disconnect = list(set(terminals_to_disconnect))

        for connection in self.connections.submobjects:
            if (
                connection.from_terminal in terminals_to_disconnect
                or connection.to_terminal in terminals_to_disconnect
            ):
                self.connections.remove(connection)

        return self
