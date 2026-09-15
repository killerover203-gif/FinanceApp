# services/tema_service.py
"""Gerencia as preferências de tema do usuário."""
import json
from pathlib import Path
from config.temas import TEMAS, TEMA_PADRAO

ARQUIVO_PREFERENCIAS = Path("data/preferencias.json")


class TemaService:
    def __init__(self):
        self.preferencias = self._carregar_preferencias()

    def _carregar_preferencias(self) -> dict:
        """Carrega as preferências do arquivo JSON."""
        if ARQUIVO_PREFERENCIAS.exists():
            try:
                with open(ARQUIVO_PREFERENCIAS, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {"tema": TEMA_PADRAO}
        return {"tema": TEMA_PADRAO}

    def _salvar_preferencias(self):
        """Salva as preferências no arquivo JSON."""
        ARQUIVO_PREFERENCIAS.parent.mkdir(parents=True, exist_ok=True)
        with open(ARQUIVO_PREFERENCIAS, "w", encoding="utf-8") as f:
            json.dump(self.preferencias, f, indent=2)

    def obter_tema_atual(self) -> str:
        """Retorna o ID do tema atual."""
        return self.preferencias.get("tema", TEMA_PADRAO)

    def definir_tema(self, tema_id: str):
        """Define um novo tema e salva a preferência."""
        if tema_id in TEMAS:
            self.preferencias["tema"] = tema_id
            self._salvar_preferencias()

    def obter_paleta_atual(self, modo_escuro: bool) -> dict:
        """Retorna a paleta de cores do tema atual conforme o modo."""
        tema_id = self.obter_tema_atual()
        tema = TEMAS.get(tema_id, TEMAS[TEMA_PADRAO])
        return tema["escuro"] if modo_escuro else tema["claro"]

    def obter_seed_tema(self) -> str:
        """Retorna o seed do tema atual (para o tema do Flet)."""
        tema_id = self.obter_tema_atual()
        return TEMAS.get(tema_id, TEMAS[TEMA_PADRAO])["seed"]

    def listar_temas(self) -> list[dict]:
        """Lista todos os temas disponíveis com suas informações."""
        return [
            {
                "id": tema_id,
                "nome": tema["nome"],
                "descricao": tema["descricao"],
                "preview_cores": tema["claro"]["preview_cores"],
            }
            for tema_id, tema in TEMAS.items()
        ]