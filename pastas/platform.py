# utils/platform.py
"""Utilitários para detectar plataforma e ajustar layout."""
import sys
import flet as ft


def is_mobile() -> bool:
    """Verifica se está rodando em dispositivo móvel (via sys.platform)."""
    return sys.platform in ['android', 'ios']


def is_desktop() -> bool:
    """Verifica se está rodando em desktop."""
    return sys.platform in ['win32', 'darwin', 'linux']


def get_tela_tipo(page: ft.Page) -> str:
    """Retorna o tipo de tela baseado na largura atual.

    Esta é a forma mais confiável, pois funciona mesmo quando
    o Python roda no PC mas a tela é renderizada no celular (QR code).

    Returns:
        'mobile' (< 600px)
        'tablet' (600-1000px)
        'desktop' (> 1000px)
    """
    try:
        # Tenta pegar a largura da página
        width = page.width
        if width is None or width == 0:
            width = 1200  # Fallback
    except:
        width = 1200

    if width < 600:
        return "mobile"
    elif width < 1000:
        return "tablet"
    else:
        return "desktop"


def get_tamanhos_fonte(tipo_tela: str) -> dict:
    """Retorna tamanhos de fonte adaptados ao tipo de tela."""
    if tipo_tela == "mobile":
        return {
            "titulo_grande": 20,
            "titulo_medio": 16,
            "titulo_pequeno": 14,
            "texto": 13,
            "texto_pequeno": 11,
            "card_valor": 18,
            "card_titulo": 12,
        }
    elif tipo_tela == "tablet":
        return {
            "titulo_grande": 21,
            "titulo_medio": 17,
            "titulo_pequeno": 15,
            "texto": 13,
            "texto_pequeno": 11,
            "card_valor": 20,
            "card_titulo": 12,
        }
    else:
        return {
            "titulo_grande": 22,
            "titulo_medio": 18,
            "titulo_pequeno": 16,
            "texto": 14,
            "texto_pequeno": 12,
            "card_valor": 22,
            "card_titulo": 13,
        }