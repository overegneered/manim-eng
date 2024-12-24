Your first circuit diagram
==========================

Through the course of this tutorial, we'll try to replicate the current shunt animation
shown below (fans of CircuiTikZ may recognise this example!)

.. manim:: CurrentShunt
    :hide_source:

    from manim_eng import *

    class CurrentShunt(Scene):
        def construct(self):
            r1 = Resistor().rotate(90 * DEGREES)
            r2 = Resistor().rotate(90 * DEGREES).shift(2 * RIGHT)
            isource = CurrentSource().rotate(90 * DEGREES).shift(2 * LEFT)
            top_node = Node().shift(UP)
            bottom_node = Node().shift(DOWN)

            r2.set_label("R_2")
            r2.right.set_current("I_2")

            c = Circuit(isource, r1, top_node, bottom_node)

            self.play(
                Create(c),
            )
            self.play(
                c.animate.connect(isource.right, top_node.left),
                c.animate.connect(isource.left, bottom_node.left),
                c.animate.connect(r1.right, top_node.down),
                c.animate.connect(r1.left, bottom_node.up)
            )
            self.play(
                isource.animate.set_current("I_0"),
                r1.animate.set_label("R_1"),
            )
            voltage = r1.voltage("left", "right", "V", component_buff=0.35)
            self.play(
                r1.right.animate.set_current("I_1"),
                Create(voltage),
            )

            self.wait()
            self.play(
                c.animate.add(r2),
                c.animate.connect(r2.left, bottom_node.right),
                c.animate.connect(r2.right, top_node.right),
                voltage.animate.set_terminals(
                    start=r2.left,
                    end=r2.right,
                )
            )
            self.wait()

We'll start with just building the final circuit statically in the first four sections,
and then we'll animate it in the final section. Well, without further ado, let's get
started! If you want to jump to a particular point, use the contents below, but
otherwise, move on to :doc:`adding components <adding_components>`.

.. toctree::
    :caption: Contents

    adding_components
    adding_wires
    circuit_class
    voltage_and_current_labels
    animations
