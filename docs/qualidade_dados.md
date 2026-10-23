# Relatório de qualidade dos dados

Fonte: Brazilian E-Commerce Public Dataset by Olist (Kaggle), 9 tabelas e cerca de 100 mil pedidos (set/2016 a out/2018).
Evidências e código: `notebooks/01_qualidade_e_preparacao.ipynb`. Regras implementadas em `src/dados.py` e `src/config.py`.

Este relatório mostra o que foi encontrado de errado ou de estranho nos dados e o que foi feito em cada caso. Toda regra que muda um número virou uma **decisão numerada (D1 a D9)**, para qualquer pessoa conseguir conferir.

**Formato dos arquivos:** os 9 arquivos originais ficam em `data/raw/`, em `.csv` (versão completa) ou em `.csv.zip` (versão compactada do GitHub). O notebook 01 reconhece os dois e chega aos mesmos números.

## Inventário

| Tabela | Linhas | Observação |
|---|---:|---|
| pedidos | 99.441 | `order_id` único; 2.965 sem data de entrega (coerente com o status) |
| clientes | 99.441 | 96.096 pessoas distintas (`customer_unique_id`) |
| itens | 112.650 | 9.803 pedidos com mais de 1 item |
| pagamentos | 103.886 | 2.961 pedidos com mais de 1 pagamento |
| avaliacoes | 99.224 | 547 pedidos com mais de 1 avaliação; comentários opcionais (59% vazios) |
| produtos | 32.951 | 610 sem categoria |
| vendedores | 3.095 | 59,7% em SP |
| geolocalizacao | 1.000.163 | 261.831 linhas idênticas; 42 pontos fora do Brasil |
| traducao_categorias | 71 | 2 categorias de `produtos` sem tradução |

## Integridade

- Nenhum join perde linhas: todo pedido tem cliente e todo item tem produto e vendedor.
- 775 pedidos não têm itens (quase todos `unavailable` ou `canceled`) e ficam sem receita.
- 1 pedido não tem pagamento e 768 não têm avaliação.

## Decisões

| # | Problema encontrado | Decisão | Impacto |
|---|---|---|---|
| **D1** | 2016 tem 329 pedidos em 3 meses; set–out/2018 têm 20. São cortes da extração. | Séries temporais usam **jan/2017 a ago/2018** (20 meses). Coluna `na_janela`. | Evita crescimento e queda artificiais nas pontas. |
| **D2** | 1.234 pedidos `canceled` ou `unavailable` (1,2%). | Fora da receita (`gerou_venda = False`). Os demais status contam como venda. | Receita reflete vendas efetivas. |
| **D3** | Duas fontes de valor (itens × pagamentos). O join direto duplica valores. | **Receita oficial = vendas = preço + frete dos itens**, agregados por pedido. `payment_value` só para meios de pagamento. | As fontes batem em 99,75% dos pedidos (249 com diferença > R$ 1, compatível com juros e arredondamento). |
| **D4** | 547 pedidos com mais de 1 avaliação. | 1 avaliação por pedido: a respondida por último. Avaliação ruim = nota 1 ou 2. | Join sem duplicar pedidos. |
| **D5** | `customer_id` é gerado a cada pedido. | Cliente = `customer_unique_id`. | Recompra real: 3,12% dos clientes, contra 0% se usado `customer_id`. |
| **D6** | 8 pedidos `delivered` sem data; 6 `canceled` com data. A data estimada não tem hora. | `entregue` = status `delivered` **e** data preenchida. **Atraso = dia da entrega > dia estimado** (comparação por dia). | 96.470 pedidos entregues; 6,8% com atraso. |
| **D7** | 1.359 pedidos postados antes de aprovados; 166 antes da compra; 23 entregues antes da postagem. | A etapa afetada vira ausente e o pedido recebe `data_inconsistente = True`. O prazo total é mantido, porque nenhuma entrega é anterior à compra. | Tempos por etapa sem valores negativos. |
| **D8** | Vários pontos por prefixo de CEP, pontos fora do Brasil e grafias diferentes de cidade. | 1 coordenada por prefixo (mediana) dentro do território. Cidade e UF vêm de clientes e vendedores. Distância vendedor → cliente por haversine. | Distância ausente para 1,3% dos pedidos (CEP sem coordenada). |
| **D9** | 2 categorias sem tradução; 610 produtos sem categoria. | Tradução manual em `config.py`; ausentes viram `sem categoria`. Gráficos em português. | Nenhum produto descartado. |

## Limitações conhecidas

- **Censura à direita:** pedidos de ago/2018 ainda em trânsito na data da extração (47 `shipped`) ficam fora das métricas de prazo. O efeito é pequeno, mas existe.
- **Avaliação condicionada:** a nota só existe quando o cliente responde. Ausência de avaliação não significa satisfação.
- **Distância em linha reta** subestima a rota real, mas preserva a ordem (longe × perto), que é o que importa para comparar.
- **Base anonimizada:** não há dados de margem, custo logístico real nem marketing. As recomendações de valor financeiro são estimativas baseadas nas vendas (preço + frete), e não no lucro.
