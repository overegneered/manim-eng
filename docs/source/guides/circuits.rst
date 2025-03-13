Circuits
========

The :class:`~.Circuit` class is designed to make building circuits easier, in particular
by handling as much wiring as possible (including the pesky attaching and detaching).

.. note::

    If you haven't read the guide on :doc:`wiring <wiring>`, I recommend you read
    that first --- the :class:`~.Wire` is what :class:`~.Circuit` uses under the bonnet
    to do component connection, and won't repeat the coverage of how those connections
    are plotted.

.. _add_components_to_circuits:

Adding and removing components
------------------------------

Adding and removing components is very simple, and mirrors the API for Manim
:external+manim:class:`manim.scene.scene.Scene`\ s: :meth:`~.Circuit.add` is used to add
one or more components, and :meth:`~.Circuit.remove` removes one or more components.

Adding wires
------------

Wires are added using the :meth:`~.Circuit.connect` method. This mirrors the signature
of the :class:`~.Wire` constructor; the first parameter is the terminal to go from, the
second is the terminal to go to. One caveat here is that all terminals passed to
:meth:`~.Circuit.connect` must belong to components in the circuit, i.e. they must have
been :ref:`added <add_components_to_circuits>` first.

.. tip::

    If you want to connect a component in a given circuit to one not in that circuit,
    you can use either a :class:`~.Wire` or a :class:`~.ManualWire`, which work
    regardless of what any given components' parents are --- see
    :doc:`here <wiring>` for more info.

.. code-block:: python

    class CircuitExample(Scene):
        def construct(self):
            r1 = Resistor(label="R_1").shift(UP)
            r2 = Resistor(label="R_2")
            r3 = Resistor(label="R_3").shift(DOWN)
            c = Circuit(r1, r2, r3)

            c.connect(r1.right, r2.right)
            c.connect(r2.right, r3.right)
            c.connect(r1.left, r2.left)
            c.connect(r2.left, r3.left)

            self.add(c)

.. manim:: CircuitExample
    :hide_source:
    :save_last_frame:

    from manim_eng import *

    class CircuitExample(Scene):
        def construct(self):
            r1 = Resistor(label="R_1").shift(UP)
            r2 = Resistor(label="R_2")
            r3 = Resistor(label="R_3").shift(DOWN)
            c = Circuit(r1, r2, r3)

            c.connect(r1.right, r2.right)
            c.connect(r2.right, r3.right)
            c.connect(r1.left, r2.left)
            c.connect(r2.left, r3.left)

            self.add(c)

.. note::

    You'd normally add some :class:`~.Node`\ s to have solder blobs either side of |R2|,
    but I've omitted these here to keep the example short.

Removing wires
--------------

There are two ways of removing wires from a circuit: :meth:`~.Circuit.disconnect` and
:meth:`~.Circuit.isolate`. These vary slightly in how they decide if a wire is to be
removed, but otherwise work identically. They take an arbitrarily long list of end
specifiers, which can be either :class:`~.Component`\ s or :class:`~.Terminal`\ s
(passing a component is shorthand for passing all of its terminals).

Disconnection
^^^^^^^^^^^^^

The :meth:`~.Circuit.disconnect` method will only remove a wire if *both* the start and
end of the wire are passed as arguments. In the example below, we disconnect |R1| and
|R2|, with the result we expect.

.. code-block:: python

    class CircuitExample(Scene):
        def construct(self):
            r1 = Resistor(label="R_1").shift(UP)
            r2 = Resistor(label="R_2")
            r3 = Resistor(label="R_3").shift(DOWN)
            c = Circuit(r1, r2, r3)

            c.connect(r1.right, r2.right)
            c.connect(r2.right, r3.right)
            c.connect(r1.left, r2.left)
            c.connect(r2.left, r3.left)

            c.disconnect(r1, r2)

            self.add(c)

.. manim:: CircuitExample
    :hide_source:
    :save_last_frame:

    from manim_eng import *

    class CircuitExample(Scene):
        def construct(self):
            r1 = Resistor(label="R_1").shift(UP)
            r2 = Resistor(label="R_2")
            r3 = Resistor(label="R_3").shift(DOWN)
            c = Circuit(r1, r2, r3)

            c.connect(r1.right, r2.right)
            c.connect(r2.right, r3.right)
            c.connect(r1.left, r2.left)
            c.connect(r2.left, r3.left)

            c.disconnect(r1, r2)

            self.add(c)

To drive the point about needing to pass both ends home, if we just one end specifier
(say ``r1.left``), nothing will happen.

