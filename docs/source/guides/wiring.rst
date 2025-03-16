Wiring and nodes
================

Basic wiring
------------

The central element of wiring in manim-eng is the :class:`~.Wire` class. It takes a
start terminal and an end terminal, and automatically plans a path between the two. It
actually does this continuously via an updater, so if the terminals to which the wire is
attached are moved, the wire will plan a new path seamlessly.

.. code-block:: python

    class WireBasics(Scene):
        def construct(self):
            r1 = Resistor().shift(LEFT)
            r2 = Resistor().shift(RIGHT)
            self.add(r1, r2)
            self.add(Wire(r1.right, r2.left))
            self.wait()
            self.play(
                r1.animate.shift(UP),
                r2.animate.shift(DOWN),
            )
           self.play(
                r1.animate.shift(LEFT),
                r2.animate.shift(RIGHT),
            )
            self.play(Rotate(r2, angle=-PI))
            self.wait()

.. manim:: WireBasics
    :hide_source:

    from manim_eng import *

    class WireBasics(Scene):
        def construct(self):
            r1 = Resistor().shift(LEFT)
            r2 = Resistor().shift(RIGHT)
            self.add(r1, r2)
            self.add(Wire(r1.right, r2.left))
            self.wait()
            self.play(
                r1.animate.shift(UP),
                r2.animate.shift(DOWN),
            )
            self.play(
                r1.animate.shift(LEFT),
                r2.animate.shift(RIGHT),
            )
            self.play(Rotate(r2, angle=-PI))
            self.wait()

Planning wire paths
^^^^^^^^^^^^^^^^^^^

In order to determine what path a wire should follow, manim-eng follows the following
principles:

1. Wires only run horizontally or vertically;
2. Terminals are treated as having the nearest cardinal direction (e.g. a terminal at
   60° anticlockwise from the horizontal would be treated as pointing up);
3. Wires should never go 'backwards' out of a terminal;
4. Wire should, where possible, come out of the front of a terminal; and
5. Where three line segments are required, the middle segment should be placed in the
   middle (meaning the other two segments have the same length).

In general, the only situation in which this will produce results that look visibly
strange is if two collinear terminals pointing in the same direction are connected, as
demonstrated in the example below.

.. code-block:: python

    class StrangeAutomaticWiring(Scene):
        def construct(self):
            r1 = Resistor().shift(LEFT)
            r2 = Resistor().shift(RIGHT)
            self.add(r1, r2)
            self.add(Wire(r1.right, r2.right))

.. manim:: StrangeAutomaticWiring
    :save_last_frame:
    :hide_source:

    from manim_eng import *

    class StrangeAutomaticWiring(Scene):
        def construct(self):
            r1 = Resistor().shift(LEFT)
            r2 = Resistor().shift(RIGHT)
            self.add(r1, r2)
            self.add(Wire(r1.right, r2.right))

Note that these are both resistors (i.e. the right-hand one is *not* a fuse!)

Advanced wiring: using nodes
----------------------------

A notable deficiency of the :class:`~.Wire` class is that it can only connect two
terminals. To produce more complex layouts that include intersections, we have to turn
to the :class:`~.Node` class.

