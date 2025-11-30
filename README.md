# zxp2boriel

A Python tool to convert ZX-Paintbrush (.zxp) sprite files into Boriel Basic `DIM` array declarations.

## Features

- Converts ZX-Paintbrush bitmap data to Boriel Basic arrays
- Exports tile attributes (colors) automatically
- Generates individual arrays for each sprite/tile
- Supports sprites of any size (must be multiple of 8)
- Optional attribute export control

## Installation

```bash
pip install zxp2boriel
```

## Usage

```bash
zxp2boriel --input <file.zxp> --width <pixels> --rows <rows> --cols <cols> --output <file.bas> --name <array_name> [--no-attributes]
```

### Arguments

- `--input`, `-i`: Input .zxp file path.
- `--width`, `-w`: Tile width in pixels (must be a multiple of 8).
- `--rows`, `-r`: Number of rows in the sprite sheet.
- `--cols`, `-c`: Number of columns in the sprite sheet.
- `--output`, `-o`: Output .bas file path.
- `--name`, `-n`: Name prefix for the generated array variables.
- `--no-attributes`: (Optional) Skip exporting attribute arrays.

### Example

Convert an 8x8 tileset with 1 row and 6 columns:

```bash
zxp2boriel -i tileset.zxp -w 8 -r 1 -c 6 -o tileset.bas -n tile
```

This will generate a `tileset.bas` file containing individual arrays for each tile:

```basic
Dim tile0(7) As Ubyte => { _
	$00,$7E,$42,$5A,$00,$FF,$81,$81 _
}
Dim tileAttr0(0) As Ubyte => { $22 }

Dim tile1(7) As Ubyte => { _
	$00,$00,$00,$00,$00,$00,$00,$00 _
}
Dim tileAttr1(0) As Ubyte => { $22 }

...
```

### Output Format

- **Sprite Data**: Each sprite is exported as `{name}{index}` (e.g., `tile0`, `tile1`)
- **Attributes**: Each sprite's attributes are exported as `{name}Attr{index}` (e.g., `tileAttr0`)
- Attributes are formatted in a single line for better readability
- Each sprite and its attributes are grouped together, separated from the next sprite by a blank line

### Skipping Attributes

If you don't need color attributes:

```bash
zxp2boriel -i sprites.zxp -w 24 -r 2 -c 6 -o sprites.bas -n sprite --no-attributes
```

## License

AGPL-v3

