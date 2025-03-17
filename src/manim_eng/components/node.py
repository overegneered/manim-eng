"""Nodes for wire routing and display of circuit terminals and solder blobs."""

from typing import Any, Self, cast

import manim as mn
import manim.typing as mnt
import numpy as np

from manim_eng import config_eng
from manim_eng.components.base.component import Component
from manim_eng.components.base.terminal import Terminal
from manim_eng.units import Value

__all__ = ["Node", "OpenNode"]

AUTOBLOBBING_BLOB_THRESHOLD = 2
BLOB_Z_INDEX = 10


# Allows switch components to get an identical shape without bringing in all the extra
# baggage of the full Node class (anchors etc.)
def _create_node_blob(match_to: Component, open_: bool) -> mn.Dot:
    return mn.Dot(
        radius=config_eng.symbol.node_radius,
        stroke_width=config_eng.symbol.wire_stroke_width,
        stroke_color=match_to.color,
        fill_opacity=1.0,
        fill_color=mn.config.background_color if open_ else match_to.color,
        z_index=BLOB_Z_INDEX,
    )


class Node(Component):
    """Node in a circuit and open/filled terminal circuit symbol.

    ``Node`` handles two main purposes: it displays node symbols (open terminal symbols
    and solder blobs), and serves as an aid for wire routing, particularly when paired
    with updaters.

    Parameters
    ----------
    open_ : bool
        Whether to display an open or filled circle for the node. Open ones are
        typically used for external connections to a circuit (i.e. loose ends), whereas
        filled ones are used for 'solder blobs' to indicated that three or more wires
        connect.
    autoblob : bool
        Whether to handle the addition/removal of solder blobs automatically. Has no
        effect if the node is open (as autoblobbing only makes sense for solder blobs).
    """

    def __init__(self, open_: bool = False, autoblob: bool = True, **kwargs: Any):
        self.open = open_
        self.autoblob = autoblob if not open_ else False

        self.__blob: mn.Dot

        super().__init__(terminals=[], **kwargs)

        if self.autoblob:
            self.add_updater(self.__blob_updater)
            self.update()

        self.remove(self._annotation_anchor)

    def _construct(self) -> None:
        super()._construct()

        self.__blob = _create_node_blob(self, self.open)
        self._body.add(self.__blob)

    def set_label(
        self, label: str | Value, direction: mnt.Vector3D | float | None = None
    ) -> Self:
        """Set the label of the node, optionally specifying where it should be.

        The ``direction`` parameter can be used to specify the position the label should
        take. If it is left unspecified, the node will identify the most logical
        position for it (the widest gap between terminals) and keep the label here, with
        ties being broken by the uppermost position being favoured. This will continue
        to happen as terminals are added/removed.

        Parameters
        ----------
        label : str
            The label to set. Takes a TeX math mode string, or a ``Value`` to be typeset
            as a math mode string.
        direction : Vector3D | float | None
            The direction in which to place the label. Can either be a direction vector
            (``Vector3D``), an angle in radians (``float``), or ``None``, which
            signifies that the label should be placed automatically.
        """
        self._reposition_label_anchor(direction)
        super().set_label(label)
        return self

    def set_annotation(self, annotation: str | Value) -> Self:
        """Fails for nodes, as they do not have annotations."""
        raise NotImplementedError(
            "Nodes have no annotation. Please use `.set_label()`."
        )

    def clear_annotation(self) -> Self:
        """Fails for nodes, as they do not have annotations."""
        raise NotImplementedError(
            "Nodes have no annotation. Please use `.clear_label()`."
        )

    def get(self, direction: mnt.Vector3D | float) -> Terminal:
        """Get a terminal of the node in a given direction, creating it if necessary.

        Parameters
        ----------
        direction : mnt.Vector3D | float
            The direction to get a terminal in, as either a direction vector or an angle
            in radians. Note that the angle is defined as is mathematical standard:
            measured anticlockwise from the positive horizontal.

        Returns
        -------
        Terminal
            The terminal on the node in the specified direction.

        See Also
        --------
        clear
        right, up, left, down, up_right, up_left, down_left, down_right
        """
        direction = self._get_normalised_direction(direction)

        for terminal in self.terminals:
            if np.allclose(terminal.direction, direction):
                to_return = terminal
                break
        else:
            to_return = Terminal(
                position=self.get_center(),
                direction=direction,
                auto=True,
            ).match_style(self)
            self._terminals.add(to_return)

        return to_return

    @property
    def right(self) -> Terminal:
        """Get the right-pointing terminal of the node, creating it if necessary."""
        return self.get(mn.RIGHT)

    @property
    def up(self) -> Terminal:
        """Get the up-pointing terminal of the node, creating it if necessary."""
        return self.get(mn.UP)

    @property
    def left(self) -> Terminal:
        """Get the left-pointing terminal of the node, creating it if necessary."""
        return self.get(mn.LEFT)

    @property
    def down(self) -> Terminal:
        """Get the down-pointing terminal of the node, creating it if necessary."""
        return self.get(mn.DOWN)

    @property
    def up_right(self) -> Terminal:
        """Get the up-right-pointing terminal of the node, creating it if necessary."""
        return self.get(mn.UR)

    @property
    def up_left(self) -> Terminal:
        """Get the up-left-pointing terminal of the node, creating it if necessary."""
        return self.get(mn.UL)

    @property
    def down_left(self) -> Terminal:
        """Get the down-left-pointing terminal of the node, creating it if necessary."""
        return self.get(mn.DL)

    @property
    def down_right(self) -> Terminal:
        """Get down-right-pointing terminal of the node, creating it if necessary."""
        return self.get(mn.DR)

    def set_blob_visibility(self, visible: bool) -> Self:
        """Alter the solder blob visibility.

        This will disable autoblobbing, as otherwise there would be two competing
        sources of truth on whether a blob should be displayed or not.

        Parameters
        ----------
        visible : bool
            Whether the solder blob should be visible.

        See Also
        --------
        show_blob
        hide_blob
        """
        self._set_blob_visibility(visible)
        self.disable_autoblobbing()
        return self

    def show_blob(self) -> Self:
        """Make the solder blob visible.

        This will disable autoblobbing, as otherwise there would be two competing
        sources of truth on whether a blob should be displayed or not.

        See Also
        --------
        set_blob_visibility
        hide_blob
        """
        return self.set_blob_visibility(visible=True)

    def hide_blob(self) -> Self:
        """Make the solder blob invisible.

        This will disable autoblobbing, as otherwise there would be two competing
        sources of truth on whether a blob should be displayed or not.

        See Also
        --------
        set_blob_visibility
        show_blob
        """
        return self.set_blob_visibility(visible=False)

    def set_autoblobbing(self, autoblob: bool) -> Self:
        """Specify whether the node should autoblob or not.

        If used to enable autoblobbing, an autoblob calculation will be made to decide
        whether to display the blob or not. Will not have an effect if the node is of an
        open type.

        Parameters
        ----------
        autoblob : bool
            Whether the node should autoblob or not.

        See Also
        --------
        enable_autoblobbing
        disable_autoblobbing
        """
        self.autoblob = autoblob
        if autoblob:
            if self.__blob_updater not in self.updaters:
                self.add_updater(self.__blob_updater)
            self.update()
        else:
            self.remove_updater(self.__blob_updater)
        return self

    def enable_autoblobbing(self) -> Self:
        """Enable autoblobbing for the node.

        If the node is of a filled type, an autoblob calculation will be made to decide
        whether to display the blob or not, and the node display updated accordingly.
        Will not have an effect if the node is of an open type.

        See Also
        --------
        set_autoblobbing
        disable_autoblobbing
        """
        return self.set_autoblobbing(True)

    def disable_autoblobbing(self) -> Self:
        """Disable autoblobbing for the node.

        Will not have an effect if the node is of an open type.

        See Also
        --------
        set_autoblobbing
        enable_autoblobbing
        """
        return self.set_autoblobbing(False)

    def make_open(self, make_visible: bool = True) -> Self:
        """Set the type of the node to open (an empty circle).

        Autoblobbing will be automatically disabled by this call. By default, it will
        also make the node symbol appear (i.e. an unfilled circle), regardless of
        whether it was showing before. Use the ``make_visible`` parameter to adjust this
        behaviour.

        Parameters
        ----------
        make_visible : bool
            Whether the open node symbol should be forced to become visible by this
            call. Note that a value of ``False`` will *not* force the node symbol to be
            invisible, but the symbol will maintain its previous visiblity. Defaults to
            ``True``.

        See Also
        --------
        make_filled
        """
        self.__blob.set_fill(color=mn.config.background_color)
        self.disable_autoblobbing()
        if make_visible:
            self.show_blob()
        return self

    def make_filled(self, reenable_autoblobbing: bool = True) -> Self:
        """Set the type of the node to filled (a filled solder blob, i.e. circle).

        By default, this call will automatically re-enable autoblobbing. To disable this
        behaviour, use the ``reenable_autoblobbing`` parameter.

        Parameters
        ----------
        reenable_autoblobbing : bool
            Whether to re-enable autoblobbing with this call. Defaults to ``True``.

        See Also
        --------
        make_open
        """
        self.__blob.set_fill(color=self.color)
        if reenable_autoblobbing:
            self.enable_autoblobbing()
        return self

    def get_center(self) -> mnt.Point3D:
        """Get the centre of the node.

        Note that this is not the geometric centre, but rather the point from which
        terminals originate (the centre of the node circle/blob).
        """
        return self.__blob.get_center()

    def _set_blob_visibility(self, visible: bool) -> Self:
        self.__blob.set_opacity(1.0 if visible else 0.0)
        return self

    def _get_normalised_direction(
        self, direction: mnt.Vector3D | float
    ) -> mnt.Vector3D:
        if isinstance(direction, float):
            return mn.rotate_vector(mn.RIGHT, direction)
        return mn.normalize(direction)

    def _should_be_visible(self) -> bool:
        visible_terminal_count = sum(
            [terminal.is_visible() for terminal in self.terminals]
        )
        return visible_terminal_count > AUTOBLOBBING_BLOB_THRESHOLD

    def _get_visible_terminal_angles(self) -> list[float]:
        return sorted(
            [
                mn.angle_of_vector(terminal.direction)
                for terminal in self.terminals
                if terminal.is_visible()
            ]
        )

    @staticmethod
    def _midangles_of_largest_gaps_between_list_of_angles(
        angles: list[float],
    ) -> list[float]:
        largest_gap = 0.0
        midangles: list[float] = []
        for start_angle, end_angle in zip(np.roll(angles, 1), angles, strict=False):
            if end_angle <= start_angle:
                # This comparison occurs over the 'break' at ±pi, or there is only one
                # element in `angles`. Either way, we get the behaviour we want by
                # adding 2 pi
                end_angle += 2 * np.pi  # noqa: PLW2901

            gap = end_angle - start_angle
            if gap < largest_gap and not np.isclose(gap, largest_gap):
                continue

            if gap > largest_gap:
                largest_gap = gap
                midangles = []

            centre_angle = 0.5 * (start_angle + end_angle)
            if centre_angle > np.pi:
                centre_angle -= 2 * np.pi
            midangles.append(centre_angle)

        return sorted(midangles)

    @staticmethod
    def _topmost_angle_as_direction(angles: list[float]) -> mnt.Vector3D:
        if len(angles) == 0:
            return mn.UP

        angles.sort(key=lambda x: np.sin(x), reverse=True)
        angle = angles[0]
        return mn.rotate_vector(mn.RIGHT, angle)

    def _get_optimal_label_anchor_direction(self) -> mnt.Vector3D:
        terminal_angles = self._get_visible_terminal_angles()
        angles = self._midangles_of_largest_gaps_between_list_of_angles(terminal_angles)
        return self._topmost_angle_as_direction(angles)

    def _update_label_positioning_using_vector(self, direction: mnt.Vector3D) -> None:
        position = self.get_center() + config_eng.symbol.node_radius * direction
        self._label_anchor.move_to(position)
        self._label.update()

    def _reposition_label_anchor(self, direction: mnt.Vector3D | float | None) -> None:
        if direction is None:
            if self.__label_anchor_updater not in self.updaters:
                self.add_updater(self.__label_anchor_updater)
            self.update()
        else:
            if self.__label_anchor_updater in self.updaters:
                self.remove_updater(self.__label_anchor_updater)
            direction = self._get_normalised_direction(direction)
            self._update_label_positioning_using_vector(direction)

    @staticmethod
    def __blob_updater(mobject: mn.Mobject) -> None:
        node = cast(Node, mobject)
        node._set_blob_visibility(node._should_be_visible())

    @staticmethod
    def __label_anchor_updater(mobject: mn.Mobject) -> None:
        node = cast(Node, mobject)
        new_direction = node._get_optimal_label_anchor_direction()
        node._update_label_positioning_using_vector(new_direction)

    @mn.override_animate(set_label)
    def __animate_set_label(
        self,
        label: str,
        direction: mnt.Vector3D | float | None = None,
        anim_args: dict[str, Any] | None = None,
    ) -> mn.Animation:
        self._reposition_label_anchor(direction)
        return self.animate(**anim_args)._set_mark(self._label, label).build()


class OpenNode(Node):
    """Open node circuit symbol.

    A utility wrapper around the ``Node`` class that sets the ``open_`` parameter to
    ``True`` automatically.

    See Also
    --------
    Node
    """

    def __init__(self, **kwargs: Any):
        super().__init__(open_=True, **kwargs)
