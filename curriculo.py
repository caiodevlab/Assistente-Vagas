"""
Modulo de perfil do curriculo.
Gerencia as habilidades, palavras-chave e experiencia do usuario.
"""

from dataclasses import dataclass, field

import json


# ── Perfil padrao (exemplo para estudante de Desenvolvimento de Sistemas) ──

PERFIL_PADRAO = {
    "nome": "Estudante de Desenvolvimento de Sistemas",
    "resumo": (
        "Estudante de Desenvolvimento de Sistemas com interesse em "
        "desenvolvimento web, banco de dados e suporte tecnico."
    ),
    "habilidades": [
        "python", "javascript", "html", "css",
        "sql", "mysql", "git", "github",
        "logica de programacao", "poo",
        "suporte tecnico", "redes", "linux",
        "excel", "pacote office",
    ],
    "nivel": "estagiario",
    "area_interesse": "TI",
}


@dataclass
class Curriculo:
    """Representa o curriculo/perfil do candidato."""

    nome: str = ""
    resumo: str = ""
    habilidades: list[str] = field(default_factory=list)
    nivel: str = ""
    area_interesse: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "Curriculo":
        """Cria Curriculo a partir de um dicionario."""
        return cls(
            nome=data.get("nome", ""),
            resumo=data.get("resumo", ""),
            habilidades=", ".join(data.get("habilidades", [])).split(", ")
            if isinstance(data.get("habilidades"), list)
            else data.get("habilidades", "").split(", "),
            nivel=data.get("nivel", ""),
            area_interesse=data.get("area_interesse", ""),
        )

    @classmethod
    def padrao(cls) -> "Curriculo":
        """Retorna o perfil padrao de estudante."""
        return cls.from_dict(PERFIL_PADRAO)

    @classmethod
    def carregar(cls, caminho: str = "curriculo.json") -> "Curriculo":
        """Carrega curriculo de arquivo JSON."""
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls.from_dict(data)
        except FileNotFoundError:
            print(f"[INFO] Arquivo '{caminho}' nao encontrado. Usando perfil padrao.")
            return cls.padrao()
        except (json.JSONDecodeError, KeyError) as exc:
            print(f"[AVISO] Erro ao ler '{caminho}': {exc}. Usando perfil padrao.")
            return cls.padrao()

    def salvar(self, caminho: str = "curriculo.json") -> None:
        """Salva curriculo em arquivo JSON."""
        data = {
            "nome": self.nome,
            "resumo": self.resumo,
            "habilidades": self.habilidades,
            "nivel": self.nivel,
            "area_interesse": self.area_interesse,
        }
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[OK] Curriculo salvo em: {caminho}")

    @property
    def keywords(self) -> list[str]:
        """Retorna todas as palavras-chave em lowercase."""
        palavras = set()
        for hab in self.habilidades:
            palavras.add(hab.strip().lower())
            # Adiciona tokens individuais (ex: "logica de programacao")
            for token in hab.strip().lower().split():
                if len(token) > 2:
                    palavras.add(token)
        return sorted(palavras)

    def __str__(self) -> str:
        linhas = [
            f"Nome: {self.nome}",
            f"Nivel: {self.nivel}",
            f"Area: {self.area_interesse}",
            f"Habilidades: {', '.join(self.habilidades)}",
        ]
        return "\n".join(linhas)
