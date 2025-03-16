Building custom components
==========================

It's not unlikely that when using manim-eng you will want to implement your own circuit
symbols, especially given manim-eng's current infancy. This page aims to guide you
through the process of doing so, through the lens of building the resistor symbol.

.. note::

    On this page I frequently use the term 'mobject' generally. The :class:`~.Component`
    base class expects that mobjects used to form component symbols will specifically be
    :external+manim:class:`VMobject <manim.mobject.types.vectorized_mobject.VMobject>`
    \ s. I use mobject as it is easier to read than vmobject, but only vmobjects may be
    used to form component symbols.

Step 1: import the implementation API
-------------------------------------

First, import the standard and base classes. To avoid cluttering the global namespace,
the classes required to implement your own components are kept in the ``implementation``
submodule.

.. code-block:: python

    from manim_eng import *
    from manim_eng.implementation import *


Step 2: choose the right base class
-----------------------------------

While you can get along only using the :class:`~.Component` class for all components you
wish to implement, it's better to use the right base class for the job. This will ensure
consistency of API with the rest of manim-eng and allow you to focus on just building
your symbol.

The base class hierarchy looks something like this:

.. inheritance-diagram::
    manim_eng.components.base.bipole
    manim_eng.components.base.component
    manim_eng.components.base.monopole
    manim_eng.components.base.source
    manim_eng.components.base.switch
    manim_eng.components.base.xkcd
    :parts: 1
    :top-classes: manim_eng.components.base.component.Component

Your component can derive from any of these, but some are more appropriate for certain
applications than others. The table below outlines the intended uses for each.

====================================  ==================================================
Base class                            Purpose
====================================  ==================================================
:class:`~.Component`                  Specialised components not handled by the
                                      subclasses below (currently most likely to be
                                      components with more than two terminals).
:class:`~.Bipole`                     Two-terminal components with rectangular symbol
                                      footprints, such as resistors and inductors. Adds
                                      :attr:`~.Bipole.left` and :attr:`~.Bipole.right`
                                      properties to easily access the left and right
                                      terminals. Sets up two terminals at the standard
                                      rectangular bipole distance apart.
:class:`~.SquareBipole`               Two-terminal components with square symbol
                                      footprints, such as capacitors (and sources, but
                                      these have the :class:`~.Source` subclass, see
                                      below). Sets up two terminals at the standard
                                      square bipole distance apart.
:class:`~.Source`                     Source symbols (such as cells). Adds
                                      :attr:`~.Source.positive`,
                                      :attr:`~.Source.negative`, :attr:`~.Source.anode`,
                                      and :attr:`~.Source.cathode` properties to easily
                                      access the respective terminals.
:class:`~.CurrentSourceBase`          Current source symbols. Adds a ``current``
                                      parameter to the constructor for setting the
                                      source's current.
:class:`~.EuropeanCurrentSourceBase`  European current source symbols (with a vertical
                                      line).
:class:`~.VoltageSourceBase`          Voltage source symbols. Adds a ``voltage``
                                      parameter to set the source's voltage, as well as
                                      a specialised straight voltage arrow set up as
                                      part of the component.
:class:`~.EuropeanVoltageSourceBase`  European voltage source symbols (with a horizontal
                                      line).
:class:`~.RandalMunroeSourceBase`     Specialised voltage source for building symbols
                                      for Randal Munroe's baertty and battttttttttttery.
:class:`~.Monopole`                   Components with a single terminal, such as grounds
                                      and power rails. Removes the ability to set
                                      annotations, as monopole components do not support
                                      them.
====================================  ==================================================

In our running example, we want to select the :class:`~.Bipole` class, as a resistor is
a standard rectangular bipole.

.. code-block:: python

    from manim_eng import *
    from manim_eng.implementation import *

    class Resistor(Bipole):
        # read on...

Step 3: override the ``_construct()`` method
--------------------------------------------

A component's :meth:`~.Component._construct` method works much the same as a Manim
scene's :external+manim:meth:`construct() <manim.scene.scene.Scene.construct>` method.
Components should override this method and populate it with the code to build their
symbol.

.. warning::

    This is contrary to Manim's standard of performing symbol construction in the
    ``__init__()`` constructor. This is done because the base constructor in
    :class:`~.Component` needs to set things up both before and after the component
    structure is specified.

Step 3(a): call the superclass' ``_construct()`` method
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You need to make sure to call the superclass' ``_construct()`` method as well, as some
of the base classes perform their own construction (as an example,
:class:`~.EuropeanVoltageSourceBase` constructs a horizontal line). That gets us this
far...

.. code-block:: python

    from manim_eng import *
    from manim_eng.implementation import *

    class Resistor(Bipole):
        def _construct(self):
            super()._construct()

Step 3(b): build the mobjects representing the symbol
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For a resistor, we want to construct a rectangle. The question, though, is what its
dimensions should be and where it should be placed.

