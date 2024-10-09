"""Nodes for wire routing and display of circuit terminals and solder blobs."""

from typing import Any, Self

import manim as mn
import manim.typing as mnt
import numpy as np

from manim_eng import config_eng
from manim_eng.components.base import Component, Terminal

__all__ = ["Node", "OpenNode"]

AUTOBLOBBING_BLOB_THRESHOLD = 2


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

    def _construct(self) -> None:
        super()._construct()

        self.__blob = mn.Dot(
            radius=config_eng.symbol.node_radius,
            stroke_width=config_eng.symbol.wire_stroke_width,
            stroke_color=self.color,
            fill_opacity=1.0,
            fill_color=mn.config.background_color if self.open else self.color,
            z_index=10,
        )
        self._body.add(self.__blob)

        self._autoblob_if_autoblobbing()

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
            The terminal on the node in the specifed direction.
        """
        if isinstance(direction, float):
            direction = mn.rotate_vector(mn.RIGHT, direction)
        else:
            direction = mn.normalize(direction)

        for terminal in self.terminals:
            if np.allclose(terminal.direction, direction):
                to_return = terminal
                break
        else:
            to_return = Terminal(
                position=self.get_center(),
                direction=direction,
            ).match_style(self)
            self._terminals.add(to_return)

            self._autoblob_if_autoblobbing()

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
        self._autoblob_if_autoblobbing()
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

    def set_open(self, open_: bool, reenable_autoblobbing: bool = True) -> Self:
        """Set the type of the node (open or filled).

        If the node type is set to open, autoblobbing will be automatically disabled. If
        set to filled, autoblobbing will be automatically enabled if
        ``reenable_autoblobbing`` is ``True``.

        Parameters
        ----------
        open_ : bool
            Whether the node should be open (``True``) or filled (``False``).
        reenable_autoblobbing : bool
            Whether autoblobbing should be automatically re-enabled in the case the node
            is being set to filled. Defaults to ``True`` (automatic re-enablement). Only
            has an effect if the node is being set to filled.

        See Also
        --------
        make_open
        make_filled
        """
        self.__blob.set_fill(color=mn.config.background_color if open_ else self.color)
        self.open = open_
        if open_:
            self.disable_autoblobbing()
        elif reenable_autoblobbing:
            self.enable_autoblobbing()
        return self

    def make_open(self) -> Self:
        """Set the type of the node to open (an empty circle).

        Autoblobbing will be automatically disabled by this call.

        See Also
        --------
        set_open
        make_filled
        """
        return self.set_open(open_=True)

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
        set_open
        make_open
        """
        return self.set_open(open_=False, reenable_autoblobbing=reenable_autoblobbing)

    def get_center(self) -> mnt.Point3D:
        """Get the centre of the node.

        Note that this is not the geometric centre, but rather the point from which
        terminals originate (the centre of the node circle/blob).
        """
        return self.__blob.get_center()

    def _set_blob_visibility(self, visible: bool) -> Self:
        self.__blob.set_opacity(1.0 if visible else 0.0)
        return self

    def _autoblob_if_autoblobbing(self) -> Self:
        if self.autoblob:
            self._set_blob_visibility(len(self.terminals) > AUTOBLOBBING_BLOB_THRESHOLD)
        return self


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
