"""Contains the anchor class for attachments of marks.

See Also
--------
mark
"""

import abc

import manim as mn
import manim.typing as mnt

from manim_eng._config import config_eng

__all__ = ["Anchor"]


class Anchor(mn.Arc, metaclass=abc.ABCMeta):
    """Anchor to which Marks can be attached.

    See Also
    --------
    mark.Mark
    """

    def __init__(self, colour: mn.ManimColor) -> None:
        super().__init__(
            config_eng.anchor.radius if config_eng.debug else 0,
            start_angle=0,
            angle=2 * mn.PI,
            color=colour,
            stroke_width=config_eng.anchor.stroke_width,
            z_index=100,
        )

    @property
    def pos(self) -> mnt.Point3D:
        return self.get_center()


class AnnotationAnchor(Anchor):
    def __init__(self) -> None:
        super().__init__(config_eng.anchor.annotation_colour)


class CentreAnchor(Anchor):
    def __init__(self) -> None:
        super().__init__(config_eng.anchor.centre_colour)


class CurrentAnchor(Anchor):
    def __init__(self) -> None:
        super().__init__(config_eng.anchor.current_colour)


class LabelAnchor(Anchor):
    def __init__(self) -> None:
        super().__init__(config_eng.anchor.label_colour)


class TerminalAnchor(Anchor):
    def __init__(self) -> None:
        super().__init__(config_eng.anchor.terminal_colour)


class VoltageAnchor(Anchor):
    def __init__(self) -> None:
        super().__init__(config_eng.anchor.voltage_colour)
