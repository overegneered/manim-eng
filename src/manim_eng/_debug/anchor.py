import abc

import manim as mn
import manim.typing as mnt
import numpy as np

from manim_eng._config import config_eng


class Anchor(mn.Arc, metaclass=abc.ABCMeta):
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
        return np.array(self.get_center())


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
