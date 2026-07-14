# Assistente de Vagas com Ranking de Compatibilidade

Projeto desenvolvido em Python para automatizar a busca e organizacao de vagas de Tecnologia da Informacao, com sistema de **ranking por palavras-chave** baseado no curriculo do usuario.

## Sobre o Projeto

Encontrar vagas de estagio, jovem aprendiz e posicoes de entrada em TI pode consumir muito tempo. Este projeto coleta oportunidades de diferentes plataformas e as **ranqueia por compatibilidade** com o perfil do candidato, economizando tempo na triagem.

## Funcionalidades

* Busca automatica de vagas em 5 plataformas
* Coleta de titulo, empresa, localizacao e link
* Pesquisa por multiplos termos simultaneamente
* **Ranking de compatibilidade por palavras-chave**
* **Score alto/media/baixa/minima** para cada vaga
* Exportacao dos resultados para CSV com scores
* Menu interativo no terminal
* Perfil de curriculo personalizavel (JSON)

## Como o Ranking Funciona

O sistema compara as **palavras-chave do seu curriculo** com o **titulo de cada vaga** e calcula um score:

| Tipo de Match | Peso | Descricao |
|---|---|---|
| Exato | +3 | Palavra inteira encontrada no titulo |
| Parcial | +1 | Substring encontrada no titulo |
| Nivel | +2 | Vagas de estagio para perfil de estagiario |
| Area | +2 | Area de interesse encontrada |

**Faixas de compatibilidade:**

* **ALTA** (score >= 15) — Candidatar imediatamente
* **MEDIA** (score >= 8) — Boa candidatura
* **BAIXA** (score >= 3) — Candidatura possivel
* **MINIMA** (score < 3) — Pouca relacao

## Tecnologias Utilizadas

* Python 3
* Requests
* BeautifulSoup4
* CSV
* Web Scraping
* Dataclasses

## Estrutura do Projeto

```text
assistente-vagas/
|
├── main.py              # Menu interativo (ponto de entrada)
├── vagas_scraper.py     # Scraper de vagas
├── curriculo.py         # Perfil do candidato
├── ranking.py           # Motor de compatibilidade
├── curriculo.json       # Seu perfil (editavel)
├── vagas.csv            # Vagas coletadas (gerado)
├── ranking_vagas.csv    # Ranking exportado (gerado)
├── requirements.txt
└── README.md
```

## Como Executar

1. Clone o repositorio:

```bash
git clone https://github.com/caiodevlab/Assistente-Vagas
```

2. Instale as dependencias:

```bash
pip install requests beautifulsoup4
```

3. (Opcional) Edite seu curriculo em `curriculo.json` com suas habilidades.

4. Execute o programa:

```bash
python main.py
```

5. No menu, escolha:
   - **Opcao 2** — Buscar novas vagas
   - **Opcao 3** — Buscar + Ranquear (recomendado)
   - **Opcao 1** — Ver ranking das vagas ja coletadas
   - **Opcao 4** — Editar seu curriculo
   - **Opcao 5** — Exportar ranking para CSV

## Termos de Busca

O sistema atualmente pesquisa vagas relacionadas a:

* Estagio TI
* Jovem Aprendiz TI
* Suporte Tecnico

## Fontes de Vagas

* InfoJobs
* Catho
* Indeed Brasil
* Vagas.com
* LinkedIn

## Personalizando seu Curriculo

Edite o arquivo `curriculo.json`:

```json
{
  "nome": "Seu Nome",
  "resumo": "Breve descricao do seu perfil",
  "habilidades": ["Python", "JavaScript", "SQL", "Git"],
  "nivel": "estagiario",
  "area_interesse": "TI"
}
```

O nivel pode ser: `estagiario`, `junior`, `pleno` ou `senior`.

## Melhorias Futuras

* [x] Ranking de compatibilidade com curriculo
* [ ] Analise de vagas utilizando IA (LLM)
* [ ] Notificacoes automaticas
* [ ] Dashboard de acompanhamento
* [ ] Integracao com APIs de emprego

## Autor

Projeto desenvolvido por Caio como parte do aprendizado em Python, automacao e inteligencia artificial.
