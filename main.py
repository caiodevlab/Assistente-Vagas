"""
Ponto de entrada principal do Assistente de Vagas.
Menu interativo para buscar vagas e ver ranking de compatibilidade.
"""

import csv
import os
import sys

from curriculo import Curriculo
from ranking import ranquear_vagas, formatar_ranking


def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")


def exibir_menu():
    print()
    print("=" * 50)
    print("  ASSISTENTE DE VAGAS - MENU PRINCIPAL")
    print("=" * 50)
    print()
    print("  1 - Ver ranking de compatibilidade (vagas.csv)")
    print("  2 - Buscar novas vagas (executa scraper)")
    print("  3 - Buscar + Ranquear (completo)")
    print("  4 - Ver/Editar meu curriculo")
    print("  5 - Exportar ranking para CSV")
    print("  0 - Sair")
    print()
    print("-" * 50)


def carregar_vagas_csv(caminho: str = "vagas.csv") -> list[dict]:
    """Carrega vagas do arquivo CSV."""
    if not os.path.exists(caminho):
        print(f"\n[ERRO] Arquivo '{caminho}' nao encontrado.")
        print("  Execute a busca de vagas primeiro (opcao 2).")
        return []

    vagas = []
    with open(caminho, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            vagas.append(dict(row))

    print(f"\n[INFO] {len(vagas)} vagas carregadas de '{caminho}'.")
    return vagas


def opcao_ranking():
    """Opcao 1: Ver ranking de compatibilidade."""
    vagas = carregar_vagas_csv()
    if not vagas:
        return

    curriculo = Curriculo.carregar("curriculo.json")
    print(f"\n[INFO] Curriculo: {curriculo.nome}")
    print(f"  Habilidades: {', '.join(curriculo.habilidades[:8])}...")

    resultados = ranquear_vagas(vagas, curriculo)
    print(formatar_ranking(resultados, top_n=25))


def opcao_buscar():
    """Opcao 2: Executar scraper."""
    print("\n[INFO] Executando scraper de vagas...")
    print("  Isso pode levar alguns minutos.\n")

    # Importa e executa o scraper
    try:
        from vagas_scraper import main as scraper_main
        scraper_main()
    except ImportError:
        print("[ERRO] Modulo vagas_scraper.py nao encontrado.")
    except Exception as exc:
        print(f"[ERRO] Falha no scraper: {exc}")


def opcao_completo():
    """Opcao 3: Buscar vagas e ranquear."""
    opcao_buscar()
    print("\n")
    opcao_ranking()


def opcao_curriculo():
    """Opcao 4: Ver e editar curriculo."""
    curriculo = Curriculo.carregar("curriculo.json")

    print("\n" + "=" * 50)
    print("  SEU CURRICULO")
    print("=" * 50)
    print(curriculo)
    print(f"\n  Keywords geradas: {', '.join(curriculo.keywords[:12])}...")
    print("-" * 50)

    print("\n  Deseja editar? (s/n): ", end="")
    escolha = input().strip().lower()

    if escolha == "s":
        print("\n  Nome (Enter para manter): ", end="")
        nome = input().strip()
        if nome:
            curriculo.nome = nome

        print("  Nivel (estagiario/junior/pleno/senior) (Enter para manter): ", end="")
        nivel = input().strip().lower()
        if nivel:
            curriculo.nivel = nivel

        print("  Area de interesse (Enter para manter): ", end="")
        area = input().strip()
        if area:
            curriculo.area_interesse = area

        print(
            "  Habilidades (separadas por virgula) (Enter para manter): ", end=""
        )
        hab = input().strip()
        if hab:
            curriculo.habilidades = [h.strip() for h in hab.split(",") if h.strip()]

        curriculo.salvar("curriculo.json")
        print("\n[OK] Curriculo atualizado!")
    else:
        print("  Nenhuma alteracao feita.")


def opcao_exportar():
    """Opcao 5: Exportar ranking para CSV."""
    vagas = carregar_vagas_csv()
    if not vagas:
        return

    curriculo = Curriculo.carregar("curriculo.json")
    resultados = ranquear_vagas(vagas, curriculo)

    caminho_saida = "ranking_vagas.csv"
    campos = [
        "posicao", "score", "compatibilidade", "nivel",
        "titulo", "empresa", "localizacao", "fonte",
        "link", "matches",
    ]

    with open(caminho_saida, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        for i, r in enumerate(resultados, 1):
            writer.writerow({
                "posicao": i,
                "score": r.score,
                "compatibilidade": r.compatibilidade,
                "nivel": r.nivel,
                "titulo": r.titulo,
                "empresa": r.empresa,
                "localizacao": r.localizacao,
                "fonte": r.fonte,
                "link": r.link,
                "matches": "; ".join(r.matches),
            })

    print(f"\n[OK] Ranking exportado para: {caminho_saida}")
    print(f"  {len(resultados)} vagas ranqueadas.")


def main():
    limpar_tela()
    print("\n  Bem-vindo ao Assistente de Vagas!")
    print("  Encontre as melhores vagas para seu perfil.\n")

    while True:
        exibir_menu()
        print("  Escolha uma opcao: ", end="")
        opcao = input().strip()

        if opcao == "1":
            opcao_ranking()
        elif opcao == "2":
            opcao_buscar()
        elif opcao == "3":
            opcao_completo()
        elif opcao == "4":
            opcao_curriculo()
        elif opcao == "5":
            opcao_exportar()
        elif opcao == "0":
            print("\n  Ate logo! Boa sorte nas aplicacoes!\n")
            sys.exit(0)
        else:
            print("\n  Opcao invalida. Tente novamente.")

        print("\nPressione Enter para continuar...")
        input()
        limpar_tela()


if __name__ == "__main__":
    main()
