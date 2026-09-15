# converter_icone.py
from PIL import Image

# Abre o PNG (crie um icon.png 512x512 na pasta assets/)
img = Image.open('assets/icon.png')

# Converte para ICO com vários tamanhos
img.save('assets/icon.ico', format='ICO', sizes=[
    (16, 16), (32, 32), (48, 48),
    (64, 64), (128, 128), (256, 256)
])
print("✅ Ícone criado: assets/icon.ico")