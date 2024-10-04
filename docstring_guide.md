# Docstring guide

This short guide aims to be a quick reference on how docstrings should be written, for consistency. First of all,
manim-eng's docstrings follow the `numpydoc` standard, so the
[style guide](https://numpydoc.readthedocs.io/en/latest/format.html) for that should be a first reference. It doesn't
cover specifics however, so this aims to clear up some ambiguity for this specific project.

## Modules

Module docstrings should follow the `numpydoc` standard. The summary line should not include the words 'module',
'package', or similar, as the fact that it is a module is obvious. It should rather be a summary of what the module
*contains*.

## Classes

### Class docstrings

Classes should have a summary line that describes the classes' purpose. They should not include the word 'class', unless
referring to the wider class heirarchy: 'base class' is fine, as that is an accurate descriptor of the purpose of the
class, but e.g. 'class encoding the circuit symbol for...' is not (it should just be 'circuit symbol for...').

### Methods

Methods should be documented in more depth, but not to the point of verbosity. If one line will suffice, one line is all
that is needed. In particular, methods that have `-> Self` in their signature need not have a `Returns` section in their
docstring: this adds an extra four lines (including the blank one) but doesn't add any extra meaning. It is obvious from
the signature that the method mutates the object and then returns the object.
