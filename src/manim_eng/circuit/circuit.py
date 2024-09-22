"""Module containing the Circuit class."""

from typing import Self

import manim as mn

__all__ = ["Circuit"]

from manim_eng._base.component import Component


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
        for component in [*components]:
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
