# Metodologia

Este documento explica **como o trabalho foi pensado**: qual pergunta guiou o estudo, em que ordem as análises foram feitas, quais técnicas foram usadas e por quê. A ideia é que qualquer pessoa consiga entender o caminho sem precisar abrir o código.

## 1. Pergunta norteadora e trilha do projeto

> **A Olist cresce de forma sustentável? E o que trava a satisfação e a recompra do cliente?**

O enunciado do Tech Challenge pede um relatório para **investidores e acionistas**. Investidor quer saber, basicamente, três coisas: *o negócio cresce?*, *onde está o risco?* e *onde colocar o dinheiro?*. Por isso a trilha do projeto foi resumida numa pergunta prática:

> **O que fazer para as vendas da Olist crescerem cada vez mais?**

**Vendas** é a receita bruta de vendas: preço dos produtos + frete, somados por pedido. É o principal número de um marketplace.

## 2. Os quatro tipos de análise

Nas aulas, a análise de dados foi dividida em quatro níveis, do mais simples ao mais completo. O projeto passa pelos quatro:

| Tipo de análise | Pergunta que responde | Onde aparece |
|---|---|---|
| **Descritiva** | O que aconteceu? | Notebooks 01 e 02 (qualidade dos dados, crescimento) |
| **Diagnóstica** | Por que aconteceu? | Notebooks 03 e 04 (logística, satisfação e recompra) |
| **Preditiva** | O que pode acontecer? | Notebook 05 (projeção de 2018 e regressão linear) |
| **Prescritiva** | O que fazer? | Notebook 05 (cenários, piloto, recomendações e KPIs) |

## 3. KDD primeiro, CRISP-DM depois

Duas metodologias de projeto de dados foram vistas na disciplina de Análise de Dados e Storytelling (Aula 2):

- **KDD** (*Knowledge Discovery in Databases*): serve para **explorar e descobrir**. É usado quando ainda não se sabe direito o que os dados vão mostrar. Etapas: seleção, pré-processamento, transformação, mineração (exploração) e interpretação.
- **CRISP-DM**: serve para **construir uma solução para o negócio**. Tem seis fases: entendimento do negócio, entendimento dos dados, preparação, modelagem, avaliação e implantação.

O trabalho usou as duas, cada uma no momento certo:

| Fase do projeto | Metodologia | Notebooks | O que foi feito |
|---|---|---|---|
| Seleção, limpeza e transformação | KDD (etapas 1 a 3) e CRISP-DM (fases 2 e 3) | 01 | Leitura dos 9 arquivos, nulos, ligações entre tabelas, decisões D1 a D9 e montagem das bases |
| Exploração e descoberta de padrões | **KDD** (etapas 4 e 5) | 02, 03 e 04 | Crescimento, logística, satisfação e recompra; teste das hipóteses |
| Modelo e recomendações | **CRISP-DM** (fases 4 a 6) | 05 | Projeção, cenários, piloto, regressão linear (treino e teste) e KPIs |

**Por que essa ordem:** no começo o problema ainda estava sendo entendido, então fazia sentido explorar (KDD). Quando os padrões ficaram claros (atraso, pedido com vários itens, cliente que não volta), o CRISP-DM organizou a parte de modelo e de recomendação.

## 4. A história em atos

O estudo foi montado como uma história para o investidor, em que cada ato responde a uma pergunta e abre a pergunta do próximo:

| Ato | Pergunta do investidor | Notebook | Resposta curta |
|---|---|---|---|
| 0 | Dá para confiar nos dados? | 01_qualidade_e_preparacao | Sim, depois de 9 decisões de tratamento documentadas |
| 1 | O negócio cresce? | 02_crescimento | Cresceu muito em 2017 e parou em 2018 |
| 2 | Onde a experiência quebra? | 03_logistica_satisfacao | No atraso e no pedido com vários itens |
| 3 | O cliente volta? | 04_retencao_rfm | Quase nunca: 1,9% em 6 meses |
| 4 | O que fazer, e quanto vale? | 05_modelo_e_recomendacoes | Logística primeiro, depois Norte e Nordeste, e retenção só com piloto |

## 5. 5 Porquês: "quase ninguém volta a comprar"

A técnica dos **5 Porquês** (Aula 1 de Storytelling) pergunta "por quê?" várias vezes seguidas até chegar a uma causa mais profunda. Aqui, cada resposta virou uma **hipótese para testar com os dados**, e não uma conclusão pronta.

