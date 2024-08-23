import manim as mn
import numpy as np
import numpy.typing as npt

LABEL_COLOUR = mn.RED
ANNOTATION_COLOUR = mn.BLUE
CURRENT_COLOUR = mn.ORANGE
TERMINAL_COLOUR = mn.GREEN
CENTRE_COLOUR = mn.PURPLE


class Anchor(mn.Arc):
    def __init__(self, debug: bool, colour: mn.ManimColor):
        super().__init__(
            0.06 if debug else 0,
            start_angle=0,
            angle=2 * mn.PI,
            color=colour,
            stroke_width=2,
            z_index=100,
        )

    @property
    def pos(self) -> npt.NDArray:
        return np.array(self.get_center())