Nodes behave a little differently to normal components, namely in the way they handle
terminals. Nodes can have terminals in any direction, and create them as and when
they're needed. Node terminals are only visible when wires are attached to them, and are
otherwise invisible. [#terminal_invisibility]_

Attaching and detaching wires
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In order for a terminal to change its visibility based on whether or not a wire is
attached to it, it needs to know whether or not a wire is attached. This brings us to
the :meth:`~.WireBase.attach()` and :meth:`~.WireBase.detach()` methods.

These methods instruct a wire to tell the terminals it has in its ``start`` and ``end``
attributes that it is now attached, by calling the
:meth:`~.Terminal._increment_connection_count()` or
:meth:`~.Terminal._decrement_connection_count()` methods on them.

But why not attach automatically?
"""""""""""""""""""""""""""""""""

It comes down to animations. Consider the following example:

.. code-block:: python

    n1 = Node().shift(LEFT)
    n2 = Node().shift(RIGHT)
    w = Wire(start=n1.right, end=n2.left)

    self.add(n1, n2)
    self.wait()
    self.add(w.attach())
    self.wait()

If :class:`~.Wire` called :meth:`~.WireBase.attach` automatically in its constructor,
then the terminals of ``node 1`` and ``node 2`` would be updated to display *before*
``w`` were displayed. We would then see the following.

.. manim:: WhyNotAttachAutomatically
    :hide_source:

    from manim_eng import *

    class WhyNotAttachAutomatically(Scene):
        def construct(self):
            n1 = Node().shift(LEFT)
            n2 = Node().shift(RIGHT)
            w = Wire(start=n1.right, end=n2.left).attach()

            self.add(n1, n2)
            self.wait()
            self.add(w.attach())
            self.wait()

.. important::

    This is *not* what you would see if you ran the code above! This is what you would
    see *if the* wire *constructor ran* ``attach()`` *automatically*.

We end up with a weird artefact of the node terminals being presented before the wire
is. As an aside, if we actually run the code above, we see the below...

.. manim:: WhyNotAttachAutomatically
    :hide_source:

    from manim_eng import *

    class WhyNotAttachAutomatically(Scene):
        def construct(self):
            n1 = Node().shift(LEFT)
            n2 = Node().shift(RIGHT)
            w = Wire(start=n1.right, end=n2.left)

            self.add(n1, n2)
            self.wait()
            self.add(w.attach())
            self.wait()

... which looks much better. Of course, this is a contrived example, but hopefully you
see the reasoning.

Some things handle attaching for you
""""""""""""""""""""""""""""""""""""

There are some ways of getting around having to worry about this. The
:class:`~.WireBase` class (the base class of all other wires) overrides the
:external+manim:class:`~.Create` and :external+manim:class:`~.Uncreate` animations to
call :meth:`~.WireBase.attach` or :meth:`~.WireBase.detach`, respectively. The
:class:`~.Circuit` class also handles this itself.

If you're using a mix of these automatic solutions and manual handling, or you're not
quite sure, it's always worth erring on the side of attaching and detaching manually.
The :meth:`~.WireBase.attach`/:meth:`~.WireBase.detach` method checks whether a wire
is already attached/detached before attaching/detaching, so attaching/detaching twice
has no detrimental effects.

.. _autoblobbing:

Autoblobbing
^^^^^^^^^^^^

Circuit drawing best practice says that intersections of wires should be drawn with
solder blobs. By default, :class:`~.Node`\ s handle this automatically, in what
manim-eng calls **autoblobbing**. Let's take a look at an example.

.. code-block:: python

    class AutoblobbingExample(Scene):
        def construct(self):
            r1 = Resistor().shift(UL)
            r2 = Resistor().shift(DL)
            r3 = Resistor().shift(RIGHT)
            n = Node()
            self.add(
                r1, r2, r3, n,
                Wire(r1.right, n.up).attach(),
                Wire(r2.right, n.down).attach(),
                Wire(r3.left, n.right).attach(),
            )
            n.update()

.. manim:: AutoblobbingExample
    :hide_source:
    :save_last_frame:

    from manim_eng import *

    class AutoblobbingExample(Scene):
        def construct(self):
            r1 = Resistor().shift(UL)
            r2 = Resistor().shift(DL)
            r3 = Resistor().shift(RIGHT)
            n = Node()
            self.add(
                r1, r2, r3, n,
                Wire(r1.right, n.up).attach(),
                Wire(r2.right, n.down).attach(),
                Wire(r3.left, n.right).attach(),
            )
            n.update()

.. note::

    Nodes use updaters to perform autoblobbing, and so in static scenes they need
    kicking into gear by manually calling `update()`. If you're dealing with more than
    one node, the :external+manim:meth:`manim.scene.scene.Scene.update_mobjects()`
    method on scenes can update them all at once.

If you don't want to use this behaviour, you can pass ``autoblob=False`` to the node
constructor or use the :meth:`~.Node.disable_autoblobbing` method and use
:meth:`~.Node.show_blob` or :meth:`~.Node.hide_blob` to manually control whether or not
to display a blob. (Note: these methods disable autoblobbing as well, to prevent there
being two sources of truth on whether a blob should be visible.)

Note that, by default, nodes will display their blob if autoblobbing is disabled in the
constructor. If we change the node construction to be

.. code-block:: python

    n = Node().hide_blob()

we see the below.

.. manim:: AutoblobbingExample
    :hide_source:
    :save_last_frame:

    from manim_eng import *

    class AutoblobbingExample(Scene):
        def construct(self):
            r1 = Resistor().shift(UL)
            r2 = Resistor().shift(DL)
            r3 = Resistor().shift(RIGHT)
            n = Node(autoblob=False).hide_blob()
            self.add(
                r1, r2, r3, n,
                Wire(r1.right, n.up).attach(),
                Wire(r2.right, n.down).attach(),
                Wire(r3.left, n.right).attach(),
            )
            n.update()

No blob!

.. _nodes_and_updaters:

Keeping nodes in place using updaters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:class:`~.Node`\ s provide us with a way to produce complex layouts, but currently we
can't make them responsive to component movement. That's where Manim's updaters come in.

.. note::

    This does not aim to be a comprehensive guide to updaters, as they are a Manim
    feature and not something introduced by manim-eng. This will only touch on how they
    can be used to create responsive layouts within manim-eng. If you want to learn more
    about updaters, Manim's :external+manim:doc:`deep dive<guides/deep_dive>` page
    touches on them briefly, and you can also take a look at the entries in its
    :external+manim:doc:`API docs <reference>`.

Let's examine the simple example of a potential divider.

.. code-block:: python

    class PotentialDivider(Scene):
        def construct(self):
            r1 = Resistor().shift(2 * UP).rotate(0.5 * PI)
            r2 = Resistor().shift(2 * DOWN).rotate(0.5 * PI)
            n = Node().shift(1 * DOWN)
            t = OpenNode().shift(2 * RIGHT + 1 * DOWN)

            self.add(
                r1, r2, n, t,
                Wire(r1.left, n.up).attach(),
                Wire(r2.right, n.down).attach(),
                Wire(n.right, t.left).attach(),
            )

.. manim:: PotentialDivider
    :hide_source:
    :save_last_frame:

    from manim_eng import *

    class PotentialDivider(Scene):
        def construct(self):
            r1 = Resistor().shift(2 * UP).rotate(0.5 * PI)
            r2 = Resistor().shift(2 * DOWN).rotate(0.5 * PI)
            n = Node().shift(1 * DOWN)
            t = OpenNode().shift(2 * RIGHT + 1 * DOWN)

            self.add(
                r1, r2, n, t,
                Wire(r1.left, n.up).attach(),
                Wire(r2.right, n.down).attach(),
                Wire(n.right, t.left).attach(),
            )

In a somewhat contrived manner, I've deliberately placed the open node off-centre. Let's
put that right with an animation. We'll add the following lines to our scene.

.. code-block:: python

    self.play(t.animate.shift(UP))
    self.wait()

.. manim:: PotentialDivider
    :hide_source:

    from manim_eng import *

    class PotentialDivider(Scene):
        def construct(self):
            r1 = Resistor().shift(2 * UP).rotate(0.5 * PI)
            r2 = Resistor().shift(2 * DOWN).rotate(0.5 * PI)
            n = Node().shift(1 * DOWN)
            t = OpenNode().shift(2 * RIGHT + 1 * DOWN)

            self.add(
                r1, r2, n, t,
                Wire(r1.left, n.up).attach(),
                Wire(r2.right, n.down).attach(),
                Wire(n.right, t.left).attach(),
            )

            self.play(t.animate.shift(UP))
            self.wait()

That looks fine, but it's a bit annoying that the node and open node are misaligned now.
We could of course just move the node as well, but that's kind of cumbersome. Instead,
we'll add an *updater*, which will keep the node aligned.

To do this, we'll add the line below just above the ``self.add()`` call.

.. code-block:: python

    n.add_updater(lambda mob: mob.align_terminal("right", t.left))

Note that this uses the :meth:`~.Component.align_terminal` method, a positioning method
added by manim-eng that allows you to keep terminals of different components aligned
with one another. Using this updater gives us the below.

.. manim:: PotentialDivider
    :hide_source:

    from manim_eng import *

    class PotentialDivider(Scene):
        def construct(self):
            r1 = Resistor().shift(2 * UP).rotate(0.5 * PI)
            r2 = Resistor().shift(2 * DOWN).rotate(0.5 * PI)
            n = Node().shift(1 * DOWN)
            t = OpenNode().shift(2 * RIGHT + 1 * DOWN)

            n.add_updater(lambda mob: mob.align_terminal("right", t.left))

            self.add(
                r1, r2, n, t,
                Wire(r1.left, n.up).attach(),
                Wire(r2.right, n.down).attach(),
                Wire(n.right, t.left).attach(),
            )

            self.play(t.animate.shift(UP))
            self.wait()

That looks much better. This example, although simple, hopefully shows the theory of
combining nodes and updaters to create responsive layouts.

The open node: the other kind of node
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :class:`~.OpenNode` acts precisely like a normal node, but with the centre unfilled
and :ref:`autoblobbing <autoblobbing>` disabled. It is used to represent circuit
terminals (note that this is *not* referring to the manim-eng concept of component
terminals, but the external connections to a circuit in a circuit diagram. In fact, I
snuck one in in the :ref:`previous section <nodes_and_updaters>`. For another example,
the below displays a two-port network low-pass filter.

.. code-block:: python

    class LowPassFilter(Scene):
        def construct(self):
            in_pwr = OpenNode().shift(UP + 2 * LEFT)
            in_gnd = OpenNode().shift(DOWN + 2 * LEFT)
            out_pwr = OpenNode().shift(UP + 2 * RIGHT)
            out_gnd = OpenNode().shift(DOWN + 2 * RIGHT)
            r = Resistor().shift(UP + 0.5 * LEFT)
            c = Capacitor().shift(RIGHT).rotate(0.5 * PI)
            node_up = Node().shift(UR)
            node_down = Node().shift(DR)

            self.add(
                in_pwr, in_gnd, out_pwr, out_gnd,
                r, c,
                node_up, node_down,
                Wire(in_pwr.right, r.left).attach(),
                Wire(in_gnd.right, node_down.left).attach(),
                Wire(r.right, node_up.left).attach(),
                Wire(node_up.right, out_pwr.left).attach(),
                Wire(node_down.right, out_gnd.left).attach(),
                Wire(node_up.down, c.right).attach(),
                Wire(node_down.up, c.left).attach(),
            )
            self.update_mobjects(0)

.. manim:: LowPassFilter
    :hide_source:
    :save_last_frame:

    from manim_eng import *

    class LowPassFilter(Scene):
        def construct(self):
            in_pwr = OpenNode().shift(UP + 2 * LEFT)
            in_gnd = OpenNode().shift(DOWN + 2 * LEFT)
            out_pwr = OpenNode().shift(UP + 2 * RIGHT)
            out_gnd = OpenNode().shift(DOWN + 2 * RIGHT)
            r = Resistor().shift(UP + 0.5 * LEFT)
            c = Capacitor().shift(RIGHT).rotate(0.5 * PI)
            node_up = Node().shift(UR)
            node_down = Node().shift(DR)

            self.add(
                in_pwr, in_gnd, out_pwr, out_gnd,
                r, c,
                node_up, node_down,
                Wire(in_pwr.right, r.left).attach(),
                Wire(in_gnd.right, node_down.left).attach(),
                Wire(r.right, node_up.left).attach(),
                Wire(node_up.right, out_pwr.left).attach(),
                Wire(node_down.right, out_gnd.left).attach(),
                Wire(node_up.down, c.right).attach(),
                Wire(node_down.up, c.left).attach(),
            )
            self.update_mobjects(0)

Advanced wiring: the ``ManualWire`` class
-----------------------------------------

The automatic wire routing is great, but sometimes, you need something custom. In this
case, you have two options. The first is to subclass the :class:`~.WireBase` class ---
this is particularly good if you want to encode new routing behaviour to use repeatedly.

The other, simpler, method is the :class:`~.ManualWire` class. This requires a list of
points at which the wire should have corners, which can be updated later using the
:meth:`~.ManualWire.set_corner_points` method if desired. This can be combined with an
updater to make a responsive wire, but if using anything more than trivial logic for
this you probably want to be using the subclassing option above.

Let's take a look at :class:`~.ManualWire` in action. For this we'll use a simple
'switchboard', which aptly demonstrates the main use case of the :class:`~.ManualWire`:
it facilitates diagonal wires.

.. code-block:: python

    class Switchboard(Scene):
        def construct(self):
            in1 = OpenNode().shift(UP + 2 * LEFT)
            in2 = OpenNode().shift(DOWN + 2 * LEFT)
            out1 = OpenNode().shift(UP + 2 * RIGHT)
            out2 = OpenNode().shift(DOWN + 2 * RIGHT)
            self.add(in1, in2, out1, out2)
            self.add(
                ManualWire(
                    in1.right, out2.left, [UP + 0.5 * LEFT, DOWN + 0.5 * RIGHT]
                ).attach(),
                ManualWire(
                    in2.right, out1.left, [DOWN + 0.5 * LEFT, UP + 0.5 * RIGHT]
                ).attach(),
            )

.. manim:: Switchboard
    :hide_source:
    :save_last_frame:

    from manim_eng import *

    class Switchboard(Scene):
        def construct(self):
            in1 = OpenNode().shift(UP + 2 * LEFT)
            in2 = OpenNode().shift(DOWN + 2 * LEFT)
            out1 = OpenNode().shift(UP + 2 * RIGHT)
            out2 = OpenNode().shift(DOWN + 2 * RIGHT)
            self.add(in1, in2, out1, out2)
            self.add(
                ManualWire(
                    in1.right, out2.left, [UP + 0.5 * LEFT, DOWN + 0.5 * RIGHT]
                ).attach(),
                ManualWire(
                    in2.right, out1.left, [DOWN + 0.5 * LEFT, UP + 0.5 * RIGHT]
                ).attach(),
            )

In fact, if you just want to connect two terminals directly, you don't need to specify
the list of corner points at all. Let's look at what this would look like in our
switchboard example.

.. code-block:: python

    class Switchboard(Scene):
        def construct(self):
            in1 = OpenNode().shift(UP + 2 * LEFT)
            in2 = OpenNode().shift(DOWN + 2 * LEFT)
            out1 = OpenNode().shift(UP + 2 * RIGHT)
            out2 = OpenNode().shift(DOWN + 2 * RIGHT)
            self.add(in1, in2, out1, out2)
            self.add(
                ManualWire(in1.right, out2.left).attach(),
                ManualWire(in2.right, out1.left).attach(),
            )

.. manim:: Switchboard
    :hide_source:
    :save_last_frame:

    from manim_eng import *

    class Switchboard(Scene):
        def construct(self):
            in1 = OpenNode().shift(UP + 2 * LEFT)
            in2 = OpenNode().shift(DOWN + 2 * LEFT)
            out1 = OpenNode().shift(UP + 2 * RIGHT)
            out2 = OpenNode().shift(DOWN + 2 * RIGHT)
            self.add(in1, in2, out1, out2)
            self.add(
                ManualWire(in1.right, out2.left).attach(),
                ManualWire(in2.right, out1.left).attach(),
            )

As can be seen above, the wires now go directly from one terminal to another.

``Circuit``\ s: a teaser
------------------------

With that, you should now have a decent idea of the ways you can use and customise
manim-eng's various wire types. Those of you who have gone through the
:doc:`tutorial <first_circuit_diagram/index>` will note that we are yet to touch on one
other class that can perform wiring: the :class:`~.Circuit`. This deserved to be handled
separately, and so is outlined in the next guide.

.. rubric:: Footnotes

.. [#terminal_invisibility] This is achieved through the ``auto`` parameter on the
    :class:`~.Terminal` constructor --- see the Terminal API docs for more details.
