# depgraph

Visualize Python project dependency trees as interactive SVG graphs.

---

## Installation

```bash
pip install depgraph
```

Or install from source:

```bash
git clone https://github.com/yourname/depgraph.git && cd depgraph && pip install .
```

---

## Usage

Analyze a project's dependencies and generate an interactive SVG graph:

```bash
depgraph generate --output deps.svg
```

You can also point it at a specific `requirements.txt` or `pyproject.toml`:

```bash
depgraph generate --input requirements.txt --output deps.svg
```

Use it as a library inside your own scripts:

```python
from depgraph import build_graph, render_svg

graph = build_graph("requirements.txt")
render_svg(graph, output="deps.svg")
```

Open the resulting `deps.svg` in any modern browser to explore the interactive dependency tree — zoom, pan, and click nodes to highlight direct relationships.

---

## Options

| Flag | Description |
|------|-------------|
| `--input` | Path to `requirements.txt` or `pyproject.toml` (default: auto-detect) |
| `--output` | Output SVG file path (default: `deps.svg`) |
| `--depth` | Max dependency depth to render (default: unlimited) |

---

## License

This project is licensed under the [MIT License](LICENSE).