"""Nodes for wire routing and display of circuit pins and solder blobs."""

from typing import Any, Self, cast

import manim as mn
import manim.typing as mnt
import numpy as np

from manim_eng import config_eng
from manim_eng._base.mark import Mark
from manim_eng.components.base.component import Component
from manim_eng.components.base.pin import Pin

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
    """Circuit symbol for a node (open/filled terminal or wire-routing aid).

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
        Autoblobbing will add a solder blob automatically if more than two wires into
        the node are visible or the label is shown.
    label_pos : manim.Vector3D, optional
        Where the node label should be placed. If left unspecified, the label is
        automatically placed where it will fit best.
    """

    def __init__(
        self,
        open_: bool = False,
        autoblob: bool = True,
        label_pos: mnt.Vector3D | None = None,
        **kwargs: Any,
    ):
        self._open = open_
        self._autoblob = autoblob if not open_ else False
        self._manual_label_pos = label_pos

        self.__blob: mn.Dot

        super().__init__(pins=[], **kwargs)
        self.remove(self._annotation_anchor)

        if self._autoblob:
            self.add_updater(self.__blob_updater)
            self.update()
        self._reposition_label_anchor(label_pos)

    def _construct(self) -> None:
        super()._construct()

        self.__blob = _create_node_blob(self, self._open)
        self._body.add(self.__blob)

    @property
    def annotation(self) -> Mark:
        """Nodes do not have annotations.

        **THIS WILL FAIL.**
        """
        raise NotImplementedError(
            "`Node`s have no annotations. Please use `label` instead."
        )

    def get(self, direction: mnt.Vector3D | float) -> Pin:
        """Get a pin on the node in a given direction, creating it if necessary.

        Parameters
        ----------
        direction : mnt.Vector3D | float
            The direction to get the pin in, as either a direction vector or an angle
            in radians. Note that the angle is defined as is mathematical standard:
            measured anticlockwise from the positive horizontal.

        Returns
        -------
        Pin
            The pin on the node in the specified direction.

        See Also
        --------
        clear
        right, up, left, down, up_right, up_left, down_left, down_right
        """
        direction = self._get_normalised_direction(direction)

        for pin in self.pins:
            if np.allclose(pin.direction, direction):
                to_return = pin
                break
        else:
            to_return = Pin(
                position=self.get_center(),
                direction=direction,
                parent=self,
            )
            self._pins.add(to_return)

        return to_return

    @property
    def right(self) -> Pin:
        """Get the right-pointing pin of the node, creating it if necessary."""
        return self.get(mn.RIGHT)

    @property
    def up(self) -> Pin:
        """Get the up-pointing pin of the node, creating it if necessary."""
        return self.get(mn.UP)

    @property
    def left(self) -> Pin:
        """Get the left-pointing pin of the node, creating it if necessary."""
        return self.get(mn.LEFT)

    @property
    def down(self) -> Pin:
        """Get the down-pointing pin of the node, creating it if necessary."""
        return self.get(mn.DOWN)

    @property
    def up_right(self) -> Pin:
        """Get the up-right-pointing pin of the node, creating it if necessary."""
        return self.get(mn.UR)

    @property
    def up_left(self) -> Pin:
        """Get the up-left-pointing pin of the node, creating it if necessary."""
        return self.get(mn.UL)

    @property
    def down_left(self) -> Pin:
        """Get the down-left-pointing pin of the node, creating it if necessary."""
        return self.get(mn.DL)

    @property
    def down_right(self) -> Pin:
        """Get down-right-pointing pin of the node, creating it if necessary."""
        return self.get(mn.DR)

    @property
    def connected_pins(self) -> list[Pin]:
        """Get the pins of this node that are currently attached to wires."""
        return [pin for pin in self.pins if pin.wire_currently_attached()]

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
        self._autoblob = autoblob
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

    def set_label_direction(self, direction: mnt.Vector3D) -> Self:
        """Set the direction the label should be placed in.

        Will disable automatic label placement.

        Parameters
        ----------
        direction : mnt.Vector3D
            The direction the label should be placed in.

        See Also
        --------
        enable_automatic_label_placement
        """
        self._reposition_label_anchor(direction)
        return self

    def enable_automatic_label_placement(self) -> Self:
        """Make the label place itself automatically.

        See Also
        --------
        set_label_direction
        """
        self._reposition_label_anchor(None)
        return self

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
        pins originate (the centre of the node circle/blob).
        """
        return self.__blob.get_center()

    def next_to(
        self,
        mobject_or_point: Pin | mn.Mobject | mnt.Point3DLike,
        direction: mnt.Vector3D | None = None,
        buff: float = mn.DEFAULT_MOBJECT_TO_MOBJECT_BUFFER,
        aligned_edge: mnt.Vector3D = mn.ORIGIN,
        submobject_to_align: mn.Mobject | None = None,
        index_of_submobject_to_align: int | None = None,
        coor_mask: mnt.Vector3D | None = None,
    ) -> Self:
        """Move this node next to another pin, mobject, or point.

        Operates much as :meth:`manim.mobject.mobject.Mobject.next_to` does, but with
        added ability to handle :class:`~.Pin` objects.

        Parameters
        ----------
        mobject_or_point : Pin | Mobject | Point3DLike
            The target to place this node next to. If a :class:`~.Pin` is passed, its
            tip position is used as the reference point, and (unless ``direction`` is
            given explicitly) its outward direction is used as the placement direction.
        direction : Vector3D | None, optional
            The direction from ``mobject_or_point`` in which this node is placed.
            Defaults to the pin's outward direction when a :class:`~.Pin` is passed,
            or :attr:`manim.RIGHT` when ``None`` is passed or no value is given.
            Supplying this argument always overrides the pin's direction.

        See Also
        --------
        :meth:`manim.mobject.mobject.Mobject.next_to`.
        """
        point: mn.Mobject | mnt.Point3DLike
        if isinstance(mobject_or_point, Pin):
            if direction is None:
                direction = mobject_or_point.direction
            point = mobject_or_point.tip
        else:
            point = mobject_or_point

        if direction is None:
            direction = mn.RIGHT
        if coor_mask is None:
            coor_mask = np.array([1, 1, 1])

        return super().next_to(  # type: ignore[no-any-return]  # Manim lacks stubs
            point,
            direction,
            buff,
            aligned_edge,
            submobject_to_align,
            index_of_submobject_to_align,
            coor_mask,
        )

    def _set_blob_visibility(self, visible: bool) -> Self:
        self.__blob.set_opacity(1.0 if visible else 0.0)
        return self

    def _get_normalised_direction(
        self, direction: mnt.Vector3D | float
    ) -> mnt.Vector3D:
        if isinstance(direction, float):
            return mn.rotate_vector(mn.RIGHT, direction)
        return mn.normalize(direction)

    @staticmethod
    def __blob_updater(mobject: mn.Mobject) -> None:
        node = cast(Node, mobject)
        node._set_blob_visibility(node._should_be_visible())

    def _should_be_visible(self) -> bool:
        """Return if there are more than 2 visible wires or the label is visible."""
        visible_pin_count = sum(pin.is_visible() for pin in self.pins)
        pins_above_threshold = visible_pin_count > AUTOBLOBBING_BLOB_THRESHOLD
        return pins_above_threshold or self._label.is_visible()

    def _reposition_label_anchor(self, direction: mnt.Vector3D | float | None) -> None:
        """Set the anchor using direction if given, otherwise enable the updater."""
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
    def __label_anchor_updater(mobject: mn.Mobject) -> None:
        node = cast(Node, mobject)
        new_direction = node._get_optimal_label_anchor_direction()
        node._update_label_positioning_using_vector(new_direction)

    def _get_optimal_label_anchor_direction(self) -> mnt.Vector3D:
        pin_angles = self._get_visible_pin_angles()
        angles = self._midangles_of_largest_gaps_between_list_of_angles(pin_angles)
        return self._topmost_angle_as_direction(angles)

    def _update_label_positioning_using_vector(self, direction: mnt.Vector3D) -> None:
        position = self.get_center() + config_eng.symbol.node_radius * direction
        self._label_anchor.move_to(position)
        self._label.update()

    def _get_visible_pin_angles(self) -> list[float]:
        return sorted(
            mn.angle_of_vector(pin.direction) for pin in self.pins if pin.is_visible()
        )

    @staticmethod
    def _topmost_angle_as_direction(angles: list[float]) -> mnt.Vector3D:
        if len(angles) == 0:
            return mn.UP

        angles.sort(key=np.sin, reverse=True)
        angle = angles[0]
        return mn.rotate_vector(mn.RIGHT, angle)

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


class OpenNode(Node):
    """Circuit symbol for an open terminal.

    A utility wrapper around the ``Node`` class that sets the ``open_`` parameter to
    ``True`` automatically.

    See Also
    --------
    Node
    """

    def __init__(self, **kwargs: Any):
        super().__init__(open_=True, **kwargs)
