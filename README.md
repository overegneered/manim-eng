![manim-eng logo](docs/source/_static/logo.png)

---

manim-eng is a plugin for the [Manim Community](https://www.manim.community/) animation engine that introduces symbols and utilities for drawing engineering diagrams.
Currently this only includes circuits, but the goal is to extend this to structures in the future as well.

### Why make another circuit library?

Quite simply, because the other options available just don't cut it for me. The [manim-circuit](https://github.com/Mr-FuzzyPenguin/manim-circuit/blob/main/README.md) plugin, which was released during early development of this plugin, comes closer to what I want, but still isn't quite there. My goal can be summed up as 'manim-eng should be to ManimCE what CircuiTikZ is to LaTeX'. This means:

- Easy to configure and automatically placed labels, annotations, and current and voltage indications.
- Automatic, sensible animations for when these labels are introduced, removed, or changed.
- Automatic component connections.
- Ability to specify component types (i.e. European or American), with as much or as little granularity as you wish.

Those who know CircuiTikZ will know that it can't actually do all of the above, but why not make something better than your inspiration? On top of these features, I wanted a clean, intuitive, Pythonic interface to the library. No available option that I could find had all of this. Making my own was also an excellent way to get familiar with Manim, and a fun project.

## Getting started

Head over to the [documentation](https://docs.manim-eng.egneer.ing) to get started with your first circuit diagrams!

## Development

### Environment setup

manim-eng, like Manim itself, uses [Poetry](https://python-poetry.org/) as a build system. You will need Poetry
installed before proceeding. First, clone the repository with Git:

```shell
git clone https://github.com/overegneered/manim-eng.git
```

Then install dependencies with Poetry:

```shell
poetry install
```

Finally, install the pre-commit hooks:

```shell
pre-commit install
```

### Testing

manim-eng uses [pytest](https://pytest.org) as a testing framework. To run the test suite, you can use

```shell
poetry run pytest
```

though using an IDE integration, such as PyCharm's pytest runner, may be easier!

## Licencing and citation

If you use this project in your work, I ask that you cite it using the information contained in the [`CITATION.cff`](https://github.com/overegneered/manim-eng/blob/trunk/CITATION.cff) file. The easiest way to do this is to go to the [repository page](https://github.com/overegneered/manim-eng) on GitHub and click on 'Cite this repository'. For more info on `CITATION.cff` files, check out [this website](https://citation-file-format.github.io/).

This project is mostly licenced under the MIT licence, like Manim itself. However, I specifically revoke any right or permissions to use the contents of this repository for the training of AI models without my prior written approval.
