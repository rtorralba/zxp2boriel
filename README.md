# zxp2boriel

A Python tool to convert ZX-Paintbrush (.zxp) sprite files into Boriel Basic `DIM` array declarations.

## Installation

```bash
pip install zxp2boriel
```

## Usage

```bash
zxp2boriel --input <file.zxp> --width <pixels> --rows <rows> --cols <cols> --output <file.bas> --name <array_name>
```

### Arguments

- `--input`, `-i`: Input .zxp file path.
- `--width`, `-w`: Tile width in pixels (must be a multiple of 8).
- `--rows`, `-r`: Number of rows in the sprite sheet.
- `--cols`, `-c`: Number of columns in the sprite sheet.
- `--output`, `-o`: Output .bas file path.
- `--name`, `-n`: Name of the generated array variable.

### Example

Convert a 16x16 sprite sheet with 3 rows and 16 columns:

```bash
zxp2boriel -i sprites.zxp -w 16 -r 3 -c 16 -o sprites.bas -n tiles
```

This will generate a `sprites.bas` file containing:

```basic
Dim tiles(47, 31) As Ubyte => { ... }
```

## License

AGPL-v3
