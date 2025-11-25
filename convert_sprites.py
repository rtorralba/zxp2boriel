#!/usr/bin/env python3
"""
Convierte sprites de ZX-Paintbrush (.zxp) a formato ZX BASIC para putChars
Los sprites están en formato bitmap (0=papel, 1=tinta) de 24x24 pixels
"""

def read_zxp_file(filename):
    """Lee el archivo .zxp y extrae las líneas de sprites"""
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # Saltar las primeras 2 líneas (cabecera)
    sprite_lines = [line.strip() for line in lines[2:] if line.strip() and not line.startswith('0F') and not line.startswith('47')]
    return sprite_lines

def extract_sprite(lines, row, col):
    """
    Extrae un sprite de 24x24 de la posición especificada
    row: 0=arriba (derecha), 1=abajo (izquierda)
    col: 0-5 (6 sprites por fila)
    """
    sprite = []
    start_col = col * 24
    start_row = row * 24
    
    for y in range(24):
        if start_row + y < len(lines):
            line = lines[start_row + y]
            # Asegurarse de que la línea sea lo suficientemente larga
            if start_col + 24 <= len(line):
                sprite_row = line[start_col:start_col + 24]
                sprite.append(sprite_row)
            else:
                sprite.append("0" * 24)
        else:
            sprite.append("0" * 24)
    
    return sprite

def bitmap_to_bytes(sprite):
    """
    Convierte un sprite bitmap 24x24 a bytes en formato interleaved para putChars (3x3 chars)
    Total: 72 bytes
    """
    bytes_data = []
    
    # Recorrer las 3 columnas de caracteres (0, 1, 2)
    for col_block in range(3):
        # Recorrer las 3 filas de caracteres (0, 1, 2)
        for row_block in range(3):
            # Recorrer las 8 líneas de cada carácter
            for y_offset in range(8):
                byte_val = 0
                y = row_block * 8 + y_offset
                
                # Recorrer los 8 pixels de cada byte
                for x_offset in range(8):
                    x = col_block * 8 + x_offset
                    
                    if y < len(sprite) and x < len(sprite[y]):
                        if sprite[y][x] == '1':
                            byte_val |= (1 << (7 - x_offset))
                            
                bytes_data.append(byte_val)
    
    return bytes_data

def format_bytes(bytes_data):
    """Formatea los bytes en cadenas hexadecimales para ZX BASIC"""
    hex_strings = ['$' + format(b, '02X') for b in bytes_data]
    
    # Dividir en líneas de 8 bytes
    lines = []
    for i in range(0, len(hex_strings), 8):
        line = ','.join(hex_strings[i:i+8])
        # Añadir coma al final excepto en la última línea
        if i + 8 < len(hex_strings):
            line += ','
        lines.append(line)
    
    return ' _\n\t\t'.join(lines)

def generate_sprites_bas(zxp_file, output_file):
    """Genera el archivo sprites.bas completo"""
    lines = read_zxp_file(zxp_file)
    
    # Extraer sprites
    # Fila 0 (derecha): 4 walking + 2 standing
    walk_right = []
    for i in range(4):
        sprite = extract_sprite(lines, 0, i)
        bytes_data = bitmap_to_bytes(sprite)
        walk_right.append(format_bytes(bytes_data))
    
    stand_right = []
    for i in range(4, 6):
        sprite = extract_sprite(lines, 0, i)
        bytes_data = bitmap_to_bytes(sprite)
        stand_right.append(format_bytes(bytes_data))
    
    # Fila 1 (izquierda): 4 walking + 2 standing
    walk_left = []
    for i in range(4):
        sprite = extract_sprite(lines, 1, i)
        bytes_data = bitmap_to_bytes(sprite)
        walk_left.append(format_bytes(bytes_data))
    
    stand_left = []
    for i in range(4, 6):
        sprite = extract_sprite(lines, 1, i)
        bytes_data = bitmap_to_bytes(sprite)
        stand_left.append(format_bytes(bytes_data))

    # Jump Right (2 frames) - Row 0, cols 6-7
    jump_right = []
    for i in range(6, 8):
        sprite = extract_sprite(lines, 0, i)
        bytes_data = bitmap_to_bytes(sprite)
        jump_right.append(format_bytes(bytes_data))

    # Jump Left (2 frames) - Row 1, cols 6-7
    jump_left = []
    for i in range(6, 8):
        sprite = extract_sprite(lines, 1, i)
        bytes_data = bitmap_to_bytes(sprite)
        jump_left.append(format_bytes(bytes_data))
    
    # Generar archivo .bas
    with open(output_file, 'w') as f:
        # standRight (2 frames)
        f.write('DIM standRight(1,71) AS UByte => { _\n')
        for i, sprite in enumerate(stand_right):
            f.write('\t{ _\n')
            f.write(f'\t\t{sprite} _\n')
            f.write('\t}')
            if i < len(stand_right) - 1:
                f.write(', _\n')
            else:
                f.write(' _\n')
        f.write('}\n')
        
        # standLeft (2 frames)
        f.write('DIM standLeft(1,71) AS UByte => { _\n')
        for i, sprite in enumerate(stand_left):
            f.write('\t{ _\n')
            f.write(f'\t\t{sprite} _\n')
            f.write('\t}')
            if i < len(stand_left) - 1:
                f.write(', _\n')
            else:
                f.write(' _\n')
        f.write('}\n')
        
        # walkRight (4 frames)
        f.write('DIM walkRight(3,71) AS UByte => { _\n')
        for i, sprite in enumerate(walk_right):
            f.write('\t{ _\n')
            f.write(f'\t\t{sprite} _\n')
            f.write('\t}')
            if i < len(walk_right) - 1:
                f.write(', _\n')
            else:
                f.write(' _\n')
        f.write('}\n')
        
        # walkLeft (4 frames)
        f.write('DIM walkLeft(3,71) AS UByte => { _\n')
        for i, sprite in enumerate(walk_left):
            f.write('\t{ _\n')
            f.write(f'\t\t{sprite} _\n')
            f.write('\t}')
            if i < len(walk_left) - 1:
                f.write(', _\n')
            else:
                f.write(' _\n')
        f.write('}\n')
        
        # jumpRight (2 frames)
        f.write('DIM jumpRight(1,71) AS UByte => { _\n')
        for i, sprite in enumerate(jump_right):
            f.write('\t{ _\n')
            f.write(f'\t\t{sprite} _\n')
            f.write('\t}')
            if i < len(jump_right) - 1:
                f.write(', _\n')
            else:
                f.write(' _\n')
        f.write('}\n')

        # jumpLeft (2 frames)
        f.write('DIM jumpLeft(1,71) AS UByte => { _\n')
        for i, sprite in enumerate(jump_left):
            f.write('\t{ _\n')
            f.write(f'\t\t{sprite} _\n')
            f.write('\t}')
            if i < len(jump_left) - 1:
                f.write(', _\n')
            else:
                f.write(' _\n')
        f.write('}\n')
        

        
        # Empty sprite para borrado (3x3 chars = 72 bytes)
        f.write('DIM empty(71) AS UByte => { _\n')
        empty_bytes = [0] * 72
        formatted_zeros = format_bytes(empty_bytes)
        f.write(f'\t\t{formatted_zeros} _\n')
        f.write('}\n')

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) != 3:
        print("Uso: python convert_sprites.py <archivo.zxp> <sprites.bas>")
        sys.exit(1)
    
    zxp_file = sys.argv[1]
    output_file = sys.argv[2]
    
    generate_sprites_bas(zxp_file, output_file)
    print(f"Sprites generados en {output_file}")