1. **Por que o cliente não volta?** A primeira compra não cria motivo para voltar: a experiência é neutra ou ruim.
2. **Por que a experiência é ruim?** Parte dos pedidos atrasa ou demora muito, e isso derruba a nota. *(H2, H5)*
3. **Por que atrasa ou demora?** O vendedor está longe do cliente: entrega entre estados e transporte longo para o Norte e o Nordeste. *(H3)*
4. **Por que o vendedor está longe?** Os vendedores são mais concentrados que os clientes: 59,7% dos vendedores estão em SP, contra 42,0% dos clientes. *(H4)*
5. **Por que essa concentração continua?** Hipótese de causa raiz: não há incentivo para ter vendedores em outras regiões, nem uma ação de relacionamento depois da compra. *(H6, H7)*

## 6. Diagrama de Ishikawa (6M) adaptado ao e-commerce

O **Ishikawa**, ou espinha de peixe (Aula 1 de Storytelling), organiza as possíveis causas de um problema em seis grupos. O efeito estudado é **baixa satisfação e baixa recompra**.

| Categoria | Causas possíveis | Variável usada na base |
|---|---|---|
| **Método** | Prazo prometido mal calibrado; demora para postar | `prazo_prometido_dias`, `dias_ate_postagem` |
| **Máquina** | Plataforma ou rastreio; aprovação de pagamento lenta | `dias_aprovacao`, `pagamento_principal` |
| **Material** | Produto pesado ou grande; categoria; anúncio pobre | `peso_g`, `volume_cm3`, `categoria`, `product_photos_qty` |
| **Mão de obra** | Vendedores com desempenho ruim na postagem | `vendedor_principal` × atraso e nota |
| **Meio ambiente** | Distância, região, picos de venda (Black Friday) | `distancia_km`, `regiao_cliente`, `mes` |
| **Medição** | Nota só existe se o cliente responde; datas inconsistentes; meses incompletos | Decisões D1, D4 e D7 em `qualidade_dados.md` |

## 7. Hipóteses e resultados

| # | Hipótese | Como foi testada | Resultado | Notebook |
|---|---|---|---|---|
| H1 | O crescimento é consistente, além do pico da Black Friday | Tendência mensal das vendas reais; jan–ago 2017 × 2018 | ⚠️ **Parcial.** +133% real, mas parado em 2018 (−1,8% ao mês) | 02 |
| H2 | Atraso derruba a nota | % de avaliações ruins por faixa de atraso, dentro de cada região e categoria; teste qui-quadrado | ✅ De 9% (no prazo) para 62% (atrasados); cerca de 80% com 8 dias ou mais | 03 |
| H3 | Distância e entrega entre estados aumentam prazo e atraso | Prazo e atraso por faixa de distância; mesmo estado × outro estado | ✅ Até 100 km: 5 dias e 4,5% de atraso; acima de 2.000 km: 18 dias e 12% | 03 |
| H4 | Frete proporcionalmente caro pesa mais no Norte e Nordeste | Frete ÷ valor do produto por região | ✅ 22–23%, contra 15% no Sudeste | 03 |
| H5 | Prazo longo reduz a nota mesmo sem atraso | Nota por prazo real, só nos pedidos no prazo | ✅ Moderado: nota de 4,45 (até 5 dias) para 3,99 (20–30 dias) | 03 |
| H6 | Quem tem experiência ruim recompra menos | Recompra em 180 dias por nota e por atraso da 1ª compra; teste z | ✅ −21% a −24% (p < 0,05), mas até o cliente nota 5 quase não volta (2,1%) | 04 |
| H7 | A recompra depende, em parte, da categoria | Recompra por categoria da 1ª compra | ✅ De 1,0% (cool stuff) a 2,9% (pet shop) | 04 |
| H8 | A receita está concentrada | Pareto de categorias e de vendedores | ✅ Vendedores (10% fazem 66%) · ❌ Categorias (a maior tem 9%) | 02 |
| *Nova* | Pedido com vários itens gera insatisfação | Achado da exploração (KDD) + leitura dos comentários | ✅ 3 a 4 vezes mais avaliações ruins no prazo; 43% citam item faltando | 03 |

## 8. Técnicas usadas e onde elas aparecem

Todas as técnicas ficaram dentro do conteúdo do Módulo 1.

