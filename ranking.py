"""
Modulo de ranking de compatibilidade.
Calcula o grau de compatibilidade entre o curriculo e cada vaga.

Algoritmo:
  - Match exato (palavra inteira): +3 pontos
  - Match parcial (substring): +1 ponto
  - Match de nivel compativel: +2 pontos
  - Match de area de interesse: +2 pontos
  - Bonus por diversidade de matches: ate +3 pontos
"""

from dataclasses import dataclass

from curriculo import Curriculo


# ── Pesos ────────────────────────────────────────────────────────────────────

PESO_EXATO = 3
PESO_PARCIAL = 1
PESO_NIVEL = 2
PESO_AREA = 2
BONUS_DIVERSIDADE = 3  # bonus maximo por ter muitos matches diferentes

# Niveis aceitaveis por perfil
NIVEIS_COMPATIVEIS = {
    "estagiario": ["estagio", "estagiario", "estagiaria", "trainee", "aprendiz", "jovem aprendiz"],
    "junior": ["junior", "jr", "estagio", "estagiario", "trainee", "aprendiz"],
    "pleno": ["pleno", "pl", "junior", "jr"],
    "senior": ["senior", "sr", "pleno", "pl"],
}

# Palavras muito curtas/genericas que nao devem contar como match parcial
STOPWORDS = {"ti", "em", "de", "da", "do", "na", "no", "ao", "os", "as", "um", "uma"}


@dataclass
class ResultadoRanking:
    """Resultado da analise de compatibilidade de uma vaga."""

    titulo: str
    empresa: str
    localizacao: str
    link: str
    fonte: str
    score: int
    matches: list[str]
    nivel: str

    @property
    def compatibilidade(self) -> str:
        """Retorna faixa de compatibilidade em texto."""
        if self.score >= 10:
            return "ALTA"
        if self.score >= 6:
            return "MEDIA"
        if self.score >= 3:
            return "BAIXA"
        return "MINIMA"

    @property
    def barra_visual(self) -> str:
        """Retorna barra visual de compatibilidade (0-10)."""
        nivel = min(self.score, 10)
        cheio = "█" * nivel
        vazio = "░" * (10 - nivel)
        return f"[{cheio}{vazio}]"

    @property
    def estrelas(self) -> str:
        """Retorna avaliacao em estrelas."""
        if self.score >= 10:
            return "★★★★★"
        if self.score >= 7:
            return "★★★★☆"
        if self.score >= 5:
            return "★★★☆☆"
        if self.score >= 3:
            return "★★☆☆☆"
        return "★☆☆☆☆"


def _normalizar(texto: str) -> str:
    """Normaliza texto para comparacao: lowercase, sem acentos comuns."""
    texto = texto.lower().strip()
    substituicoes = {
        "á": "a", "à": "a", "â": "a", "ã": "a",
        "é": "e", "ê": "e",
        "í": "i",
        "ó": "o", "ô": "o", "õ": "o",
        "ú": "u",
        "ç": "c",
    }
    for orig, repl in substituicoes.items():
        texto = texto.replace(orig, repl)
    return texto


def _match_exato(titulo_norm: str, keyword: str) -> bool:
    """Verifica se a keyword aparece como palavra inteira no titulo."""
    delimitadores = (" ", ",", ".", "/", "(", ")", "-", ":", ";", "|", "–")
    for d in delimitadores:
        for d2 in delimitadores:
            if f"{d}{keyword}{d2}" in titulo_norm:
                return True
    if titulo_norm.startswith(keyword + " ") or titulo_norm.startswith(keyword + "-"):
        return True
    if titulo_norm.endswith(" " + keyword) or titulo_norm.endswith("-" + keyword):
        return True
    if titulo_norm == keyword:
        return True
    return False


def _detectar_nivel(titulo_norm: str) -> str:
    """Detecta o nivel da vaga pelo titulo."""
    for nivel, termos in NIVEIS_COMPATIVEIS.items():
        for termo in termos:
            if termo in titulo_norm:
                return nivel
    return "nao_informado"


