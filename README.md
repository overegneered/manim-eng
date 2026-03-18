![manim-eng logo](docs/source/_static/logo.png)

---

manim-eng is a plugin for the [Manim Community](https://www.manim.community/) animation engine that introduces
symbols and utilities for drawing engineering diagrams. Currently this only includes
circuits, but the goal is to extend this to structures in the future as well.

### Why make another circuit library?

Quite simply, because the other options available just don't cut it for me. The
[manim-circuit](https://github.com/Mr-FuzzyPenguin/manim-circuit/blob/main/README.md)
plugin, which was released during early development of this plugin, comes closer to what
I want, but still isn't quite there. My goal can be summed up as 'manim-eng should be to
ManimCE what CircuiTikZ is to LaTeX'. This means:

- Easy to configure and automatically placed labels, annotations, and current and voltage indications.
- Automatic, sensible animations for when these labels are introduced, removed, or changed.
- Automatic component connections.
- Ability to specify component types (i.e. European or American), with as much or as little granularity as you wish.

Those who know CircuiTikZ will know that it can't actually do all of the above, but why
not make something better than your inspiration? On top of these features, I wanted a
clean, intuitive, Pythonic interface to the library. No available option that I could
find had all of this. Making my own was also an excellent way to get familiar with
Manim, and a fun project.

## Getting started

Head over to the [documentation](https://docs.manim-eng.egneer.ing) to get started with your first circuit diagrams!

## Development

### Environment setup

manim-eng, like Manim itself, uses [uv](https://docs.astral.sh/uv/) as a package manager
and build system. You will need uv installed before proceeding. First, clone the
repository with Git:

```shell
git clone https://github.com/overegneered/manim-eng.git
```

Then install dependencies with uv:

```shell
uv sync --extra dev
```

Finally, install the pre-commit hooks:

```shell
uv run pre-commit install
```

### Testing

manim-eng uses [pytest](https://pytest.org) as a testing framework. To run the test
suite, you can use

```shell
uv run pytest
```

though using an IDE integration, such as PyCharm's pytest runner, may be easier!

### Documentation

manim-eng uses [Sphinx](https://www.sphinx-doc.org/en/master/index.html) for its
documentation. It is set up to be built from the root directory using

```shell
sphinx-build -M html docs/source docs/build
```

though when editing on the documentation, using
[sphinx-autobuild](https://github.com/sphinx-doc/sphinx-autobuild) is going to be
easier:

```shell
sphinx-autobuild docs/source docs/build
```

sphinx-autobuild is included in the `docs` dependency group, so you can use

```shell
uv sync --extra docs
```

to install it if you don't have it already.

## Licencing and citation

If you use this project in your work, I ask that you cite it using the information
contained in the [`CITATION.cff`](https://github.com/overegneered/manim-eng/blob/trunk/CITATION.cff) file. The easiest way to do this is to go to the
[repository page](https://github.com/overegneered/manim-eng) on GitHub and click on
'Cite this repository'. For more info on `CITATION.cff` files, check out
[this website](https://citation-file-format.github.io/).

This project is provided under the terms of the MIT licence.
