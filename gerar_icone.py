# gerar_icone_bonito.py
"""Gera um ícone profissional com gradiente."""
from PIL import Image, ImageDraw, ImageFont
import os
import math


def gerar_icone_bonito():
    """Cria um ícone com gradiente e símbolo financeiro."""

    tamanho = 512
    img = Image.new('RGBA', (tamanho, tamanho), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Gradiente de verde (do mais claro ao mais escuro)
    for y in range(tamanho):
        # Calcula a cor do gradiente
        ratio = y / tamanho
        r = int(46 + (76 - 46) * ratio)
        g = int(125 + (175 - 125) * ratio)
        b = int(91 + (80 - 91) * ratio)

        # Desenha linha horizontal
        draw.line([(0, y), (tamanho, y)], fill=(r, g, b, 255))

    # Aplica máscara circular
    mask = Image.new('L', (tamanho, tamanho), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse([0, 0, tamanho - 1, tamanho - 1], fill=255)

    # Aplica a máscara
    img.putalpha(mask)

    # Adiciona borda branca sutil
    draw = ImageDraw.Draw(img)
    draw.ellipse([2, 2, tamanho - 3, tamanho - 3], outline=(255, 255, 255, 100), width=4)

    # Desenha símbolo "$" branco
    try:
        font = ImageFont.truetype("arial.ttf", 320)
    except:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 320)
        except:
            font = ImageFont.load_default()

    texto = "$"
    bbox = draw.textbbox((0, 0), texto, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (tamanho - text_width) / 2
    y = (tamanho - text_height) / 2 - bbox[1]

    # Sombra do texto
    draw.text((x + 3, y + 3), texto, fill=(0, 0, 0, 80), font=font)
    # Texto principal
    draw.text((x, y), texto, fill=(255, 255, 255), font=font)

    # Salva
    os.makedirs('assets', exist_ok=True)
    img.save('assets/icon.png')
    img.save('assets/icon.ico', format='ICO', sizes=[
        (16, 16), (32, 32), (48, 48),
        (64, 64), (128, 128), (256, 256)
    ])
    print("✅ Ícone profissional criado!")


if __name__ == "__main__":
    gerar_icone_bonito()