We'll first consider the second question. manim-eng symbols are always taken to be
centred on the origin of their construction (much like Manim mobjects). However, there
*is* a difference: manim-eng components take their centre to be the position of their
centre anchor, and *not* the geometric centre of the symbol. To illuminate this,
consider the example of an inductor. The symbol is not central on the centre anchor, but
rotates around its centre anchor (purple below).

.. manim:: RotatingInductor
    :hide_source:

    from manim_eng import *

    config.frame_width = 2.5
    config.pixel_width = 512
    config.pixel_height = 512
    config_eng.debug = True

    class RotatingInductor(Scene):
        def construct(self):
            l = Inductor()
            self.play(Rotating(l, run_time=5))

So, to bring it back to our resistor: our rectangle should be centred on the origin.

.. code-block:: python

    from manim_eng import *
    from manim_eng.implementation import *

    class Resistor(Bipole):
        def _construct(self):
            super()._construct()
            box = Rectangle()

Now, what size should it be? Well, manim-eng has a series of standard sizes for
components, configured via its configuration system. If you're building a symbol that
conforms to a certain size category, you should make it thr right size. In our case,
a resistor is a standard bipole (i.e. it has two terminals), so we care about the
:attr:`~.ComponentSymbolConfig.bipole_width` and
:attr:`~.ComponentSymbolConfig.bipole_height` lengths.

Combining these, we can get a rectangle in the right place with the right size:

.. code-block:: python

    from manim_eng import *
    from manim_eng.implementation import *

    class Resistor(Bipole):
        def _construct(self):
            super()._construct()
            box = Rectangle(
                width=config_eng.symbol.bipole_width,
                height=config_eng.symbol.bipole_width,
            )

Step 3(c): match the style of the mobjects
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

manim-eng uses different stroke widths for different parts of components (most notably,
symbols and wires use two different thicknesses). On top of this, we need to maintain
support for other customisations passed to components that go all the way up to their
mobject constructors. This requires that mobjects constructed as part of a component
symbol be 'matched' to their parent mobject.

For simple symbols, this is easily done using the ``match_style()`` method on all
:external+manim:class:`VMobject <manim.mobject.types.vectorized_mobject.VMobject>`\ s.
This essentially copies over the key styling attributes from one mobject to another.

.. code-block:: python

    from manim_eng import *
    from manim_eng.implementation import *

    class Resistor(Bipole):
        def _construct(self):
            super()._construct()
            box = Rectangle(
                width=config_eng.symbol.bipole_width,
                height=config_eng.symbol.bipole_width,
            ).match_style(self)

In more complex cases, you may need to exercise more judgement and copy parameters over
more conservatively (especially when considering fills).

Step 3(d): add the mobjects to the component body
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :class:`~.Component` base class places the label and annotation anchors
automatically based on the shape of the component. To avoid terminals influencing these
calculations, :class:`~.Component` needs to be able to differentiate between the
component body and its terminals. As such, it maintains two
:external+manim:class:`VGroup <manim.mobject.types.vectorized_mobject.VGroup>`\ s, one
for the body (``_body``) and one for the terminals (``_terminals``).

All this is to say that when adding mobjects to form a component's body, they should be
added to ``self._body``:

.. code-block:: python

    from manim_eng import *
    from manim_eng.implementation import *

    class Resistor(Bipole):
        def _construct(self):
            super()._construct()
            box = Rectangle(
                width=config_eng.symbol.bipole_width,
                height=config_eng.symbol.bipole_height,
            ).match_style(self)
            self._body.add(box)

If we now append some basic visualisation code, we see exactly what we want!

.. manim:: ResistorExample
    :hide_source:
    :save_last_frame:

    from manim_eng import *
    from manim_eng.implementation import *

    config.frame_width = 2.5
    config.pixel_width = 512
    config.pixel_height = 256
    config_eng.debug = False

    class Resistor(Bipole):
        def _construct(self):
            super()._construct()
            box = Rectangle(
                width=config_eng.symbol.bipole_width,
                height=config_eng.symbol.bipole_height,
            ).match_style(self)
            self._body.add(box)

    class ResistorExample(Scene):
        def construct(self):
            r = Resistor()
            self.add(r)

.. note::

    The extra visualisation code is as below.

    .. code-block:: python

        config.frame_width = 2.5
        config.pixel_width = 512
        config.pixel_height = 256

        class ResistorExample(Scene):
            def construct(self):
                r = Resistor()
                self.add(r)

Finally, we visualise with the :doc:`debug mode <debug_mode>` enabled, to see that the
label (red) and annotation (blue) anchors have been correctly automatically placed on
the top and bottom of our component.

