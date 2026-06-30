# PDF-Extract

## With uv (recommended)

No setup required — uv installs dependencies into an isolated environment automatically:

```
uv run --with pillow --with pypdf extract-pdf-img.py <input.pdf>
```

Or install once into a project environment:

```
uv init
uv add pillow pypdf
uv run extract-pdf-img.py <input.pdf>
```

## With conda (legacy)

```
conda create -n pdf-extract
conda activate pdf-extract
conda install -y python
pip install -r requirements.txt
```

> **Note:** `requirements.txt` uses `pypdf` (the successor to the deprecated `PyPDF2`).