| Técnica | Para que foi usada | Notebook |
|---|---|---|
| Média, mediana, quartis e P90 | Resumir valores e prazos sem ser enganado por casos extremos | 02, 03, 05 |
| Gráfico de densidade (KDE) | Ver a forma da distribuição do valor dos pedidos | 02 |
| Correlação (Pearson e Spearman) | Ver quais variáveis andam juntas | 01, 05 |
| Correção pela inflação (IPCA) | Comparar receitas de meses diferentes de forma justa | 02, 05 |
| Crescimento médio mensal composto | Medir o ritmo de crescimento | 02 |
| Pareto (curva acumulada) | Ver se poucas categorias ou vendedores concentram a receita | 02 |
| Penetração por habitante | Comparar regiões de tamanhos diferentes | 02, 05 |
| Teste qui-quadrado e teste z de proporções | Verificar se uma diferença pode ser acaso | 03, 04 |
| Análise de coorte | Acompanhar cada "turma" de clientes ao longo dos meses | 04 |
| Segmentação RFM | Separar clientes por recência, frequência e valor | 04 |
| Amostragem estratificada e tamanho de amostra | Desenhar o piloto da campanha de 2ª compra | 05 |
| Regressão linear (mínimos quadrados) | Projetar a receita e calcular o risco de nota ruim | 05 |
| Treino e teste, R², precisão e recall | Conferir se a equação funciona em pedidos que ela nunca viu | 05 |
| KPIs com metas SMART e painel (técnica do Z) | Acompanhar se as ações estão funcionando | 05 |

## 9. A regressão linear do notebook 05, em poucas linhas

1. **Treino:** pedidos comprados de jan/2017 a mar/2018. **Teste:** pedidos de abr a ago/2018. O corte é pela data, como na vida real: a equação aprende com o passado e é usada no futuro.
2. Cada pedido vira três números: **x1** = dias de atraso (0 a 7), **x2** = itens extras (0 a 2) e **y** = nota ruim (sim ou não).
3. Os pedidos do treino são resumidos em 24 grupos iguais, e em cada grupo se calcula a % de notas ruins.
4. A regressão encontra a equação **y = 8,14 + 10,48 · x1 + 12,70 · x2**: um pedido no prazo e com 1 item tem cerca de 8% de risco; cada dia de atraso soma 10,5 pontos; cada item extra soma 12,7 pontos.
5. **Conferência:** a equação explica 98% da variação entre os grupos no treino (R² = 0,98) e 94% nos pedidos novos do teste (R² = 0,94). O critério adotado foi R² de 0,70 ou mais nos dois.
6. **Uso:** o atendimento liga para quem tem risco de 20% ou mais (13% dos pedidos) e encontra 42% dos clientes insatisfeitos, o dobro da regra "ligar só para quem atrasou".

## 10. Dados externos

O enunciado sugere enriquecer a análise com dados de fora. Foram usados dois:

| Dado | Fonte | Para que serviu |
|---|---|---|
| IPCA mensal | Banco Central (série SGS 433, IBGE) | Corrigir as vendas pela inflação, a preços de ago/2018 (crescimento real) |
| População estimada por UF, 2018 | IBGE (SIDRA, tabela 6579) | Calcular pedidos por 100 mil habitantes (penetração) |

As fontes e as conferências estão em `data/external/FONTES.md`.

## 11. KPIs oficiais (definição única)

Cada indicador tem uma fórmula só, usada em todos os notebooks:

| KPI | Fórmula | Olhado por |
|---|---|---|
| Vendas | Soma de (preço + frete) dos pedidos que viraram venda | mês, UF, categoria |
| Ticket médio | Vendas ÷ nº de pedidos que viraram venda | mês, UF |
| % de entregas atrasadas | pedidos atrasados ÷ pedidos entregues | mês, UF, vendedor |
| Prazo de entrega (mediana e P90) | dias entre a compra e a entrega | mês, UF |
| Frete relativo | soma do frete ÷ soma do valor dos produtos | região, categoria |
| % de avaliações ruins | pedidos com nota 1 ou 2 ÷ pedidos avaliados | segmento |
| Taxa de recompra em 180 dias | clientes que voltam entre o dia 1 e o dia 180 ÷ clientes da coorte | coorte, categoria |

As metas propostas para cada KPI estão no notebook 05 (seção 6).

## 12. Limitações

- **Amostra pública:** a base tem cerca de 100 mil pedidos anonimizados, e não a operação inteira da Olist. Não há custo, margem, marketing nem conversão: os valores são de vendas, não de lucro.
- **Correlação não é causa:** as relações encontradas são observacionais. Por isso o projeto propõe um **piloto** (teste com grupo de controle) antes de investir em escala.
- **Período curto:** 20 meses limitam a projeção e a leitura de sazonalidade.
- **Meses finais incompletos:** pedidos ainda não entregues ficam fora da base, o que faz o atraso recente parecer menor.
- **Nota só de quem respondeu:** quem não avaliou não entra nas contas de satisfação.
- **Comentários:** a leitura dos temas das reclamações é feita por palavras-chave e é aproximada.
