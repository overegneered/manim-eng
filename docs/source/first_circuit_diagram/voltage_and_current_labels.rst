Adding voltage and current labels
=================================

Voltage label
-------------

Voltage labels are administered through the :class:`~.Voltage` class, which has a very
similar interface to that of :class:`~.Wire`. However, as our voltage arrow is going
across a single component, we can use the :meth:`~.Component.voltage` method as a
shorthand.

Let's add one in.

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
            self.add(r2.voltage("left", "right", "V"))

.. note::

    There are two ways of telling a component-specific voltage arrow which terminals to
    attach to. You can either pass in the terminals just as you would for a standard
    voltage or wire (so in this case, ``r2.left`` and ``r2.right``), or you can pass
    strings of the terminal names, which is quicker, and so I opted for it here.

This gives us a beautiful voltage arrow as below.

.. manim:: CurrentShunt
    :save_last_frame:
    :hide_source:

    from manim_eng import *
    config_eng.debug = False

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
            self.add(r2.voltage("left", "right", "V"))

The voltage arrow is clever --- because we constructed it using |R2|'s method, it knows
to avoid |R2| and its labels and annotations. See the :class:`~.Voltage` documentation
for more details.

Current labels
--------------

There are two ways to add current labels to terminals in manim-eng: one is to use the
:meth:`~.Terminal.set_current()` method on :class:`~.Terminal`, and the other is to use
the :meth:`~.Component.set_current()` method on :class:`~.Component`. Both have their
advantages and drawbacks, but the main points are:

- Using the first method allows static code analysers (such as those built-in to all
  modern IDEs) to verify that the terminal you're trying to use actually exists on the
  component.
- The second method, whilst indirect, returns the component it was called on, allowing
  for method chaining.

As we used the second method back when we were
:doc:`adding components <adding_components>` to our scene, we'll use the first method
now.

.. code-block:: python

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
            self.add(r2.voltage("left", "right", "V"))

This gives us the result below.

.. manim:: CurrentShunt
    :save_last_frame:
    :hide_source:

    from manim_eng import *
    config_eng.debug = False

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
            self.add(r2.voltage("left", "right", "V"))

Tweaking the voltage label
--------------------------

The above looks pretty good, but it's a little annoying how the voltage arrow collides
with the |I2| current arrow. We can avoid this by changing the buffer. There are two
types of buffer on a voltage arrow:

- The ``buff``, which is the buffer between the end of the voltage arrow and the
  terminals it is attached to; and
- The ``component_buff``, which is the buffer applied between the arrow and the
  component it is attached to (if any). The ``component_buff`` impacts the curvature of
  the arrow.

We'll adjust the ``component_buff`` for our purposes.

.. code-block:: python

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

.. manim:: CurrentShunt
    :save_last_frame:
    :hide_source:

    from manim_eng import *
    config_eng.debug = False

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

And with that, we've got our full circuit! With that, you should be at least aware of
the important aspects of manim-eng that make it tick (at least, aware enough to know
where to start digging).

However, there's one last thing we need to touch on --- animations!

.. |R2| replace:: *R*\ :sub:`2`
.. |I2| replace:: *I*\ :sub:`2`
