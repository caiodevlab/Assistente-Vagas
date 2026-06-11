"""
Script de scraping de vagas de TI.
Busca vagas de estagio, jovem aprendiz e suporte tecnico
em multiplos sites e salva os resultados em vagas.csv.

Uso:
    python vagas_scraper.py

Dependencias:
    pip install requests beautifulsoup4
"""

import csv
import time
import urllib.parse
from dataclasses import dataclass, field, asdict

import requests
from bs4 import BeautifulSoup

# ── Modelo ──────────────────────────────────────────────────────────────────

@dataclass
class Vaga:
    titulo: str = ""
    empresa: str = ""
    localizacao: str = ""
    link: str = ""
    termo_busca: str = ""
    fonte: str = ""


# ── Utilidades HTTP ─────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}


def get_soup(url: str, params: dict | None = None, timeout: int = 15) -> BeautifulSoup | None:
    """Faz GET e retorna BeautifulSoup ou None em caso de erro."""
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except requests.RequestException as exc:
        print(f"  [ERRO] {url} -> {exc}")
        return None


def pausa():
    """Pausa educada entre requests."""
    time.sleep(1.5)


# ── Scrapers por site ───────────────────────────────────────────────────────

# Cada funcao retorna list[Vaga]

def buscar_infojobs(termo: str) -> list[Vaga]:
    """
    Busca vagas no InfoJobs.
    URL de busca: https://www.infojobs.com.br/vagas-de-emprego-<termo>.aspx
    """
    print(f"  [InfoJobs] Buscando: {termo}")
    vagas: list[Vaga] = []

    termo_url = termo.replace(" ", "-").lower()
    url = f"https://www.infojobs.com.br/vagas-de-emprego-{termo_url}.aspx"

    soup = get_soup(url)
    if not soup:
        return vagas

    # InfoJobs renderiza vagas em elementos com data-test ou classes especificas
    # Tentamos seletores comuns
    cards = soup.select("div.js_cardLink, div.card-job, article.card, div[class*='card']")

    if not cards:
        # Fallback: buscar links de vaga diretamente
        cards = soup.find_all("a", href=True)

    for card in cards:
        link_tag = card if card.name == "a" else card.find("a", href=True)
        if not link_tag:
            continue

        href = link_tag.get("href", "")
        if not href or "/vaga-de-emprego/" not in href:
            continue

        titulo_tag = (
            card.select_one("h2, h3, span[class*='title'], a[class*='title']")
            or link_tag
        )
        titulo = titulo_tag.get_text(strip=True) if titulo_tag else ""

        empresa_tag = card.select_one(
            "span[class*='company'], a[class*='company'], span[class*='nome']"
        )
        empresa = empresa_tag.get_text(strip=True) if empresa_tag else "Nao informado"

        local_tag = card.select_one(
            "span[class*='location'], span[class*='cidade'], span[class*='city']"
        )
        localizacao = local_tag.get_text(strip=True) if local_tag else "Nao informado"

        if not titulo:
            continue

        if not href.startswith("http"):
            href = "https://www.infojobs.com.br" + href

        vagas.append(Vaga(
            titulo=titulo,
            empresa=empresa,
            localizacao=localizacao,
            link=href,
            termo_busca=termo,
            fonte="InfoJobs",
        ))

    print(f"    -> {len(vagas)} vagas encontradas")
    return vagas


def buscar_catho(termo: str) -> list[Vaga]:
    """
    Busca vagas na Catho.
    URL: https://www.catho.com.br/vagas/?q=<termo>
    """
    print(f"  [Catho] Buscando: {termo}")
    vagas: list[Vaga] = []

    url = "https://www.catho.com.br/vagas/"
    params = {"q": termo}

    soup = get_soup(url, params=params)
    if not soup:
        return vagas

    cards = soup.select("div.Card-sc-1, li[class*='vaga'], article, div[class*='JobCard']")

    for card in cards:
        link_tag = card.find("a", href=True)
        if not link_tag:
            continue

        href = link_tag.get("href", "")
        if not href:
            continue

        titulo_tag = card.select_one("h2, h3, a[class*='title'], span[class*='title']")
        titulo = titulo_tag.get_text(strip=True) if titulo_tag else ""

        empresa_tag = card.select_one("span[class*='company'], p[class*='company']")
        empresa = empresa_tag.get_text(strip=True) if empresa_tag else "Nao informado"

        local_tag = card.select_one("span[class*='location'], span[class*='city']")
        localizacao = local_tag.get_text(strip=True) if local_tag else "Nao informado"

        if not titulo:
            continue

        if not href.startswith("http"):
            href = "https://www.catho.com.br" + href

        vagas.append(Vaga(
            titulo=titulo,
            empresa=empresa,
            localizacao=localizacao,
            link=href,
            termo_busca=termo,
            fonte="Catho",
        ))

    print(f"    -> {len(vagas)} vagas encontradas")
    return vagas


