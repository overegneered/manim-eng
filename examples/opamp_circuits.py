from manim import DEGREES, DOWN, LEFT, RIGHT, UP, Scene

from manim_eng import (
    VDD,
    VSS,
    Capacitor,
    Circuit,
    Ground,
    Node,
    OpAmp,
    Resistor,
    SchottkyDiode,
)


class SineWaveGenerator(Scene):
    """A sine wave generator built with OP284 amplifier."""

    def construct(self) -> None:
        opamp = OpAmp().shift(RIGHT * 0.5)
        v1 = VDD().shift(UP + RIGHT * 0.5)
        v2 = VSS().shift(DOWN + RIGHT * 0.5)
        node1 = Node().shift(RIGHT * 3.2)
        r1 = Resistor().shift(UP * 2 + RIGHT * 2)
        c1 = Capacitor().shift(UP * 2)
        r2 = Resistor().shift(UP * 2.4 + LEFT * 2)
        c2 = Capacitor().shift(UP * 1.6 + LEFT * 2)
        gnd1 = Ground().rotate(-90 * DEGREES).shift(UP * 2.4 + LEFT * 4)
        node2 = Node().shift(UP * 2 + LEFT)
        node3 = Node().shift(UP * 1.6 + LEFT * 3.2)
        node4 = Node().shift(UP * 2.4 + LEFT * 3.2)
        d1 = SchottkyDiode().shift(DOWN * 1.4 + RIGHT * 2)
        node5 = Node().shift(DOWN * 1.4 + RIGHT * 3.2)
        d2 = SchottkyDiode().rotate(180 * DEGREES).shift(DOWN * 2.6 + RIGHT * 2)
        node6 = Node().shift(DOWN * 2 + RIGHT)
        ra = Resistor().shift(DOWN * 2)
        node7 = Node().shift(DOWN * 2 + LEFT)
        rb = Resistor().shift(DOWN * 2 + LEFT * 2)
        gnd2 = Ground().rotate(-90 * DEGREES).shift(DOWN * 2 + LEFT * 4)
        node_out = Node().shift(RIGHT * 4)

        opamp.set_label(r"\alpha")
        opamp.set_annotation(r"\text{OP284}")
        v1.set_label("+V")
        v2.set_label("-V")
        node_out.set_label(r"V_{\text{out}}")
        r1.set_label("R")
        c1.set_label(
            "C"
        )  # TODO: is there a convenient method to move the anchor to the other side?
        r2.set_label("R")
        c2.set_label("C")
        ra.set_label("R_a")
        rb.set_label("R_b")

        circuit = (
            Circuit(
                opamp,
                v1,
                v2,
                r1,
                c1,
                r2,
                c2,
                gnd1,
                node1,
                node2,
                node3,
                node4,
                d1,
                node5,
                d2,
                node6,
                ra,
                node7,
                rb,
                gnd2,
                node_out,
            )
            .connect(opamp.vdd, v1.terminal)
            .connect(opamp.vss, v2.terminal)
            .connect(opamp.vout, node1.left)
            .connect(node1.up, r1.right)
            .connect(r1.left, c1.right)
            .connect(c1.left, node2.right)
            .connect(node2.up, r2.right)
            .connect(node2.down, c2.right)
            .connect(c2.left, node3.right)
            .connect(r2.left, node4.right)
            .connect(node3.up, node4.down)
            .connect(node3.down, opamp.vp)
            .connect(node4.left, gnd1.terminal)
            .connect(node1.down, node5.up)
            .connect(node5.left, d1.right)
            .connect(node5.down, d2.left)
            .connect(d1.left, node6.up)
            .connect(d2.right, node6.down)
            .connect(node6.left, ra.right)
            .connect(ra.left, node7.right)
            .connect(node7.up, opamp.vn)
            .connect(node7.left, rb.right)
            .connect(rb.left, gnd2.terminal)
            .connect(node1.right, node_out.left)
        )

        self.add(circuit)
