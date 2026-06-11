# Assistente de Vagas com IA

Projeto em Python para automatizar a busca, organização e análise de vagas de emprego na área de Tecnologia da Informação.

## Objetivo

O objetivo deste projeto é reduzir o tempo gasto procurando oportunidades de estágio, jovem aprendiz e vagas de entrada em TI.

O sistema busca vagas automaticamente em plataformas de emprego, organiza os resultados em uma planilha e prepara os dados para futuras análises de compatibilidade com o currículo.

## Funcionalidades

- Busca automática de vagas
- Coleta de:
  - Título da vaga
  - Empresa
  - Localização
  - Link da vaga
- Pesquisa por múltiplos termos
- Exportação para CSV
- Estrutura preparada para:
  - Ranking de compatibilidade
  - Análise por IA
  - Notificações automáticas
  - Geração de relatórios

## Tecnologias Utilizadas

- Python 3
- Requests
- BeautifulSoup4
- CSV
- Web Scraping

## Termos de Busca

Atualmente o sistema procura por vagas relacionadas a:

- Estágio TI
- Jovem Aprendiz TI
- Suporte Técnico

## Estrutura do Projeto

```text
assistente-vagas/
│
├── vagas.py
├── vagas.csv
├── curriculo.txt
├── logs/
└── README.md
