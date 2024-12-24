Adding animations
=================

You may have noticed that animations have been conspicuously absent from this tutorial
so far --- the 'anim' in 'Manim' (and therefore 'manim-eng') stands for 'animation'
after all. The main reason behind this is that manim-eng has been designed so that, as
much as possible, it shouldn't matter whether you're animating or not.

manim-eng makes heavy use of the ability to override animations using
:external+manim:func:`override_animate() <manim.mobject.mobject.override_animate>`. This
ensures that the animations returned by calls using ``.animate`` are clean and sensible
--- so that you can focus on the parts of your animation that matter. For more info on
the ``.animate`` syntax, check out the
`Manim docs on the subject <https://docs.manim.community/en/stable/tutorials/quickstart.html#using-animate-syntax-to-animate-methods>`_.

Let's take a look at what this means in practice. Let's say we want to animate the
introduction of the current labels we were working on on the last page. We throw in
``.animate`` and we're done!

.. code-block:: python

    class CurrentShunt(Scene):
        def construct(self):
            r1 = Resistor().rotate(90 * DEGREES)
            r2 = Resistor().rotate(90 * DEGREES).shift(2 * RIGHT)
            isource = CurrentSource().rotate(90 * DEGREES).shift(2 * LEFT)
            top_node = Node().shift(UP)
            bottom_node = Node().shift(DOWN)

            r1.set_label("R_1")
            r2.set_label("R_2")
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

            self.wait()
            self.play(
                r1.right.animate.set_current("I_1"),
                r2.right.animate.set_current("I_2"),
            )
            self.wait()

We've removed the ``set_current()`` calls from earlier in the code and moved them to a
call to ``self.play()``, with some waits to make it easier to see. The result is then
shown below.

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

            r1.set_label("R_1")
            r2.set_label("R_2")
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

            self.wait()
            self.play(
                r1.right.animate.set_current("I_1"),
                r2.right.animate.set_current("I_2"),
            )
            self.wait()

We can do the same for everything else as well! Let's take a look.

.. code-block:: python

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

With that, you've seen all of the important parts of manim-eng, and whilst you may not
know everything, you should hopefully know where to start looking for anything you
might wish to know. Happy drawing!
