class TileExporter:
    def __init__(self, f, args, total_bytes, attr_bytes_per_sprite, image_width_px, attributes, sprite_lines, total_sprites):
        self.f = f
        self.args = args
        self.total_bytes = total_bytes
        self.attr_bytes_per_sprite = attr_bytes_per_sprite
        self.image_width_px = image_width_px
        self.attributes = attributes
        self.sprite_lines = sprite_lines
        self.total_sprites = total_sprites
        # helper methods are implemented on the class

    def write_matrix(self):
        f = self.f
        args = self.args
        total_bytes = self.total_bytes
        attr_bytes_per_sprite = self.attr_bytes_per_sprite
        attributes = self.attributes
        total_sprites = self.total_sprites

        # Build flat tile list from sprite grid
        flat_tiles = []
        for r in range(args.rows):
            for c in range(args.cols):
                sprite = self._extract_sprite(self.sprite_lines, r, c, args.width)
                bytes_data = self._bitmap_to_bytes(sprite, args.width)
                flat_tiles.append(bytes_data)

        # Build flat attributes list if present
        flat_attrs = None
        if attributes and not args.no_attributes:
            flat_attrs = []
            for r in range(args.rows):
                for c in range(args.cols):
                    attr_data = self._extract_sprite_attributes(attributes, r, c, args.width, self.image_width_px)
                    flat_attrs.append(attr_data)

        f.write(f"' Tiles matrix: {total_sprites} x {total_bytes}\n")
        f.write(f"Dim {args.name}Tiles({total_sprites - 1},{total_bytes - 1}) As Ubyte => {{ _\n")

        for idx, tile_bytes in enumerate(flat_tiles):
            formatted = self._format_bytes(tile_bytes).replace('\n\t', '\n\t\t')
            f.write('\t{ _\n\t\t')
            f.write(formatted)
            f.write(' _\n\t}')
            if idx < len(flat_tiles) - 1:
                f.write(', _\n')
            else:
                f.write(' _\n')

        f.write('}\n\n')

        if flat_attrs is not None:
            f.write(f"' Attributes matrix: {total_sprites} x {attr_bytes_per_sprite}\n")
            f.write(f"Dim {args.name}Attr({total_sprites - 1},{attr_bytes_per_sprite - 1}) As Ubyte => {{ _\n")

            for idx, attr_bytes in enumerate(flat_attrs):
                inline = self._format_bytes_inline(attr_bytes)
                f.write(f'\t{{ {inline} }}')
                if idx < len(flat_attrs) - 1:
                    f.write(', _\n')
                else:
                    f.write(' _\n')

            f.write('}\n\n')

    # --- Private helper methods (moved from zxp2boriel) ---
    def _extract_sprite(self, lines, row, col, width):
        sprite = []
        start_col = col * width
        start_row = row * width
        for y in range(width):
            if start_row + y < len(lines):
                line = lines[start_row + y]
                if start_col + width <= len(line):
                    sprite_row = line[start_col:start_col + width]
                    sprite.append(sprite_row)
                else:
                    sprite.append("0" * width)
            else:
                sprite.append("0" * width)
        return sprite

    def _extract_sprite_attributes(self, attributes, row, col, sprite_width, total_cols_px):
        attr_data = []
        sprite_blocks = sprite_width // 8
        total_blocks_width = total_cols_px // 8
        start_block_col = col * sprite_blocks
        start_block_row = row * sprite_blocks
        for r in range(sprite_blocks):
            for c in range(sprite_blocks):
                block_index = (start_block_row + r) * total_blocks_width + (start_block_col + c)
                if block_index < len(attributes):
                    attr_data.append(attributes[block_index])
                else:
                    attr_data.append(0)
        return attr_data

    def _bitmap_to_bytes(self, sprite, width):
        bytes_data = []
        chars_per_row = width // 8
        chars_per_col = width // 8
        for col_block in range(chars_per_col):
            for row_block in range(chars_per_row):
                for y_offset in range(8):
                    byte_val = 0
                    y = row_block * 8 + y_offset
                    for x_offset in range(8):
                        x = col_block * 8 + x_offset
                        if y < len(sprite) and x < len(sprite[y]):
                            if sprite[y][x] == '1':
                                byte_val |= (1 << (7 - x_offset))
                    bytes_data.append(byte_val)
        return bytes_data

    def _format_bytes(self, bytes_data):
        hex_strings = ['$' + format(b, '02X') for b in bytes_data]
        lines = []
        for i in range(0, len(hex_strings), 8):
            line = ','.join(hex_strings[i:i+8])
            if i + 8 < len(hex_strings):
                line += ','
            lines.append(line)
        return ' _\n\t'.join(lines)

    def _format_bytes_inline(self, bytes_data):
        hex_strings = ['$' + format(b, '02X') for b in bytes_data]
        return ','.join(hex_strings)

    def write_flat(self):
        f = self.f
        args = self.args
        total_bytes = self.total_bytes
        attr_bytes_per_sprite = self.attr_bytes_per_sprite
        image_width_px = self.image_width_px
        attributes = self.attributes
        sprite_lines = self.sprite_lines

        count = 0
        for r in range(args.rows):
            for c in range(args.cols):
                sprite = self._extract_sprite(sprite_lines, r, c, args.width)
                bytes_data = self._bitmap_to_bytes(sprite, args.width)
                formatted_data = self._format_bytes(bytes_data)

                f.write(f"Dim {args.name}{count}({total_bytes - 1}) As Ubyte => {{ _\n")
                f.write(f"\t{formatted_data} _\n")
                f.write(f"}}\n")

                if attributes and not args.no_attributes:
                    attr_data = self._extract_sprite_attributes(attributes, r, c, args.width, image_width_px)
                    formatted_attr = self._format_bytes_inline(attr_data)
                    f.write(f"Dim {args.name}Attr{count}({attr_bytes_per_sprite - 1}) As Ubyte => {{ {formatted_attr} }}\n")

                f.write(f"\n")
                count += 1
