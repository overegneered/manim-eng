import manim as mn
import manim.typing as mnt
import numpy as np

from .._config import config_eng


class Anchor(mn.Arc):
    def __init__(self, colour: mn.ManimColor):
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