def buscar_indeed(termo: str) -> list[Vaga]:
    """
    Busca vagas no Indeed Brasil.
    URL: https://br.indeed.com/jobs?q=<termo>
    """
    print(f"  [Indeed] Buscando: {termo}")
    vagas: list[Vaga] = []

    url = "https://br.indeed.com/jobs"
    params = {"q": termo}

    soup = get_soup(url, params=params)
    if not soup:
        return vagas

    cards = soup.select(
        "div.job_seen_beacon, "
        "div[class*='jobsearch-ResultsList'] > div, "
        "td.resultContent, "
        "div.cardOutline, "
        "div.jobTitle-color-purple, "
        "div[class*='job']"
    )

    # Fallback mais amplo
    if not cards:
        cards = soup.find_all("div", class_=lambda c: c and ("job" in c.lower() or "result" in c.lower()))

    for card in cards:
        link_tag = card.find("a", href=True)
        if not link_tag:
            continue

        href = link_tag.get("href", "")
        titulo_tag = (
            card.select_one("h2.jobTitle span, h2 a, span[title], a[id*='job_']")
            or link_tag
        )
        titulo = titulo_tag.get("title") or titulo_tag.get_text(strip=True) if titulo_tag else ""

        empresa_tag = card.select_one("span.companyName, span[class*='company'], div.company_location span")
        empresa = empresa_tag.get_text(strip=True) if empresa_tag else "Nao informado"

        local_tag = card.select_one("div.companyLocation, span[class*='location']")
        localizacao = local_tag.get_text(strip=True) if local_tag else "Nao informado"

        if not titulo:
            continue

        if not href.startswith("http"):
            href = "https://br.indeed.com" + href

        vagas.append(Vaga(
            titulo=titulo,
            empresa=empresa,
            localizacao=localizacao,
            link=href,
            termo_busca=termo,
            fonte="Indeed",
        ))

    print(f"    -> {len(vagas)} vagas encontradas")
    return vagas


def buscar_vagas_com(termo: str) -> list[Vaga]:
    """
    Busca vagas no site vagas.com.br.
    URL: https://www.vagas.com.br/vagas-de-<termo>
    """
    print(f"  [Vagas.com] Buscando: {termo}")
    vagas: list[Vaga] = []

    termo_url = urllib.parse.quote(termo)
    url = f"https://www.vagas.com.br/vagas-de-{termo.replace(' ', '-').lower()}"

    soup = get_soup(url)
    if not soup:
        return vagas

    cards = soup.select("li.vaga, div.vaga, article.vaga, li[class*='vaga']")

    for card in cards:
        link_tag = card.find("a", href=True)
        if not link_tag:
            continue

        href = link_tag.get("href", "")
        titulo = link_tag.get_text(strip=True)

        empresa_tag = card.select_one("span.empresa, span[class*='empresa'], span.nomeEmpresa")
        empresa = empresa_tag.get_text(strip=True) if empresa_tag else "Nao informado"

        local_tag = card.select_one("span.local, span[class*='local']")
        localizacao = local_tag.get_text(strip=True) if local_tag else "Nao informado"

        if not titulo:
            continue

        if not href.startswith("http"):
            href = "https://www.vagas.com.br" + href

        vagas.append(Vaga(
            titulo=titulo,
            empresa=empresa,
            localizacao=localizacao,
            link=href,
            termo_busca=termo,
            fonte="Vagas.com",
        ))

    print(f"    -> {len(vagas)} vagas encontradas")
    return vagas


