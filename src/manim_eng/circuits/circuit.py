"""Contains the Circuit class."""

from typing import Any, Callable, Literal, Self, Sequence, cast

import manim as mn
import manim.typing as mnt
import numpy as np
from scipy.cluster.hierarchy import DisjointSet

__all__ = ["Circuit"]

from manim_eng.circuits.wire import ManualWire, Wire
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

    def connect(
        self,
        start: Terminal,
        end: Terminal,
        guide: Sequence[mnt.Point3D] | None = None,
        enforce_hv: bool = True,
    ) -> Self:
        """Connect two terminals together.

        Parameters
        ----------
        start : Terminal
            The terminal the connecting wire should start at.
        end : Terminal
            The terminal the connecting wire should end at.
        guide : Sequence[mnt.Point3D] | None
            If set to a sequence of points, the connection is drawn manually via the
            ``ManualWire`` class, with the list of points as the corner points to go
            through.
            If set to ``None``, the connection is drawn automatically via the ``Wire``
            class.
        enforce_hv : bool
            If the ``manual`` field is not None and ``enforce_hv`` is set to ``True``,
            the function will  to enforce all wires to be either horizontal or vertical,
            by shifting the given points. The function ensures that each segment of the
            wire alternates between horizontal and vertical.
            The direction of the starting and ending terminal determines the direction
            of the first and the last wire. If the starting and ending conditions cannot
            be met, the function will insert one extra point(s) to the list.
            If ``enforce_hv`` is False, the function will connect the consecutive points
            given in ``guide`` directly.

        Raises
        ------
        ValueError
            If the two terminals passed are identical.
        ValueError
            If either terminal doesn't belong to a component in this circuit.
        """
        self.__check_terminals_all_belong_to_this_circuit([start, end])
        if guide is not None:
            if enforce_hv:
                guide = self.__enforce_wire_horizontal_and_vertical(start, end, guide)
            self.wires.add(ManualWire(start, end, corner_points=guide).attach())
        else:
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

    def get_wires(
        self,
        *terminals: Terminal,
        condition: Literal["start", "end", "both", "either"]
        | Callable[[bool, bool], bool] = "either",
    ) -> list[Wire]:
        """Return a list of wires based on the given conditions.

        This function iterates through all wires in the circuit and returns wires that
        satisfies the following properties:

        - If the condition is "start", the wire's start terminal is in the list of
          terminals given to the function.
        - If the condition is "end", the wire's end terminal is in the list of terminals
          given to the function.
        - If the condition is "either", then all wires with either start or end terminal
          in the list will be returned.
        - If the condition is "both", then only wires whose start and end terminals are
          both in the list will be returned.

        The condition can also be set as a function that takes in two variables,
        ``start`` and ``end``, and returns a boolean value, representing whether the
        wire should be selected.

        Parameters
        ----------
        terminals : Sequence[Terminal]
            The list of terminals to check against.
        condition : str | Callable[[Terminal, Terminal], bool]
            The condition to check against. If a string is given, it must be one of
            "start", "end", "either", or "both". If a function is given, it must take
            in two variables, ``start`` and ``end``, and return a boolean value.

        Raises
        ------
        ValueError
            If the condition is not a function, "start", "end", "either", or "both".
        """
        if isinstance(condition, str):
            if condition == "start":
                return self.__get_wires_from_terminal_condition(
                    terminals, lambda start, _: start
                )
            if condition == "end":
                return self.__get_wires_from_terminal_condition(
                    terminals, lambda _, end: end
                )
            if condition == "either":
                return self.__get_wires_from_terminal_condition(
                    terminals, lambda start, end: start or end
                )
            if condition == "both":
                return self.__get_wires_from_terminal_condition(
                    terminals, lambda start, end: start and end
                )
            raise ValueError(f"Unrecognized condition in `get_wires`: {condition}")
        return self.__get_wires_from_terminal_condition(terminals, condition)

    def get_network(self, element: Terminal | Node | Wire) -> set[Wire | Node]:
        """Get the network (wires and nodes) that contains the given element.

        This function assumes that all wires are undirected, i.e. it does not
        distinguish between the start and end of wires.

        Parameters
        ----------
        element : Terminal | Node | Wire
            The element to get the network of.

        Returns
        -------
        set[Wire | Node]
            The network components (wires and nodes) containing / originating from the
            given element.

        Raises
        ------
        ValueError
            If the given element is not a terminal, node, or wire.
        """
        s: DisjointSet[Wire | Node] = DisjointSet()
        for wire in self.wires.submobjects:
            s.add(wire)
        for node in self.nodes.submobjects:
            # Merge all wires connecting to the same node
            node = cast(Node, node)
            s.add(node)
            all_connected_wires = self.get_wires(*node.terminals)
            for i in range(len(all_connected_wires)):
                s.merge(node, all_connected_wires[i])
        if isinstance(element, Wire | Node):
            # Directly return the set containing this elemenet
            return cast(set[Wire | Node], s.subset(element))
        if isinstance(element, Terminal):
            # s is a terminal. Return the union of all sets containing the wires
            # connected to the terminal
            wires = self.get_wires(element)
            ans: set[Wire | Node] = set()
            for wire in wires:
                ans = ans.union(s.subset(wire))
            return ans
        raise ValueError(f'"{element}" must be either a terminal, a node, or a wire!')

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

    def __enforce_wire_horizontal_and_vertical(
        self, start: Terminal, end: Terminal, guide: Sequence[mnt.Point3D]
    ) -> list[mnt.Point3D]:
        # TODO: More elegant way to implement this?
        # TODO: Probably integrate this function with functions used in wire.py?
        guide = list(guide)
        # Enforce that all segments are horizontal or vertical
        start_vertical = abs(start.direction[0]) < abs(
            start.direction[1]
        )  # False for horizontal, True for vertical
        end_vertical = abs(start.direction[0]) < abs(start.direction[1])
        current_vertical = start_vertical
        last_point = start.end
        if start_vertical ^ end_vertical != bool(len(guide) % 2):
            # guide is not long enough to enforce the requirement
            guide.append(np.zeros(3))
        for point in guide:
            if current_vertical:
                point[0] = last_point[0]
            else:
                point[1] = last_point[1]
            current_vertical = not current_vertical
            last_point = point
        if current_vertical:
            guide[-1][0] = end.end[0]
        else:
            guide[-1][1] = end.end[1]
        return guide

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
        guide: Sequence[mnt.Point3D] | None = None,
        enforce_hv: bool = True,
        anim_args: dict[str, Any] | None = None,
    ) -> mn.Animation:
        if anim_args is None:
            anim_args = {}

        self.__check_terminals_all_belong_to_this_circuit([start, end])
        if guide is not None:
            if enforce_hv:
                guide = self.__enforce_wire_horizontal_and_vertical(start, end, guide)
            new_wire = ManualWire(start, end, corner_points=guide).attach()
        else:
            new_wire = Wire(start, end).attach()
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
