import manim as mn
import numpy as np

from manim_eng.component._component import Terminal

WIRE_STROKE_WIDTH: float = 2.5
COMPONENT_STROKE_WIDTH: float = 4.0


class Wire(mn.Line):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, stroke_width=WIRE_STROKE_WIDTH, **kwargs)


class Connection(Wire):
    def __init__(self, end_1: Terminal, end_2: Terminal, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO: All of this logic. Will probably end up being pretty complicated
        #       It currently doesn't work because the Component types don't take their
        #       translations into account when reporting their positions - hopefully
        #       this will work once this is resolved. This also needs line culling to
        #       prevent unnecessary lines being drawn
        half_difference = (end_2.position - end_1.position) / 2
        horizontal_half_vector = np.array([half_difference[0], 0, 0])
        vertical_half_vector = np.array([0, half_difference[1], 0])

        # TODO: pick whether to start with a horizontal or vertical line based on which
        #       is better aligned to the terminals at each end (use the dot product)
        first_half_vector = horizontal_half_vector
        ends_more_aligned_to_the_vertical_than_the_horizontal = (
            end_1.position + end_2.position
        ).dot(np.array([1, 0, 0])) < (end_1.position + end_2.position).dot(
            np.array([0, 1, 0])
        )
        if ends_more_aligned_to_the_vertical_than_the_horizontal:
            first_half_vector = vertical_half_vector

        points = [
            end_1.position,
            end_1.position + first_half_vector,
            end_2.position - first_half_vector,
            end_2.position,
        ]
        for i in range(len(points) - 1):
            if (points[i] != points[i + 1]).any():
                self.add(Wire(points[i], points[i + 1]))
