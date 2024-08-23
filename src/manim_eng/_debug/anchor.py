import manim as mn
import numpy as np
import numpy.typing as npt

from manim_eng._config import config_eng


class Anchor(mn.Arc):
    def __init__(self, colour: mn.ManimColor):
        super().__init__(
            0.06 if config_eng.debug else 0,
            start_angle=0,
            angle=2 * mn.PI,
            color=colour,
            stroke_width=2,
            z_index=100,
        )

    @property
    def pos(self) -> npt.NDArray:
        return np.array(self.get_center())
