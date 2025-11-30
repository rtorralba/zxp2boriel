#!/usr/bin/env python3
"""
Generic ZXP to Boriel Basic Converter
Converts ZXP bitmap data to Boriel Basic DIM declarations.
"""

import argparse
import sys
import os

def read_zxp_file(filename):
    """Reads the .zxp file and extracts sprite lines and attribute lines."""
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
        
        sprite_lines = []
        attribute_lines = []
        parsing_attributes = False
        
        # Skip header (first 2 lines usually)
        # We start looking from line 2
        for line in lines[2:]:
            stripped = line.strip()
            if not stripped:
                # Empty line usually signals start of attributes if we have processed sprites
                if sprite_lines:
                    parsing_attributes = True
                continue
            
            if parsing_attributes:
                attribute_lines.append(stripped)
            else:
                # Filter for bitmap data (0s and 1s)
                # Some ZXP files might have other metadata, so we ensure it looks like bitmap
                if all(c in '01' for c in stripped):
                    sprite_lines.append(stripped)
                elif ' ' in stripped and all(c in '0123456789ABCDEFabcdef ' for c in stripped):
                     # Fallback: if we missed the blank line but see hex values
                     parsing_attributes = True
                     attribute_lines.append(stripped)

        return sprite_lines, attribute_lines
    except Exception as e:
        print(f"Error reading file {filename}: {e}")
        sys.exit(1)

def extract_sprite(lines, row, col, width):
    """
    Extracts a sprite of size width x width from the grid.
    row: grid row index
    col: grid col index
    width: width/height of the sprite in pixels
    """
    sprite = []
    start_col = col * width
    start_row = row * width
    
    for y in range(width):
        if start_row + y < len(lines):
            line = lines[start_row + y]
            # Ensure line is long enough
            if start_col + width <= len(line):
                sprite_row = line[start_col:start_col + width]
                sprite.append(sprite_row)
            else:
                sprite.append("0" * width)
        else:
            sprite.append("0" * width)
    
    return sprite

def parse_attributes(attribute_lines):
    """Parses attribute lines into a single list of integer values."""
    attributes = []
    for line in attribute_lines:
        parts = line.split()
        for part in parts:
            try:
                attributes.append(int(part, 16))
            except ValueError:
                pass
    return attributes

def extract_sprite_attributes(attributes, row, col, sprite_width, total_cols_px):
    """
    Extracts attributes for a specific sprite.
    attributes: flat list of all attribute values (row-major 8x8 blocks)
    row: sprite grid row index
    col: sprite grid col index
    sprite_width: width of sprite in pixels
    total_cols_px: total width of the image in pixels (inferred)
    """
    attr_data = []
    
    # Dimensions in 8x8 blocks
    sprite_blocks = sprite_width // 8
    total_blocks_width = total_cols_px // 8
    
    start_block_col = col * sprite_blocks
    start_block_row = row * sprite_blocks
    
    for r in range(sprite_blocks):
        for c in range(sprite_blocks):
            # Calculate index in the flat attributes list
            # The attributes are stored row by row of blocks
            block_index = (start_block_row + r) * total_blocks_width + (start_block_col + c)
            
            if block_index < len(attributes):
                attr_data.append(attributes[block_index])
            else:
                attr_data.append(0)
                
    return attr_data

def bitmap_to_bytes(sprite, width):
    """
    Converts a bitmap sprite to bytes in interleaved format for putChars.
    Assumes width is a multiple of 8.
    """
    bytes_data = []
    
    chars_per_row = width // 8
    chars_per_col = width // 8 # Square tiles
    
    # Iterate through character blocks (columns then rows)
    # Note: The original script iterated col_block then row_block.
    # We will stick to that order as it seems standard for this putChars routine.
    
    for col_block in range(chars_per_col):
        for row_block in range(chars_per_row):
            # 8 lines per character
            for y_offset in range(8):
                byte_val = 0
                y = row_block * 8 + y_offset
                
                # 8 pixels per byte
                for x_offset in range(8):
                    x = col_block * 8 + x_offset
                    
                    if y < len(sprite) and x < len(sprite[y]):
                        if sprite[y][x] == '1':
                            byte_val |= (1 << (7 - x_offset))
                            
                bytes_data.append(byte_val)
    
    return bytes_data