.. code-block:: python

    class CircuitExample(Scene):
        def construct(self):
            r1 = Resistor(label="R_1").shift(UP)
            r2 = Resistor(label="R_2")
            r3 = Resistor(label="R_3").shift(DOWN)
            c = Circuit(r1, r2, r3)

            c.connect(r1.right, r2.right)
            c.connect(r2.right, r3.right)
            c.connect(r1.left, r2.left)
            c.connect(r2.left, r3.left)

            c.disconnect(r1.left)

            self.add(c)

.. manim:: CircuitExample
    :hide_source:
    :save_last_frame:

    from manim_eng import *

    class CircuitExample(Scene):
        def construct(self):
            r1 = Resistor(label="R_1").shift(UP)
            r2 = Resistor(label="R_2")
            r3 = Resistor(label="R_3").shift(DOWN)
            c = Circuit(r1, r2, r3)

            c.connect(r1.right, r2.right)
            c.connect(r2.right, r3.right)
            c.connect(r1.left, r2.left)
            c.connect(r2.left, r3.left)

            c.disconnect(r1.left)

            self.add(c)

Isolate
^^^^^^^

You may have been able to guess from our treatment of :meth:`~.Circuit.disconnect` how
:meth:`~.Circuit.isolate` differs. Isolation will remove all wires connected to the
passed end points. If we use the example above, but *isolate* ``r1.left`` rather than
*disconnecting* it, we see that the wire between |R1| and |R2|'s left terminals is
removed.

.. code-block:: python

    class CircuitExample(Scene):
        def construct(self):
            r1 = Resistor(label="R_1").shift(UP)
            r2 = Resistor(label="R_2")
            r3 = Resistor(label="R_3").shift(DOWN)
            c = Circuit(r1, r2, r3)

            c.connect(r1.right, r2.right)
            c.connect(r2.right, r3.right)
            c.connect(r1.left, r2.left)
            c.connect(r2.left, r3.left)

            c.isolate(r1.left)

            self.add(c)

.. manim:: CircuitExample
    :hide_source:
    :save_last_frame:

    from manim_eng import *

    class CircuitExample(Scene):
        def construct(self):
            r1 = Resistor(label="R_1").shift(UP)
            r2 = Resistor(label="R_2")
            r3 = Resistor(label="R_3").shift(DOWN)
            c = Circuit(r1, r2, r3)

            c.connect(r1.right, r2.right)
            c.connect(r2.right, r3.right)
            c.connect(r1.left, r2.left)
            c.connect(r2.left, r3.left)

            c.isolate(r1.left)

            self.add(c)

We could also have passed just ``r1`` to remove all wires going to |R1|, or even ``r2``
to remove all wires full stop (as all wires are connected at one end to one of |R2|'s
terminals.


Animations
----------

Like everything else in manim-eng, :class:`~.Circuit` provides hand-crafted animation
overrides for its methods. An example showcasing this and combining the various
capabilities outlined on this page is below.

.. code-block:: python

    class CircuitExample(Scene):
        def construct(self):
            r1 = Resistor(label="R_1").shift(UP)
            r2 = Resistor(label="R_2")
            r3 = Resistor(label="R_3").shift(DOWN)
            c = Circuit(r1, r2, r3)
            self.add(c)

            self.play(
                c.animate.connect(r1.right, r2.right),
                c.animate.connect(r1.left, r2.left),
            )
            self.play(
                c.animate.connect(r2.right, r3.right),
                c.animate.connect(r2.left, r3.left),
            )
            self.wait()
            self.play(
                c.animate.disconnect(r1, r2.left)
            )
            self.wait()
            self.play(
                c.animate.isolate(r3)
            )
            self.wait()

.. manim:: CircuitExample
    :hide_source:

    from manim_eng import *

    class CircuitExample(Scene):
        def construct(self):
            r1 = Resistor(label="R_1").shift(UP)
            r2 = Resistor(label="R_2")
            r3 = Resistor(label="R_3").shift(DOWN)
            c = Circuit(r1, r2, r3)
            self.add(c)

            self.play(
                c.animate.connect(r1.right, r2.right),
                c.animate.connect(r1.left, r2.left),
            )
            self.play(
                c.animate.connect(r2.right, r3.right),
                c.animate.connect(r2.left, r3.left),
            )
            self.wait()
            self.play(
                c.animate.disconnect(r1, r2.left)
            )
            self.wait()
            self.play(
                c.animate.isolate(r3)
            )
            self.wait()


.. |R1| replace:: *R*\ :sub:`1`
.. |R2| replace:: *R*\ :sub:`2`