.. manim:: ResistorExample
    :hide_source:
    :save_last_frame:

    from manim_eng import *
    from manim_eng.implementation import *

    config.frame_width = 2.5
    config.pixel_width = 512
    config.pixel_height = 256
    config_eng.debug = True

    class Resistor(Bipole):
        def _construct(self):
            super()._construct()
            box = Rectangle(
                width=config_eng.symbol.bipole_width,
                height=config_eng.symbol.bipole_height,
            ).match_style(self)
            self._body.add(box)

    class ResistorExample(Scene):
        def construct(self):
            r = Resistor()
            self.add(r)


Using modifiers to avoid duplication
------------------------------------

The symbol modifiers
^^^^^^^^^^^^^^^^^^^^

Standard component symbols can be modified in a number of ways to indicate an additional
quality (such as a diagonal arrow indicating variability). To avoid coding these
repeatedly, manim-eng defines them as separate base classes that you can inherit from
*as well as* the base symbol. These have special ``_construct()`` methods that
interrogate the shape of the symbol created and then intelligently place the modifier
symbol over the top.

.. important::

    For modifiers to be able to work intelligently based on the component symbol size,
    it is *essential* that the component body be placed in ``self._body`` and that the
    modifier be inherited from *first* (as the way Python resolves calling a tree of
    ``super()._construct()`` calls will then mean that its ``_construct()`` method will
    be called after that of the base symbol.

There are two general-purpose modifiers currently provided by manim-eng: the
:class:`~.SensorModifier` (a 'bent L') and the :class:`~.VariableModifier` (a diagonal
arrow). Let's look at what these look like when applied to our resistor from above.

The additional code is

.. code-block:: python

    class Thermistor(SensorModifier, Resistor):
        def _construct(self) -> None:
            super()._construct()


    class VariableResistor(VariableModifier, Resistor):
        def _construct(self) -> None:
            super()._construct()

and the resulting symbols are

.. manim:: ResistorModifiers
    :hide_source:
    :save_last_frame:

    from manim_eng import *
    from manim_eng.implementation import *

    config.pixel_width = 1024
    config.pixel_height = 256
    config_eng.debug = False

    class ResistorModifiers(Scene):
        def construct(self):
            r = Resistor().shift(4.5 * LEFT)
            t = Thermistor()
            v = VariableResistor().shift(4.5 * RIGHT)
            self.add(r, t, v)
            self.add(
                Tex(r"\textsf{no modifier}").shift(DOWN + 4.5 * LEFT),
                Tex(r"\texttt{SensorModifier}").shift(DOWN),
                Tex(r"\texttt{VariableModifier}").shift(DOWN + 4.5 * RIGHT),
            )
            self.add(
                Tex(r"\texttt{Resistor}").shift(UP + 4.5 * LEFT),
                Tex(r"\texttt{Thermistor}").shift(UP),
                Tex(r"\texttt{VariableResistor}").shift(UP + 4.5 * RIGHT),
            )

You may recognise these as a resistor, a thermistor, and a variable resistor. In fact,
this is precisely how manim-eng's :class:`~.Thermistor` and :class:`~.VariableResistor`
classes are defined!

The outline modifiers
^^^^^^^^^^^^^^^^^^^^^

manim-eng also has two outline modifiers, which add either a circular (in the case of
:class:`~.RoundOuter`) or a diamond (in the case of :class:`~.DiamondOuter`) outline of
a size commensurate to a square bipole (that is, using the
:attr:`~.ComponentSymbolConfig.square_bipole_side_length` configuration value). These
are used to allow sources to be built in a duplication-minimal way, as the image below
should hopefully illuminate.

.. manim:: OutlineModifierExample
    :hide_source:
    :save_last_frame:

    from manim_eng import *
    from manim_eng.implementation import *

    config.frame_width = 5
    config.pixel_width = 1000
    config.pixel_height = 600

    class OutlineModifierExample(Scene):
        def construct(self):
            self.add(
                VoltageSource().shift(LEFT),
                CurrentSource().shift(RIGHT),
                ControlledVoltageSource().shift(DL),
                ControlledCurrentSource().shift(DR),
            )
            self.add(
                Tex(r"\sf \textbf{Base class}", font_size=28).shift(UP),
                Tex(r"\texttt{EuropeanVoltageSourceBase}", font_size=14).shift(LEFT + 0.5 * UP),
                Tex(r"\texttt{EuropeanCurrentSourceBase}", font_size=14).shift(RIGHT + 0.5 * UP),
            )
            self.add(
                Tex(r"\sf \textbf{Modifier}", font_size=28).shift(2.5 * LEFT + 0.5 * DOWN).rotate(PI/2),
                Tex(r"\texttt{RoundOuter}", font_size=14).shift(LEFT + LEFT).rotate(PI/2),
                Tex(r"\texttt{DiamondOuter}", font_size=14).shift(DL + LEFT).rotate(PI/2),
            )
            for m in self.mobjects:
                m.shift(RIGHT * 0.3 + UP * 0.125)
