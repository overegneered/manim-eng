from manim import *
from manim_eng import *

class BJTAmplifier(Scene):
    def construct(self):
        r1 = Resistor().rotate(90 * DEGREES).shift(UP * 1.5 + LEFT)
        r2 = Resistor().rotate(90 * DEGREES).shift(DOWN * 1.5 + LEFT)
        c = Capacitor().shift(LEFT * 2)
        nodeinput = Node().shift(LEFT * 3)
        node1 = Node().shift(LEFT)
        # TODO: the rotation of tripolar components are still problematic. Try change their critical points.
        bjt = NPNTransistor().flip().rotate_about_origin(90 * DEGREES).shift(RIGHT)
        rload = Resistor().rotate(90 * DEGREES).shift(UP * 2 + RIGHT)
        re = Resistor().rotate(90 * DEGREES).shift(DOWN * 2 + RIGHT)
        node2 = Node().shift(RIGHT + UP * 3)
        node3 = Node().shift(RIGHT + DOWN * 3)
        vdd = VDD().shift(RIGHT + UP * 3.5)
        gnd = Earth().shift(RIGHT + DOWN * 3.5)

        r1.set_label("R_1")
        r2.set_label("R_2")
        re.set_label("R_e")
        c.set_label("C")
        nodeinput.set_label(r"V_{\text{in}}")
        rload.set_label(r"R_{\text{load}}")

        circuit = (Circuit(r1, r2, c, nodeinput, node1, bjt, rload, re, node2, node3, vdd, gnd)
                .connect(r1.left, node1.up)
                .connect(r1.right, node2.left)
                .connect(c.left, nodeinput.right)
                .connect(c.right, node1.left)
                .connect(node1.right, bjt.base)
                .connect(node1.down, r2.right)
                .connect(r2.left, node3.left)
                .connect(node2.down, rload.right)
                .connect(rload.left, bjt.collector)
                .connect(bjt.emitter, re.right)
                .connect(re.left, node3.up)
                .connect(vdd.terminal, node2.up)
                .connect(node3.down, gnd.terminal))

        self.add(circuit)