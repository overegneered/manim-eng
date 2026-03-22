"""Contains the EngScene class."""

from typing import Self, Sequence

import manim as mn

from manim_eng.circuits.base import WireBase

__all__ = ["EngScene"]


class EngScene(mn.Scene):
    """Canvas for manim-eng animations.

    This slightly augments the underlying ``Scene`` object to insert some automatic wire
    visibility handling logic. It isn't essential to use this, but you may need to do
    additional manual intervention if you do not to make sure wire visibility is
    correctly handled. All underlying functionality is preserved; it is a transparent
    abstraction.
    """

    def add(self, *mobjects: mn.Mobject) -> Self:
        """Add a mobject to the scene.

        If any of the ``Mobject``s are :class:`~.WireBase` instances, their visibility
        status will be updated automatically.
        """
        super().add(*mobjects)
        self.__set_visibility(True, *mobjects)
        return self

    def bring_to_back(self, *mobjects: mn.Mobject) -> None:
        """Remove mobjects from the scene and add them back to the back."""
        super().bring_to_back(*mobjects)
        # bring_to_back calls remove() which will set things to hidden: we need to set
        # them visible again
        self.__set_visibility(True, *mobjects)

    def clear(self) -> Self:
        """Clear all mobjects from the scene.

        If any of the ``Mobject``s are :class:`~.WireBase` instances, their visibility
        status will be updated automatically.
        """
        self.__set_visibility(False, *[*self.mobjects, *self.foreground_mobjects])
        super().clear()
        return self

    def remove(self, *mobjects: mn.Mobject) -> Self:
        """Remove a mobject from the scene.

        If any of the ``Mobject``s are :class:`~.WireBase` instances, their visibility
        status will be updated automatically.
        """
        super().remove(*mobjects)
        self.__set_visibility(False, *mobjects)
        return self

    def replace(self, old_mobject: mn.Mobject, new_mobject: mn.Mobject) -> None:
        """Replace one mobject in the scene with another, preserving draw order.

        If either of the ``Mobject``s are :class:`~.WireBase` instances, their
        visibility status will be updated automatically.
        """
        super().replace(old_mobject, new_mobject)
        self.__set_visibility(False, old_mobject)
        self.__set_visibility(True, new_mobject)

    def restructure_mobjects(
        self,
        to_remove: Sequence[mn.Mobject],
        mobject_list_name: str = "mobjects",
        extract_families: bool = True,
    ) -> Self:
        """Remove mobjects from the internal mobject lists.

        If any of the ``Mobject``s are :class:`~.WireBase` instances, their visibility
        status will be updated automatically.
        """
        super().restructure_mobjects(to_remove, mobject_list_name, extract_families)
        if mobject_list_name == "mobjects":
            # Wire removed from the main list is off screen — mark it hidden.
            self.__set_visibility(False, *to_remove)
        else:
            # Restructuring the foreground list alone: only mark hidden those wires
            # that are no longer in self.mobjects (i.e. truly off screen). Wires
            # still present in self.mobjects remain visible.
            mobjects_family: set[mn.Mobject] = set()
            for m in self.mobjects:
                mobjects_family.update(m.get_family())
            off_screen = [m for m in to_remove if m not in mobjects_family]
            if off_screen:
                self.__set_visibility(False, *off_screen)
        return self

    def __set_visibility(self, visible: bool, *mobjects: mn.Mobject) -> None:
        """Set all WireBase instances in mobjects to visible or hidden."""
        update_needed = False
        for mobject in mobjects:
            for descendant in mobject.get_family():
                if isinstance(descendant, WireBase):
                    if visible:
                        descendant._set_visible()
                    else:
                        descendant._set_hidden()
                    update_needed = True
        if update_needed:
            self.update_mobjects(0)
