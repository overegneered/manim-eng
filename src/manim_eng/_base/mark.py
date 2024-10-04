"""Contains the Mark class.

See Also
--------
anchor, markable
"""

from typing import Any, Callable, Self

import manim as mn

from manim_eng._base.anchor import Anchor
from manim_eng._config import config_eng
from manim_eng._utils import utils

__all__ = ["Mark"]


class Mark(mn.VMobject):
    """A mark object, representing any textual annotation on a component.

    Parameters
    ----------
    anchor : Anchor
        The anchor to use as a base for the attachment of the mark.
    centre_reference : Anchor
        The anchor to use as a reference; the mark will be kept aligned to ``anchor``,
        attached to the side directly opposite the side ``centre_reference`` is on.

    See Also
    --------
    anchor.Anchor
    """

    def __init__(self, anchor: Anchor, centre_reference: Anchor) -> None:
        super().__init__()
        self.mathtex: mn.MathTex = mn.MathTex("")

        self.updater: Callable[[mn.Mobject], None]
        self.change_anchors(anchor, centre_reference)

    def set_text(
        self,
        *args: Any,
        font_size: float = config_eng.symbol.mark_font_size,
        **kwargs: Any,
    ) -> Self:
        """Set the text of the mark.

        Parameters
        ----------
        *args : Any
            Positional arguments to be pass on to ``manim.MathTex``. The most important
            of these is ``*tex_strings``, i.e. the actual TeX math mode strings to use
            as the mark's text.
        font_size : float
            The font size to use for the mark. Leaving it empty adopts the default
            (recommended).
        **kwargs : Any
            Keyword arguments to pass on to ``manim.MathTex``.
        """
        if self.mathtex in self.submobjects:
            self.remove(self.mathtex)
        self.mathtex = mn.MathTex(*args, font_size=font_size, **kwargs)
        self.add(self.mathtex)
        self._reposition()
        return self

    def change_anchors(self, anchor: Anchor, centre_reference: Anchor) -> None:
        """Change the anchors to which the mark is attached.

        Parameters
        ----------
        anchor : Anchor
            The anchor to use as a base for the attachment of the mark.
        centre_reference : Anchor
            The anchor to use as a reference; the mark will be kept aligned to
            ``anchor``, attached to the side directly opposite the side
            ``centre_reference`` is on.
        """
        if len(self.updaters) != 0:
            self.remove_updater(self.updater)
        self.updater = self.__get_updater(anchor, centre_reference)
        self.add_updater(self.updater)
        self.update()

    @property
    def tex_strings(self) -> list[str] | None:
        if self.mathtex is None:
            return None
        return self.mathtex.tex_strings  # type: ignore[no-any-return]

    def _reposition(self) -> None:
        """Update the mark position so it is realigned with its anchor."""
        # If updating is suspended, the mark cannot be repositioned, as positioning is
        # done through an updater. Hence, allow updating and perform an update, but then
        # suspend updating again, all non-recursively to prevent any other
        # 'non-essential' updates
        if self.updating_suspended:
            self.resume_updating(recursive=False)
            self.update(recursive=False)
            self.suspend_updating(recursive=False)
        else:
            self.update()

    @staticmethod
    def __get_updater(
        anchor: Anchor, centre_reference: Anchor
    ) -> Callable[[mn.Mobject], None]:
        if (anchor.pos == centre_reference.pos).all():
            raise ValueError(
                "`anchor` and `centre_reference` cannot be the same. "
                f"Found: {anchor.pos=}, {centre_reference.pos=}.\n"
                "Please report this error to a developer."
            )

        def updater(mark: mn.Mobject) -> None:
            line_of_connection = anchor.pos - centre_reference.pos
            line_of_connection = mn.normalize(line_of_connection)
            line_of_connection = utils.cardinalised(
                line_of_connection, config_eng.symbol.mark_cardinal_alignment_margin
            )
            mark.next_to(
                mobject_or_point=anchor.pos,
                direction=line_of_connection,
                buff=mn.SMALL_BUFF,
            )

        return updater
