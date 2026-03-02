from manim import *
from manim_eng import *

class CurrentShunt(Scene):
    def construct(self):
        r1 = Resistor().rotate(90 * DEGREES)
        r2 = Resistor().rotate(90 * DEGREES).shift(2 * RIGHT)
        isource = CurrentSource().rotate(90 * DEGREES).shift(2 * LEFT)
        top_node = Node().shift(UP)
        bottom_node = Node().shift(DOWN)

        r1.set_label("R_1")
        r1.right.set_current("I_1")
        r2.set_label("R_2")
        r2.right.set_current("I_2")
        isource.set_current("I_0")

        c = (Circuit(r1, r2, isource, top_node, bottom_node)
             .connect(isource.right, top_node.left)
             .connect(r1.right, top_node.down)
             .connect(r2.right, top_node.right)
             .connect(isource.left, bottom_node.left)
             .connect(isource.left, bottom_node.left)
             .connect(r1.left, bottom_node.up)
             .connect(r2.left, bottom_node.right))

        self.add(c)
        self.add(r2.voltage("left", "right", "V", component_buff=0.35))