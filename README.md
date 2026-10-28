# Projeto 1 · Tech Challenge — O que fazer para as vendas da Olist crescerem cada vez mais?

**Tech Challenge – Fase 1 · POSTECH Data Analytics (FIAP)**
Autor: Matheus Benjamin Aquino Silva

Relatório executivo para **investidores e acionistas**, feito com o
[Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce):
cerca de 100 mil pedidos reais e anonimizados de um marketplace brasileiro, de 2016 a 2018.

## Pergunta norteadora

> **A Olist cresce de forma sustentável? E o que trava a satisfação e a recompra do cliente?**

A trilha do projeto é descobrir **o que fazer para as vendas voltarem a crescer**. Para isso, o estudo foi dividido em atos, como uma história:

| Ato | Pergunta do investidor | Notebook |
|---|---|---|
| 0 | Dá para confiar nos dados? | `01_qualidade_e_preparacao` |
| 1 | O negócio cresce? | `02_crescimento` |
| 2 | Onde a experiência quebra? | `03_logistica_satisfacao` |
| 3 | O cliente volta? | `04_retencao_rfm` |
| 4 | O que fazer, e quanto vale? | `05_modelo_e_recomendacoes` |

## Principais achados

1. **Cresceu muito, mas parou.** As vendas reais de jan–ago/2018 foram 133% maiores que as do mesmo período de 2017, mas toda a subida aconteceu em 2017. Em 2018 a receita ficou parada em cerca de R$ 1,1 milhão por mês. O crescimento veio de clientes novos: 97% dos pedidos são de primeira compra, e o ticket ficou estável em cerca de R$ 160.
2. **A experiência quebra em dois pontos.** O **atraso** é raro (6,8% dos pedidos), mas leva as avaliações ruins de 9% para 62%. O **pedido com vários itens** tem de 3 a 4 vezes mais avaliações ruins mesmo chegando no prazo, e 43% das reclamações desses pedidos citam item faltando.
3. **Quase ninguém volta.** Só 1,9% dos clientes fazem uma 2ª compra em até 6 meses. Quem volta vale o dobro, mas é tão raro que soma menos de 6% da receita.
4. **Norte e Nordeste são o maior espaço de crescimento.** Têm 36% da população e só 15% da receita, com prazo de entrega duas vezes maior e frete proporcionalmente mais caro. Levar as duas regiões à penetração do Centro-Oeste somaria cerca de R$ 1,9 milhão por ano (cerca de 21% das vendas).
5. **Uma regressão linear simples organiza o atendimento.** Com só duas informações do dia da entrega (dias de atraso e número de itens), a equação explica 98% da variação da nota ruim entre grupos de pedidos no treino e 94% no teste. Contatando 13% dos pedidos, o atendimento encontra 42% dos clientes insatisfeitos, o dobro da regra "contatar só quem atrasou".

## Como rodar

### 1. Ambiente (Python 3.10 ou mais novo)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Dados

Os 9 arquivos da Olist já vêm dentro de `data/raw/`. O notebook 01 reconhece sozinho os dois formatos:

| Versão | O que tem em `data/raw/` | Quando usar |
|---|---|---|
| Completa | os 9 arquivos `.csv` | Entrega na FIAP |
| Compactada | os 9 arquivos `.csv.zip` | Repositório do GitHub (arquivos menores) |

Não precisa descompactar nada: o pandas lê o `.csv.zip` direto. Se quiser baixar os dados de novo, eles estão no [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).

### 3. Notebooks, em ordem

```bash
jupyter lab notebooks/
```

Rode do **01 ao 05**, nessa ordem. O notebook 01 gera a pasta `data/processed/` (bases `pedidos` e `itens`), que os outros notebooks usam. Os gráficos são salvos em `reports/figures/`.

**Dica:** se aparecer erro de "variável não definida", use *Kernel → Restart & Run All*, porque cada notebook depende das células anteriores.

## Estrutura de pastas

```
projeto-1-tech-challenge/
├── data/
│   ├── raw/           os 9 arquivos originais da Olist (.csv ou .csv.zip)
│   ├── external/      IPCA (BCB/IBGE) e população por UF (IBGE), com as fontes em FONTES.md
│   └── processed/     bases pedidos e itens, geradas pelo notebook 01
├── docs/
│   ├── metodologia.md       como o estudo foi pensado: pergunta, KDD e CRISP-DM, 5 Porquês, Ishikawa, hipóteses, KPIs
│   ├── qualidade_dados.md   problemas encontrados nos dados e decisões D1 a D9
│   ├── dicionario_dados.md  colunas originais e colunas criadas
├── notebooks/         um notebook por ato (01 a 05)
├── reports/
│   ├── figures/       gráficos salvos pelos notebooks
│   ├── apresentacao/  apresentação executiva (PowerPoint)
│   └── relatorio_executivo.pdf   relatório executivo para investidores
├── src/
│   ├── config.py      caminhos, janela de análise e regras de negócio (num lugar só)
│   ├── dados.py       leitura, limpeza e montagem das bases
│   ├── externos.py    IPCA (correção da inflação) e população por UF
│   ├── qualidade.py   checagens reutilizáveis
│   └── viz.py         padrão visual dos gráficos
├── requirements.txt
└── README.md
```

## Governança

- **Uma regra, um lugar:** toda decisão que muda um número está em `src/config.py` ou `src/dados.py` e documentada em `docs/qualidade_dados.md` (decisões D1 a D9).
- **Conferências automáticas:** o notebook 01 para com erro se alguma junção perder ou duplicar pedidos, ou se a receita final não bater com a dos arquivos originais.
- **KPIs com definição única:** as fórmulas estão em `docs/metodologia.md`.
- **Reprodutível:** quem baixar o projeto chega aos mesmos números rodando os notebooks em ordem.

## Entregáveis

- Repositório: https://github.com/Matheus538Benjamin/projeto-1-tech-challenge---FIAP
- **Relatório executivo (PDF, 11 páginas):** [pasta no Google Drive](https://drive.google.com/drive/folders/1Yi2dza8N7z9f0lVTgBg-XD1bj43x06zP) (o mesmo arquivo está em [`reports/relatorio_executivo.pdf`](reports/relatorio_executivo.pdf)): sumário, contexto, análise, conclusões e anexo de governança
- **Apresentação executiva:** [abrir no Google Apresentações](https://docs.google.com/presentation/d/1c6XumK96umyMJigdoa4DV6TVo6hWppEvsjnA_u0DGb8/edit?usp=sharing) (o mesmo arquivo está em [`reports/apresentacao/`](reports/apresentacao/))
- **Vídeo executivo (até 5 min):** [pasta no Google Drive](https://drive.google.com/drive/folders/1CyDelcHw-yhLu5vPhku7n3kYJfMiqzoA)
- **Projeto completo (cópia no Drive):** [pasta no Google Drive](https://drive.google.com/drive/folders/1Zuc9WgbZRP9oDfIAtePCJUw4Rlx8U2Vn), com notebooks, códigos, documentação e os 9 CSVs
- **Todos os materiais:** [pasta do projeto no Google Drive](https://drive.google.com/drive/folders/1DSSrV1fv6M03l-zlPTsGSHwu-8eKNoIT)
