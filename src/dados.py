"""Carga dos CSVs brutos e construção das bases analíticas.

Fluxo: CSVs brutos -> tabelas limpas -> duas bases analíticas
    * `pedidos`: 1 linha por pedido (receita, logística, avaliação, cliente)
    * `itens`:   1 linha por item vendido (produto, categoria, vendedor, distância)

Cada regra aplicada aqui corresponde a uma decisão numerada (D1, D2...) em
docs/qualidade_dados.md.
"""
from __future__ import annotations

import warnings

import numpy as np
import pandas as pd

from . import config

COLUNAS_DATA = {
    "pedidos": [
        "order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date",
        "order_delivered_customer_date", "order_estimated_delivery_date",
    ],
    "itens": ["shipping_limit_date"],
    "avaliacoes": ["review_creation_date", "review_answer_timestamp"],
}


# ---------------------------------------------------------------------------
# Carga
# ---------------------------------------------------------------------------
def ler_csv_bruto(arquivo: str, pasta=None) -> pd.DataFrame:
    """Lê um CSV original da Olist, aceitando o arquivo .csv ou compactado (.csv.zip)."""
    pasta = pasta or config.localizar_pasta_brutos()
    for caminho in [pasta / arquivo, pasta / f"{arquivo}.zip"]:
        if caminho.exists():
            return pd.read_csv(caminho)
    raise FileNotFoundError(f"{arquivo} não encontrado em {pasta} (nem .csv nem .csv.zip).")


def carregar_brutos(pasta=None) -> dict[str, pd.DataFrame]:
    """Lê as 9 tabelas originais, convertendo as colunas de data."""
    tabelas = {}
    for nome, arquivo in config.ARQUIVOS_BRUTOS.items():
        df = ler_csv_bruto(arquivo, pasta)
        for col in COLUNAS_DATA.get(nome, []):
            df[col] = pd.to_datetime(df[col])
        tabelas[nome] = df
    return tabelas


# ---------------------------------------------------------------------------
# Limpeza por tabela
# ---------------------------------------------------------------------------
def avaliacao_por_pedido(avaliacoes: pd.DataFrame) -> pd.DataFrame:
    """D4: mantém 1 avaliação por pedido (a respondida mais recentemente)."""
    av = avaliacoes.sort_values("review_answer_timestamp")
    av = av.drop_duplicates("order_id", keep="last")
    av = av.assign(
        tem_comentario=av["review_comment_message"].notna(),
        avaliacao_ruim=av["review_score"] <= config.NOTA_RUIM_MAX,
    )
    return av[["order_id", "review_score", "avaliacao_ruim", "tem_comentario",
               "review_creation_date", "review_answer_timestamp"]]


def geolocalizacao_por_cep(geo: pd.DataFrame) -> pd.DataFrame:
    """D8: 1 coordenada por prefixo de CEP (mediana), sem pontos fora do Brasil."""
    b = config.BBOX_BRASIL
    dentro = geo["geolocation_lat"].between(b["lat_min"], b["lat_max"]) & geo[
        "geolocation_lng"
    ].between(b["lng_min"], b["lng_max"])
    return (
        geo[dentro]
        .groupby("geolocation_zip_code_prefix", as_index=False)[["geolocation_lat", "geolocation_lng"]]
        .median()
        .rename(columns={"geolocation_zip_code_prefix": "cep_prefixo",
                         "geolocation_lat": "lat", "geolocation_lng": "lng"})
    )


def produtos_com_categoria(produtos: pd.DataFrame, traducao: pd.DataFrame) -> pd.DataFrame:
    """D9: categoria legível em português; produtos sem categoria viram 'sem categoria'."""
    mapa_en = dict(zip(traducao["product_category_name"], traducao["product_category_name_english"]))
    mapa_en.update(config.TRADUCAO_CATEGORIAS_FALTANTES)
    pr = produtos.copy()
    pr["categoria_original"] = pr["product_category_name"].fillna("sem_categoria")
    pr["categoria"] = pr["categoria_original"].str.replace("_", " ")
    pr["categoria_en"] = pr["product_category_name"].map(mapa_en).fillna("no_category")
    pr["volume_cm3"] = pr["product_length_cm"] * pr["product_height_cm"] * pr["product_width_cm"]
    return pr.rename(columns={"product_weight_g": "peso_g"})[
        ["product_id", "categoria", "categoria_en", "categoria_original", "peso_g", "volume_cm3",
         "product_photos_qty"]
    ]