def format_bytes(bytes_data):
    """Formats bytes into hex strings for ZX BASIC."""
    hex_strings = ['$' + format(b, '02X') for b in bytes_data]
    
    # Split into lines of 8 bytes for readability
    lines = []
    for i in range(0, len(hex_strings), 8):
        line = ','.join(hex_strings[i:i+8])
        if i + 8 < len(hex_strings):
            line += ','
        lines.append(line)
    
    return ' _\n\t\t'.join(lines)

def main():
    parser = argparse.ArgumentParser(description='Convert ZXP sprites to Boriel Basic.')
    parser.add_argument('--input', '-i', required=True, help='Input .zxp file')
    parser.add_argument('--width', '-w', type=int, required=True, help='Tile width (pixels)')
    parser.add_argument('--rows', '-r', type=int, required=True, help='Number of rows')
    parser.add_argument('--cols', '-c', type=int, required=True, help='Number of columns')
    parser.add_argument('--output', '-o', required=True, help='Output .bas file')
    parser.add_argument('--name', '-n', required=True, help='Variable name prefix')
    parser.add_argument('--no-attributes', action='store_true', help='Do not export attributes')
    
    args = parser.parse_args()
    
    if args.width % 8 != 0:
        print("Error: Width must be a multiple of 8.")
        sys.exit(1)
        
    sprite_lines, attribute_lines = read_zxp_file(args.input)
    attributes = parse_attributes(attribute_lines)
    
    # Calculate total size of one sprite in bytes
    total_bytes = (args.width // 8) * (args.width // 8) * 8
    # Array size is total_bytes - 1 (0-indexed)
    
    total_sprites = args.rows * args.cols
    
    # Infer total image width in pixels to help with attribute extraction
    # We assume the input rows/cols describe the layout in the file
    # But wait, args.rows and args.cols are usually passed by the user to define how many sprites to extract
    # However, to correctly extract attributes from the linear list, we need to know the 'stride' of the original image.
    # Usually ZXP exports the whole image width.
    # Let's try to infer it from the length of the first sprite line.
    
    if sprite_lines:
        image_width_px = len(sprite_lines[0])
    else:
        image_width_px = args.cols * args.width # Fallback
        
    
    with open(args.output, 'w') as f:
        f.write(f"' Generated by zxp2boriel.py\n")
        f.write(f"' Source: {os.path.basename(args.input)}\n")
        f.write(f"' Size: {args.width}x{args.width}\n")
        f.write(f"' Count: {total_sprites}\n\n")
        
        # 1. Write Sprite Data
        f.write(f"Dim {args.name}({total_sprites - 1}, {total_bytes - 1}) As Ubyte => {{ _\n")
        
        count = 0
        for r in range(args.rows):
            for c in range(args.cols):
                sprite = extract_sprite(sprite_lines, r, c, args.width)
                bytes_data = bitmap_to_bytes(sprite, args.width)
                formatted_data = format_bytes(bytes_data)
                
                f.write(f"\t{{ _\n")
                f.write(f"\t\t{formatted_data} _\n")
                
                if count < total_sprites - 1:
                    f.write(f"\t}}, _\n")
                else:
                    f.write(f"\t}} _\n")
                
                count += 1
        
        f.write(f"}}\n\n")
        
        # 2. Write Attribute Data
        # Size of attributes per sprite = (W/8) * (W/8) bytes
        attr_bytes_per_sprite = (args.width // 8) * (args.width // 8)
        
        if attributes and not args.no_attributes:
            f.write(f"Dim {args.name}_attr({total_sprites - 1}, {attr_bytes_per_sprite - 1}) As Ubyte => {{ _\n")
            
            count = 0
            for r in range(args.rows):
                for c in range(args.cols):
                    attr_data = extract_sprite_attributes(attributes, r, c, args.width, image_width_px)
                    formatted_attr = format_bytes(attr_data)
                    
                    f.write(f"\t{{ _\n")
                    f.write(f"\t\t{formatted_attr} _\n")
                    
                    if count < total_sprites - 1:
                        f.write(f"\t}}, _\n")
                    else:
                        f.write(f"\t}} _\n")
                    
                    count += 1
            
            f.write(f"}}\n")
        elif not args.no_attributes:
            f.write(f"' No attributes found in source file\n")
                
    print(f"Successfully generated {count} sprites in {args.output}")

if __name__ == '__main__':
    main()
