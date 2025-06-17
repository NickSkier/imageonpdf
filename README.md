# ImageOnPDF

A command-line utility for placing images onto PDF pages according to a JSON/YAML configuration.
Excellent for PDF mass editing.
Supports:

- Regular images
- Randomly selected images
- Disposable random images (moved after use)
- Cropping pages (by points or percent)
- Page size inspection
- YAML or JSON configuration

The tool is built using `PyMuPDF` (`fitz`) and can be run either with **uv** or with the standard Python environment.

---

## Features

### Image placement

- Place images at specific coordinates on a specific page.
- Place images on **all pages** automatically.
- Scale images using a size factor.
- Random image selection from a directory.
- Disposable random images moved to another directory after insertion.

### PDF editing

- Crop pages by percentage (positive or negative).
- Crop pages by point coordinates.
- Print page size in points.

### Configuration

Supports both:

- `images.json`
- `images.yaml`

Example config files can be found in `json_example.json` and `yaml_example.yaml` or in README.

---

## Usage

### Download repository

```sh
git clone https://github.com/NickSkier/imageonpdf.git
```

### Using uv

The project is structured for use with **uv**.

#### Install dependencies

```sh
uv sync
```

#### Run

```sh
uv run main.py -i input.pdf -o output.pdf -c images.json
```

---

### Using standart Python

#### Install dependencies

```sh
pip install pymupdf pyyaml
```

#### Run

```sh
python main.py -i input.pdf -o output.pdf -c images.json
```

---

## Configuration Format

### JSON example

```json
{
  "images": [
    {
      "path": "fixed/logo.png",
      "page": 0,
      "x": 50,
      "y": 50,
      "size": 1.0
    }
  ],
  "random_images": [
    {
      "path": "random_images/",
      "page": "all",
      "x": 100,
      "y": 100,
      "size": 0.5
    }
  ],
  "disposable_random_images": [
    {
      "path": "tmp_images/",
      "disposed_path": "used_images/",
      "page": 0,
      "x": 200,
      "y": 200,
      "size": 1.2
    }
  ]
}
```

### YAML example

```yaml
images:
  - path: fixed/logo.png
    page: 0
    x: 50
    y: 50
    size: 1.0

random_images:
  - path: random_images/
    page: all
    x: 100
    y: 100
    size: 0.5

disposable_random_images:
  - path: tmp_images/
    disposed_path: used_images/
    page: 0
    x: 200
    y: 200
    size: 1.2
```

---

## CLI Arguments

| Argument            | Description                          |
| ------------------- | ------------------------------------ |
| `-i`, `--pdf`       | Input PDF (default: `input.pdf`)     |
| `-o`, `--output`    | Output PDF (default: `output.pdf`)   |
| `-c`, `--json`      | JSON config (default: `images.json`) |
| `--yaml`            | YAML config (optional)               |
| `--skip-all`        | Skip placing any images              |
| `--skip-regular`    | Skip regular images                  |
| `--skip-random`     | Skip random images                   |
| `--skip-disposable` | Skip disposable random images        |
| `-v`, `--verbose`   | Verbose output                       |
| `--page-size N`     | Print page size of page N            |
| `--crop …`          | Crop page by percentage              |
| `--crop-points …`   | Crop page by point coordinates       |

---

## Cropping

### Crop by percent

```
--crop page width_percent [height_percent]
```

Examples:

Crop page 2 to 20% width and full height:

```
--crop 2 20
```

Crop page 2 from right side (negative width) and bottom side (negative height):

```
--crop 2 -30 -40
```

### Crop by points

```
--crop-points page width height [x y]
```

Example:

```
--crop-points 2 300 500 20 20
```

---

## Examples

### Place all images

```sh
python main.py -i input.pdf -o output.pdf -c images.json
```

### Use YAML config

```sh
python main.py --yaml config.yaml
```

### Only random images

```sh
python main.py --skip-regular --skip-disposable
```

### Only crop without adding images

```sh
python main.py -i in.pdf -o out.pdf --crop 2 50
```

---

## Output

When any transformation is applied, the final PDF is saved to the path provided via:

```
-o output.pdf
```

Default: `output.pdf`.