def calcular_compatibilidade(
    titulo_vaga: str,
    curriculo: Curriculo,
) -> ResultadoRanking:
    """
    Calcula a compatibilidade entre uma vaga e o curriculo.

    Retorna ResultadoRanking com score e palavras-chave encontradas.
    """
    titulo_norm = _normalizar(titulo_vaga)
    score = 0
    matches: list[str] = []

    # 1. Match de keywords do curriculo no titulo da vaga
    for keyword in curriculo.keywords:
        if len(keyword) <= 2 or keyword in STOPWORDS:
            continue

        if _match_exato(titulo_norm, keyword):
            score += PESO_EXATO
            if keyword not in matches:
                matches.append(keyword)
        elif keyword in titulo_norm:
            # Match parcial apenas para palavras com 4+ caracteres
            if len(keyword) >= 4:
                score += PESO_PARCIAL
                matches.append(f"{keyword}*")

    # 2. Match de nivel
    nivel_vaga = _detectar_nivel(titulo_norm)
    if curriculo.nivel and nivel_vaga != "nao_informado":
        niveis_aceitos = NIVEIS_COMPATIVEIS.get(curriculo.nivel, [])
        if nivel_vaga in niveis_aceitos or nivel_vaga == curriculo.nivel:
            score += PESO_NIVEL
            matches.append(f"nivel:{nivel_vaga}")

    # 3. Match de area
    if curriculo.area_interesse:
        area_norm = _normalizar(curriculo.area_interesse)
        if area_norm in titulo_norm:
            score += PESO_AREA
            matches.append(f"area:{curriculo.area_interesse}")

    # 4. Bonus por diversidade (multiplos matches diferentes)
    matches_exatos = [m for m in matches if not m.endswith("*") and ":" not in m]
    if len(matches_exatos) >= 3:
        score += BONUS_DIVERSIDADE
        matches.append(f"bonus:+{BONUS_DIVERSIDADE}")
    elif len(matches_exatos) >= 2:
        score += 1
        matches.append("bonus:+1")

    return ResultadoRanking(
        titulo=titulo_vaga,
        empresa="",
        localizacao="",
        link="",
        fonte="",
        score=score,
        matches=matches,
        nivel=nivel_vaga,
    )


def ranquear_vagas(
    vagas: list[dict],
    curriculo: Curriculo,
) -> list[ResultadoRanking]:
    """
    Recebe lista de dicts de vagas (do CSV) e retorna lista
    de ResultadoRanking ordenada por score (maior primeiro).
    """
    resultados: list[ResultadoRanking] = []

    for vaga in vagas:
        titulo = vaga.get("titulo", "")
        if not titulo:
            continue

        resultado = calcular_compatibilidade(titulo, curriculo)
        resultado.empresa = vaga.get("empresa", "Nao informado")
        resultado.localizacao = vaga.get("localizacao", "Nao informado")
        resultado.link = vaga.get("link", "")
        resultado.fonte = vaga.get("fonte", "")
        resultados.append(resultado)

    resultados.sort(key=lambda r: r.score, reverse=True)
    return resultados


def formatar_ranking(resultados: list[ResultadoRanking], top_n: int = 20) -> str:
    """Formata o ranking para exibicao no terminal."""
    if not resultados:
        return "Nenhuma vaga para ranquear."

    linhas = []
    linhas.append("")
    linhas.append("=" * 72)
    linhas.append("  RANKING DE COMPATIBILIDADE COM SEU CURRICULO")
    linhas.append("=" * 72)
    linhas.append(f"  {'#':<4} {'SCORE':<6} {'COMPAT.':<10} {'ESTRELAS':<10} {'TITULO'}")
    linhas.append("-" * 72)

    for i, r in enumerate(resultados[:top_n], 1):
        titulo_curto = r.titulo[:42] + "..." if len(r.titulo) > 42 else r.titulo
        linhas.append(
            f"  {i:<4} {r.score:<6} {r.compatibilidade:<10} {r.estrelas:<10} {titulo_curto}"
        )
        if r.matches:
            matches_str = ", ".join(r.matches[:8])
            linhas.append(f"       {r.barra_visual}  {matches_str}")

    linhas.append("-" * 72)
    linhas.append(f"  Total de vagas analisadas: {len(resultados)}")

    alta = sum(1 for r in resultados if r.compatibilidade == "ALTA")
    media = sum(1 for r in resultados if r.compatibilidade == "MEDIA")
    baixa = sum(1 for r in resultados if r.compatibilidade == "BAIXA")
    minima = sum(1 for r in resultados if r.compatibilidade == "MINIMA")

    linhas.append(f"  Alta: {alta} | Media: {media} | Baixa: {baixa} | Minima: {minima}")
    linhas.append("=" * 72)

    return "\n".join(linhas)
