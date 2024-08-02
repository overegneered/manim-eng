import manim as mn


LABEL_COLOUR = mn.RED
ANNOTATION_COLOUR = mn.BLUE
TERMINAL_COLOUR = mn.GREEN


class Anchor(mn.Arc):
    def __init__(self, debug: bool, color: mn.ManimColor):
        super().__init__(
            0.06 if debug else 0,
            start_angle=0,
            angle=2 * mn.PI,
            color=color,
            stroke_width=3,
        )
