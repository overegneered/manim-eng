Defining new units and prefixes
===============================

.. tip::

    See also:

    - The :ref:`value expressions <value_expressions>` section in the
      :doc:`marks guide <../guides/marks>`; and
    - The :mod:`~.units` module API documentation.

manim-eng's unit system defines most of the units you would expect to be using
day-to-day, but cannot hope to cover all possible situations (in particular, it doesn't
define any imperial units). Thankfully, the process of defining your own units
(and indeed prefixes) is very simple.

Defining units
--------------

Units are defined using the :class:`~.Unit` class (which is imported by default and
doesn't require a ``manim_eng.implementation`` import). The constructor only requires
one argument: a string with the unicode representation of the unit.

.. code-block:: python

    ERLANG = Unit("E")

manim-eng uses a
:external+manim:class:`MathTex< manim.mobject.text.tex_mobject.MathTex>` to display
units. By default, it assumes that the string you passed before when wrapped in
``\mathrm{}`` is the correct LaTeX math mode string to represent the unit symbol. If
this is not the case, you can use the ``latex`` parameter to specify a custom string (it
will still be wrapped in ``\mathrm{}``.

.. code-block:: python

    MHO = Unit("℧", latex=r"\mho")

Defining prefixes
-----------------

Within the unit system, prefixes are just considered 'special' units that attach
themselves to the unit after them and don't themselves adopt an exponent. To declare a
prefix, the process is the same as outlined above for units, except the ``prefix``
parameter is set to ``True``:

.. code-block:: python

    MYRIA = Unit("my", prefix=True)

As a note, manim-eng defines the following prefixes already:

- The standard SI set of prefixes in jumps of 10\ :sup:`3` from 10\ :sup:`-30` (quecto) to
  10\ :sup:`30` (quetta);
- The other SI prefixes hecto, deca, deci, and centi; and
- The IEC binary prefixes in jumps of 2\ :sup:`10` from kibi (2\ :sup:`10`) to yobi (2\ :sup:`100`).
