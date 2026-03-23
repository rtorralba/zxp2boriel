import io
from types import SimpleNamespace
from tile_exporter import TileExporter


def test_write_matrix_single_tile():
    f = io.StringIO()
    args = SimpleNamespace(name='T', rows=1, cols=1, width=8, no_attributes=False)
    total_bytes = 8
    attr_bytes = 1
    image_width_px = 8
    attributes = [0x12]
    sprite_lines = []
    total_sprites = 1

    exporter = TileExporter(f, args, total_bytes, attr_bytes, image_width_px, attributes, sprite_lines, total_sprites)

    # one tile with incremental byte values
    flat_tiles = [[i for i in range(total_bytes)]]
    flat_attrs = [[0x12]]

    exporter.write_matrix()
    out = f.getvalue()

    assert "Dim TTiles(0,7) As Ubyte" in out
    # hex for 0 should appear
    assert "$00" in out
    # attribute inline value present
    assert "$12" in out


def test_write_flat_single_sprite():
    f = io.StringIO()
    args = SimpleNamespace(name='S', rows=1, cols=1, width=8, no_attributes=False)
    total_bytes = 8
    attr_bytes = 1
    image_width_px = 8
    # attributes list must have at least one entry
    attributes = [0x12]
    # create 8 lines of 8 pixels (leftmost set)
    sprite_lines = ["10000000" for _ in range(8)]
    total_sprites = 1

    exporter = TileExporter(f, args, total_bytes, attr_bytes, image_width_px, attributes, sprite_lines, total_sprites)

    exporter.write_flat()
    out = f.getvalue()

    assert "Dim S0(7)" in out
    # expect some byte formatted (leading bit set -> $80)
    assert "$80" in out
    # attribute for the sprite should be present
    assert "$12" in out
