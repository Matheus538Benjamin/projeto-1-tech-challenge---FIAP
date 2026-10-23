# Dicionário de dados

Este dicionário explica o que significa cada coluna: primeiro as colunas dos arquivos originais da Olist, depois as colunas criadas no notebook 01 para as duas bases do projeto (`pedidos` e `itens`, salvas em `data/processed/`). As decisões citadas (D1 a D9) estão em `qualidade_dados.md`.

## Tabelas originais (`data/raw/`, em `.csv` ou `.csv.zip`)

| Tabela | Coluna | Descrição |
|---|---|---|
| **orders** | `order_id` | Identificador do pedido (chave) |
| | `customer_id` | Cliente **daquele pedido**: muda a cada compra |
| | `order_status` | delivered, shipped, canceled, unavailable, invoiced, processing, created, approved |
| | `order_purchase_timestamp` | Data e hora da compra |
| | `order_approved_at` | Aprovação do pagamento |
| | `order_delivered_carrier_date` | Postagem (entrega à transportadora) |
| | `order_delivered_customer_date` | Entrega ao cliente |
| | `order_estimated_delivery_date` | Data prometida ao cliente (sem hora) |
| **customers** | `customer_id` | Liga com `orders` |
| | `customer_unique_id` | **Pessoa**: use para recompra |
| | `customer_zip_code_prefix`, `customer_city`, `customer_state` | Localização |
| **order_items** | `order_id`, `order_item_id` | Pedido e posição do item (1, 2, 3...) |
| | `product_id`, `seller_id` | Produto e vendedor |
| | `shipping_limit_date` | Prazo do vendedor para postar |
| | `price`, `freight_value` | Preço e frete **do item**, em R$ |
| **order_payments** | `payment_sequential` | Ordem do pagamento (um pedido pode ter vários) |
| | `payment_type` | credit_card, boleto, voucher, debit_card, not_defined |
| | `payment_installments` | Nº de parcelas |
| | `payment_value` | Valor pago naquele pagamento |
| **order_reviews** | `review_id`, `order_id` | Avaliação e pedido |
| | `review_score` | Nota de 1 a 5 |
| | `review_comment_title`, `review_comment_message` | Texto opcional |
| | `review_creation_date`, `review_answer_timestamp` | Envio da pesquisa e resposta |
| **products** | `product_category_name` | Categoria (pt) |
| | `product_weight_g`, `product_length_cm`, `product_height_cm`, `product_width_cm` | Peso e dimensões |
| | `product_photos_qty`, `product_name_lenght`, `product_description_lenght` | Qualidade do anúncio (o "lenght" com erro de grafia é do original) |
| **sellers** | `seller_id`, `seller_zip_code_prefix`, `seller_city`, `seller_state` | Vendedor e localização |
| **geolocation** | `geolocation_zip_code_prefix`, `geolocation_lat`, `geolocation_lng` | Vários pontos por prefixo de CEP |
| **category_translation** | `product_category_name`, `product_category_name_english` | Tradução pt → en |

## Base tratada `pedidos` (1 linha por pedido)

| Coluna | Tipo | Definição |
|---|---|---|
| `order_id` | texto | Chave do pedido |
| `customer_unique_id` | texto | Pessoa (D5) |
| `uf_cliente`, `cidade_cliente`, `regiao_cliente` | texto | Localização do cliente |
| `order_status` | texto | Status original |
| `gerou_venda` | bool | Status diferente de canceled/unavailable (D2) |
| `entregue` | bool | Status delivered **e** data de entrega preenchida (D6) |
| `na_janela` | bool | Compra entre 01/01/2017 e 31/08/2018 (D1) |
| `mes` | data | 1º dia do mês da compra |
| `qtd_itens`, `qtd_vendedores` | número | Itens e vendedores distintos no pedido |
| `valor_produtos`, `valor_frete` | R$ | Soma de preço e de frete dos itens |
| `gmv` | R$ | `valor_produtos + valor_frete`: **receita oficial** (D3) |
| `frete_pct_produtos` | razão | `valor_frete ÷ valor_produtos` |
| `valor_pago`, `parcelas`, `pagamento_principal` | R$ / nº / texto | Da tabela de pagamentos; só para análise de meios de pagamento |
| `categoria_principal`, `vendedor_principal`, `uf_vendedor_principal` | texto | Do item de maior preço no pedido |
| `distancia_km` | km | Distância média vendedor → cliente, em linha reta (D8) |
| `peso_total_g` | g | Peso somado dos itens |
| `dias_entrega` | dias | Compra → entrega (só entregues) |
| `prazo_prometido_dias` | dias | Compra → data estimada (só entregues) |
| `dias_aprovacao`, `dias_ate_postagem`, `dias_transporte` | dias | Tempo de cada etapa; ausente se a data estiver fora de ordem (D7) |
| `dias_atraso` | dias | Dia da entrega − dia estimado; positivo = atraso (D6) |
| `atrasado` | bool | `dias_atraso > 0`; ausente se não entregue |
| `data_inconsistente` | bool | Alguma etapa com data fora de ordem (D7) |
| `review_score` | 1–5 | Nota (D4); ausente se o cliente não avaliou |
| `avaliacao_ruim` | bool | Nota ≤ 2 |
| `tem_comentario` | bool | Cliente escreveu comentário |
| `ordem_compra_cliente` | nº | 1 = primeira compra da pessoa, 2 = segunda... |
| `cliente_recorrente` | bool | A pessoa tem 2+ pedidos na base (D5) |

## Base tratada `itens` (1 linha por item vendido)

Colunas originais de `order_items` (`preco`, `frete`) mais:

| Coluna | Definição |
|---|---|
| `categoria`, `categoria_en`, `categoria_original` | Categoria legível em pt, em en e o código original (D9) |
| `peso_g`, `volume_cm3`, `product_photos_qty` | Atributos do produto |
| `uf_vendedor`, `cidade_vendedor` | Localização do vendedor |
| `customer_unique_id`, `uf_cliente`, `order_purchase_timestamp` | Cliente e data da compra |
| `distancia_km` | Distância vendedor → cliente (D8) |
| `mesmo_estado` | Vendedor e cliente na mesma UF |
| `frete_pct_preco` | Frete ÷ preço do item |
