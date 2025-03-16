Configuration
=============

If you're familiar with Manim's configuration system, manim-eng's shouldn't come as too
much of a surprise. There are three ways to set configuration:

1. Editing the global ``config_eng`` object, an instance of :class:`~.ManimEngConfig`;
2. Using the :func:`~.tempconfig_eng` context manager; and
3. Using a :file:`manim-eng.toml` configuration file.

``config_eng``
--------------

This is the fundamental underlying representation of manim-eng's configuration, and all
other methods ultimately edit this object. To get an idea of all of the available
options, check out the :class:`~.ManimEngConfig` API documentation.

It is worth noting that, unlike Manim's
:external+manim:class:`~manim._config.utils.ManimConfig` (which underlies its ``config``
object), :class:`~.ManimEngConfig` (and hence ``config_eng``) does *not* support using
dict-like syntax to set values.


.. _tempconfig_eng_narrative:

The ``tempconfig_eng`` context manager
--------------------------------------

This works very similarly to Manim's :func:`~manim._config.tempconfig` --- you pass a
dictionary representing the configuration you wish to temporarily apply, and once the
context manager exits the edited values are returned to their previous values.

>>> from manim_eng import *
>>> config_eng.symbol.bipole_width
0.4
>>> with tempconfig_eng({"symbol": {"bipole_width": 0.5}}):
...     print(config_eng.symbol.bipole_width)
...
0.5
>>> config_eng.symbol.bipole_width
0.4

.. tip::

    To set a nested value, you need to nest dictionaries. For example, to temporarily
    set the ``config_eng.symbol.bipole_width`` configuration value to ``0.5``, you would
    *not* be able to use

    .. code-block:: python

        {"symbol.bipole_width": 0.5}

    but would instead need to use

    .. code-block:: python

        {"symbol": {"bipole_width": 0.5}}

    as above.

The ``manim-eng.toml`` config files
-----------------------------------

There are two levels of config file: user-level and project-level. The user-level file
is

- :file:`~/.config/manim/manim-eng.toml` on Linux and macOS; and
- :file:`~\AppData\Roaming\Manim\manim-eng.toml` on Windows.

Project-level configuration is placed in a file called :file:`manim-eng.toml` in the
root of your project's working directory.

The structure of a ``manim-eng.toml``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Like the :func:`~manim._config.tempconfig` :ref:`above <tempconfig_eng_narrative>`, a
:file:`manim-eng.toml` needs to reflect the structure of :class:`~.ManimEngConfig`. This
essentially means that, where a subclass exists in :class:`~.ManimEngConfig`, that
translates to a TOML table, and where a field exists, that becomes a TOML field.

By way of an example, if we wanted to set ``config_eng.symbol.bipole_width`` to ``0.5``,
the contents of a :file:`manim-eng.toml` to do so would be as below.

.. code-block:: toml

    [symbol]
    bipole_width = 0.5

Configuration priority
----------------------

When determining values for a given configuration value, the following order is used:

1. Values set in code, either by directly editing ``config_eng`` or using the
   :func:`~.tempconfig_eng()` context manager.
2. Values set in the project-level :file:`manim-eng.toml`.
3. Values set in the user-level :file:`manim-eng.toml`.
4. The default values (see the :class:`~.ManimEngConfig` documentation).