def distancia_km(lat1, lng1, lat2, lng2) -> np.ndarray:
    """Distância em linha reta (haversine), em km."""
    lat1, lng1, lat2, lng2 = map(np.radians, (lat1, lng1, lat2, lng2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lng2 - lng1) / 2) ** 2
    return 2 * 6371.0 * np.arcsin(np.sqrt(a))


def _dias(fim: pd.Series, inicio: pd.Series) -> pd.Series:
    return (fim - inicio).dt.total_seconds() / 86400


# ---------------------------------------------------------------------------
# Bases analíticas
# ---------------------------------------------------------------------------
def construir_itens(t: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """1 linha por item vendido, com produto, vendedor, cliente e distância."""
    geo = geolocalizacao_por_cep(t["geolocalizacao"])
    prod = produtos_com_categoria(t["produtos"], t["traducao_categorias"])

    vend = t["vendedores"].merge(
        geo, left_on="seller_zip_code_prefix", right_on="cep_prefixo", how="left"
    ).rename(columns={"lat": "lat_vendedor", "lng": "lng_vendedor", "seller_state": "uf_vendedor",
                      "seller_city": "cidade_vendedor"})

    cli = (
        t["pedidos"][["order_id", "customer_id", "order_purchase_timestamp"]]
        .merge(t["clientes"], on="customer_id", how="left")
        .merge(geo, left_on="customer_zip_code_prefix", right_on="cep_prefixo", how="left")
        .rename(columns={"lat": "lat_cliente", "lng": "lng_cliente", "customer_state": "uf_cliente"})
    )

    it = (
        t["itens"]
        .merge(prod, on="product_id", how="left")
        .merge(vend[["seller_id", "uf_vendedor", "cidade_vendedor", "lat_vendedor", "lng_vendedor"]],
               on="seller_id", how="left")
        .merge(cli[["order_id", "customer_unique_id", "uf_cliente", "order_purchase_timestamp",
                    "lat_cliente", "lng_cliente"]], on="order_id", how="left")
    )
    it["distancia_km"] = distancia_km(it["lat_vendedor"], it["lng_vendedor"],
                                      it["lat_cliente"], it["lng_cliente"])
    it["mesmo_estado"] = it["uf_vendedor"] == it["uf_cliente"]
    it["frete_pct_preco"] = it["freight_value"] / it["price"]
    it = it.rename(columns={"price": "preco", "freight_value": "frete"})
    return it.drop(columns=["lat_vendedor", "lng_vendedor", "lat_cliente", "lng_cliente"])


def construir_pedidos(t: dict[str, pd.DataFrame], itens: pd.DataFrame) -> pd.DataFrame:
    """1 linha por pedido. Receita, prazos, atraso, avaliação e recompra."""
    o = t["pedidos"].merge(t["clientes"], on="customer_id", how="left")
    o = o.rename(columns={"customer_state": "uf_cliente", "customer_city": "cidade_cliente"})
    o["regiao_cliente"] = o["uf_cliente"].map(config.REGIAO_POR_UF)

    # Tempo -------------------------------------------------------------------
    compra = o["order_purchase_timestamp"]
    o["mes"] = compra.dt.to_period("M").dt.to_timestamp()
    o["na_janela"] = compra.between(config.INICIO_JANELA, f"{config.FIM_JANELA} 23:59:59")

    # Status (D2) -------------------------------------------------------------
    o["gerou_venda"] = ~o["order_status"].isin(config.STATUS_SEM_VENDA)
    o["entregue"] = (o["order_status"] == "delivered") & o["order_delivered_customer_date"].notna()

    # Receita (D3): vendas = preço + frete dos itens --------------------------------
    # Primeiro item de maior preço define a categoria e o vendedor "principais".
    principal = (itens.sort_values(["order_id", "preco"], ascending=[True, False])
                 .drop_duplicates("order_id")
                 [["order_id", "categoria", "seller_id", "uf_vendedor"]]
                 .rename(columns={"categoria": "categoria_principal", "seller_id": "vendedor_principal",
                                  "uf_vendedor": "uf_vendedor_principal"}))
    agg = itens.groupby("order_id").agg(
        qtd_itens=("order_item_id", "count"),
        qtd_vendedores=("seller_id", "nunique"),
        valor_produtos=("preco", "sum"),
        valor_frete=("frete", "sum"),
        distancia_km=("distancia_km", "mean"),
        peso_total_g=("peso_g", "sum"),
    ).reset_index()
    o = o.merge(agg, on="order_id", how="left").merge(principal, on="order_id", how="left")
    o["gmv"] = o["valor_produtos"] + o["valor_frete"]
    o["frete_pct_produtos"] = o["valor_frete"] / o["valor_produtos"]

    # Pagamento: só para análises de meio de pagamento (não é a receita oficial)
    pg = t["pagamentos"]
    pg_tipo = (pg.sort_values(["order_id", "payment_value"], ascending=[True, False])
               .drop_duplicates("order_id")[["order_id", "payment_type"]]
               .rename(columns={"payment_type": "pagamento_principal"}))
    pg_agg = pg.groupby("order_id").agg(valor_pago=("payment_value", "sum"),
                                        parcelas=("payment_installments", "max")).reset_index()
    o = o.merge(pg_agg, on="order_id", how="left").merge(pg_tipo, on="order_id", how="left")

    # Logística (D6, D7) -------------------------------------------------------
    o["dias_entrega"] = _dias(o["order_delivered_customer_date"], compra)
    o["prazo_prometido_dias"] = _dias(o["order_estimated_delivery_date"], compra)
    etapas = {
        "dias_aprovacao": ("order_approved_at", "order_purchase_timestamp"),
        "dias_ate_postagem": ("order_delivered_carrier_date", "order_approved_at"),
        "dias_transporte": ("order_delivered_customer_date", "order_delivered_carrier_date"),
    }
    o["data_inconsistente"] = False
    for nome, (fim, ini) in etapas.items():
        d = _dias(o[fim], o[ini])
        negativo = d < 0
        o["data_inconsistente"] = o["data_inconsistente"] | negativo
        o[nome] = d.mask(negativo)  # etapa com data trocada vira NaN; o total segue válido
    entrega_dia = o["order_delivered_customer_date"].dt.normalize()
    o["dias_atraso"] = _dias(entrega_dia, o["order_estimated_delivery_date"]).where(o["entregue"])
    o["atrasado"] = (o["dias_atraso"] > 0).where(o["entregue"]).astype("boolean")
    for col in ["dias_entrega", "prazo_prometido_dias"]:
        o[col] = o[col].where(o["entregue"])

    # Avaliação (D4) ---------------------------------------------------------
    o = o.merge(avaliacao_por_pedido(t["avaliacoes"]), on="order_id", how="left")
    for col in ["avaliacao_ruim", "tem_comentario"]:  # pedidos sem avaliação ficam <NA>
        o[col] = o[col].astype("boolean")

    # Recompra (D5): a pessoa é customer_unique_id ------------------------------
    o = o.sort_values(["customer_unique_id", "order_purchase_timestamp"])
    o["ordem_compra_cliente"] = o.groupby("customer_unique_id").cumcount() + 1
    o["cliente_recorrente"] = o.groupby("customer_unique_id")["order_id"].transform("count") > 1

    colunas = [
        "order_id", "customer_unique_id", "customer_id", "uf_cliente", "cidade_cliente", "regiao_cliente",
        "order_status", "gerou_venda", "entregue", "na_janela", "mes",
        "order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date",
        "order_delivered_customer_date", "order_estimated_delivery_date",
        "qtd_itens", "qtd_vendedores", "valor_produtos", "valor_frete", "gmv", "frete_pct_produtos",
        "valor_pago", "parcelas", "pagamento_principal",
        "categoria_principal", "vendedor_principal", "uf_vendedor_principal", "distancia_km", "peso_total_g",
        "dias_entrega", "prazo_prometido_dias", "dias_aprovacao", "dias_ate_postagem", "dias_transporte",
        "dias_atraso", "atrasado", "data_inconsistente",
        "review_score", "avaliacao_ruim", "tem_comentario",
        "ordem_compra_cliente", "cliente_recorrente",
    ]
    return o[colunas].sort_values("order_purchase_timestamp").reset_index(drop=True)


# ---------------------------------------------------------------------------
# Persistência
# ---------------------------------------------------------------------------
def salvar(df: pd.DataFrame, nome: str, pasta=config.DADOS_TRATADOS) -> str:
    """Salva em Parquet (formato oficial do projeto)."""
    pasta.mkdir(parents=True, exist_ok=True)
    try:
        caminho = pasta / f"{nome}.parquet"
        df.to_parquet(caminho, index=False)
    except ImportError:  # ambiente sem pyarrow: fallback que preserva os tipos
        warnings.warn("pyarrow não instalado; salvando em pickle. Rode `pip install -r requirements.txt`.")
        caminho = pasta / f"{nome}.pkl"
        df.to_pickle(caminho)
    return str(caminho.relative_to(config.RAIZ))


def carregar(nome: str, pasta=config.DADOS_TRATADOS) -> pd.DataFrame:
    """Lê uma base tratada gerada pelo notebook 01."""
    pq, pk = pasta / f"{nome}.parquet", pasta / f"{nome}.pkl"
    if pq.exists():
        return pd.read_parquet(pq)
    if pk.exists():
        return pd.read_pickle(pk)
    return carregar_banco(nome)  # formato oficial: CSV do banco finalizado


# ---------------------------------------------------------------------------
# Banco finalizado em CSV (saída oficial do notebook 01, entrada dos 02 a 05)
# ---------------------------------------------------------------------------
def salvar_banco(df: pd.DataFrame, nome: str, pasta=config.BANCO_FINALIZADO) -> str:
    """Salva a base em CSV padrão (vírgula, ponto decimal, UTF-8) e um JSON com os tipos.

    O CSV não guarda tipos; o arquivo `<nome>_tipos.json` permite reabrir a base
    com datas e booleanos corretos via `carregar_banco`.
    """
    import json

    pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / f"base_{nome}.csv"
    df.to_csv(caminho, index=False, encoding="utf-8")
    tipos = {c: str(t) for c, t in df.dtypes.items()}
    (pasta / f"base_{nome}_tipos.json").write_text(json.dumps(tipos, indent=1), encoding="utf-8")
    return str(caminho.relative_to(config.RAIZ))


def carregar_banco(nome: str, pasta=config.BANCO_FINALIZADO) -> pd.DataFrame:
    """Reabre uma base do banco finalizado com os tipos originais."""
    import json

    caminho = pasta / f"base_{nome}.csv"
    if not caminho.exists():
        raise FileNotFoundError(f"{caminho} não encontrado. Rode o notebook 01 primeiro.")
    tipos_arq = pasta / f"base_{nome}_tipos.json"
    tipos = json.loads(tipos_arq.read_text(encoding="utf-8")) if tipos_arq.exists() else {}
    datas = [c for c, t in tipos.items() if t.startswith("datetime")]
    texto = {c: str for c, t in tipos.items() if t in ("object", "str", "string")}
    df = pd.read_csv(caminho, parse_dates=datas, dtype=texto, low_memory=False)
    for c, t in tipos.items():
        if t == "bool":
            df[c] = df[c].astype(bool)
        elif t == "boolean":
            df[c] = df[c].astype("boolean")
        elif t.startswith("int"):
            df[c] = df[c].astype(t)
    return df
