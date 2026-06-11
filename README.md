# Assistente de Vagas com IA

Projeto desenvolvido em Python para automatizar a busca e organização de vagas de Tecnologia da Informação.

## Sobre o Projeto

Encontrar vagas de estágio, jovem aprendiz e posições de entrada em TI pode consumir muito tempo. Este projeto foi criado para automatizar esse processo, coletando oportunidades de diferentes plataformas e organizando os resultados em um único arquivo para análise posterior.

## Funcionalidades

* Busca automática de vagas
* Coleta de título, empresa, localização e link
* Pesquisa por múltiplos termos simultaneamente
* Exportação dos resultados para CSV
* Estrutura preparada para futuras integrações com IA

## Tecnologias Utilizadas

* Python 3
* Requests
* BeautifulSoup4
* CSV
* Web Scraping

## Termos de Busca

O sistema atualmente pesquisa vagas relacionadas a:

* Estágio TI
* Jovem Aprendiz TI
* Suporte Técnico

## Estrutura do Projeto

```text
assistente-vagas/
│
├── vagas.py
├── vagas.csv
├── curriculo.txt
├── logs/
└── README.md
```

## Como Executar

1. Clone o repositório:

```bash
git clone URL_DO_REPOSITORIO
```

2. Instale as dependências:

```bash
pip install requests beautifulsoup4
```

3. Execute o programa:

```bash
python vagas.py
```

4. Os resultados serão salvos em:

```text
vagas.csv
```

## Melhorias Futuras

* Ranking de compatibilidade com currículo
* Análise de vagas utilizando IA
* Notificações automáticas
* Dashboard de acompanhamento
* Integração com APIs de emprego

## Autor

Projeto desenvolvido por Caio como parte do aprendizado em Python, automação e inteligência artificial.