def buscar_linkedin(termo: str) -> list[Vaga]:
    """
    Busca vagas publicas no LinkedIn (sem login).
    URL: https://www.linkedin.com/jobs/search/?keywords=<termo>
    """
    print(f"  [LinkedIn] Buscando: {termo}")
    vagas: list[Vaga] = []

    url = "https://www.linkedin.com/jobs/search/"
    params = {"keywords": termo, "location": "Brasil", "f_TPR": ""}

    soup = get_soup(url, params=params)
    if not soup:
        return vagas

    cards = soup.select(
        "div.base-card, "
        "li.jobs-search__results-list, "
        "div.job-search-card, "
        "div[class*='job-card']"
    )

    for card in cards:
        link_tag = card.find("a", href=True)
        if not link_tag:
            continue

        href = link_tag.get("href", "")
        titulo_tag = card.select_one("h3.base-search-card__title, h3, span.screen-reader-text")
        titulo = titulo_tag.get_text(strip=True) if titulo_tag else ""

        empresa_tag = card.select_one("h4.base-search-card__subtitle a, h4 a, span.job-search-card__company-name")
        empresa = empresa_tag.get_text(strip=True) if empresa_tag else "Nao informado"

        local_tag = card.select_one("span.job-search-card__location, span[class*='location']")
        localizacao = local_tag.get_text(strip=True) if local_tag else "Nao informado"

        if not titulo:
            continue

        if not href.startswith("http"):
            href = "https://www.linkedin.com" + href

        vagas.append(Vaga(
            titulo=titulo,
            empresa=empresa,
            localizacao=localizacao,
            link=href,
            termo_busca=termo,
            fonte="LinkedIn",
        ))

    print(f"    -> {len(vagas)} vagas encontradas")
    return vagas


# ── Orquestracao ─────────────────────────────────────────────────────────────

TERMOS_BUSCA = [
    "Estagio TI",
    "Jovem Aprendiz TI",
    "Suporte Tecnico",
]

SOURCES = [
    buscar_infojobs,
    buscar_catho,
    buscar_indeed,
    buscar_vagas_com,
    buscar_linkedin,
]


def coletar_todas_vagas() -> list[Vaga]:
    """Executa todas as buscas em todos os sites."""
    todas: list[Vaga] = []

    for termo in TERMOS_BUSCA:
        print(f"\n[Termo: {termo}]")
        for source_fn in SOURCES:
            encontradas = source_fn(termo)
            todas.extend(encontradas)
            pausa()

    return todas


def deduplicar(vagas: list[Vaga]) -> list[Vaga]:
    """Remove duplicatas por link."""
    vistos: set[str] = set()
    unicas: list[Vaga] = []
    for v in vagas:
        if v.link not in vistos:
            vistos.add(v.link)
            unicas.append(v)
    return unicas


def salvar_csv(vagas: list[Vaga], caminho: str = "vagas.csv") -> None:
    """Salva lista de vagas em CSV."""
    if not vagas:
        print("\nNenhuma vaga encontrada para salvar.")
        return

    campos = ["titulo", "empresa", "localizacao", "link", "termo_busca", "fonte"]

    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        for v in vagas:
            writer.writerow(asdict(v))

    print(f"\n{len(vagas)} vagas salvas em: {caminho}")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  SCRAPER DE VAGAS DE TI")
    print("=" * 60)

    vagas = coletar_todas_vagas()
    vagas = deduplicar(vagas)
    salvar_csv(vagas)

    # Resumo
    print("\n--- Resumo ---")
    print(f"Total de vagas coletadas: {len(vagas)}")

    fontes: dict[str, int] = {}
    for v in vagas:
        fontes[v.fonte] = fontes.get(v.fonte, 0) + 1
    for fonte, qtd in sorted(fontes.items()):
        print(f"  {fonte}: {qtd}")

    termos: dict[str, int] = {}
    for v in vagas:
        termos[v.termo_busca] = termos.get(v.termo_busca, 0) + 1
    for termo, qtd in sorted(termos.items()):
        print(f"  '{termo}': {qtd}")


if __name__ == "__main__":
    main()
