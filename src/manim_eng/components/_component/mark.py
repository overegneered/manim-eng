from typing import Any, Self

import manim as mn
import numpy as np

import manim_eng._utils as utils

from ..._debug.anchor import Anchor
from .._component import MARK_FONT_SIZE

# How many radians off a cardinal direction of alignment a components can be whilst the
# mark alignments still treat it as in a cardinal alignment
CARDINAL_ALIGNMENT_MARGIN = 5 * (np.pi / 180)


class AlreadyAttachedError(RuntimeError):
    pass


class Mark(mn.MathTex):
    """A mark object, representing any textual annotation on a component.

    Parameters
    ----------
    *args : Any
        Positional arguments to be pass on to ``manim.MathTex``. The most important
        of these is ``*tex_strings``, i.e. the actual TeX math mode strings to use as
        the mark's text.
    font_size : float
        The font size to use for the mark. Leaving it empty adopts the default
        (recommended).
    **kwargs : Any
        Keyword arguments to pass on to ``manim.MathTex``.
    """

    def __init__(
        self, *args: Any, font_size: float = MARK_FONT_SIZE, **kwargs: Any
    ) -> None:
        super().__init__(*args, font_size=font_size, **kwargs)

        self._attached: bool = False

    def attach(self, anchor: Anchor, centre_reference: Anchor) -> Self:
        if (anchor.pos == centre_reference.pos).all():
            raise ValueError(
                "`anchor` and `centre_reference` cannot be the same. "
                f"Found: {anchor=}, {centre_reference=}.\n"
                "Please report this error to a developer."
            )

        if self._attached:
            raise AlreadyAttachedError(
                "This Mark is already attached to an anchor, and cannot be attached to "
                "another.\n"
                "Please report this error to a developer."
            )

        def updater(mark: mn.Mobject) -> None:
            line_of_connection = anchor.pos - centre_reference.pos
            line_of_connection = utils.normalised(line_of_connection)
            line_of_connection = utils.cardinalised(
                line_of_connection, CARDINAL_ALIGNMENT_MARGIN
            )
            mark.next_to(
                mobject_or_point=anchor.pos,
                direction=line_of_connection,
                buff=mn.SMALL_BUFF,
            )

        self.add_updater(updater)
        self.update()
        self._attached = True
        return self
