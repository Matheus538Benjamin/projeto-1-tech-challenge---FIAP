"""Configurações centrais do projeto: caminhos, janela de análise e regras de negócio.

Toda decisão que afeta números (janela, status válidos, definição de atraso)
fica aqui, num lugar só, para que todos os notebooks calculem igual.
"""
from pathlib import Path

# --- Caminhos -------------------------------------------------------------
RAIZ = Path(__file__).resolve().parents[1]
DADOS_BRUTOS = RAIZ / "data" / "raw"
DADOS_EXTERNOS = RAIZ / "data" / "external"
DADOS_TRATADOS = RAIZ / "data" / "processed"
BANCO_FINALIZADO = RAIZ / "data" / "banco_finalizado"   # bases finais em CSV (saída do notebook 01)
FIGURAS = RAIZ / "reports" / "figures"

# Pastas onde os CSVs originais podem estar, em ordem de preferência
PASTAS_BRUTOS_CANDIDATAS = [DADOS_BRUTOS, RAIZ / "notebooks" / "PASTA", RAIZ / "PASTA"]


def localizar_pasta_brutos() -> Path:
    """Devolve a primeira pasta que contém os CSVs da Olist (aceita .csv ou .csv.zip)."""
    for pasta in PASTAS_BRUTOS_CANDIDATAS:
        if (pasta / "olist_orders_dataset.csv").exists() or (pasta / "olist_orders_dataset.csv.zip").exists():
            return pasta
    raise FileNotFoundError(
        "CSVs da Olist não encontrados. Coloque-os em data/raw/ (ver README). "
        f"Pastas verificadas: {[str(p) for p in PASTAS_BRUTOS_CANDIDATAS]}"
    )

ARQUIVOS_BRUTOS = {
    "clientes": "olist_customers_dataset.csv",
    "geolocalizacao": "olist_geolocation_dataset.csv",
    "itens": "olist_order_items_dataset.csv",
    "pagamentos": "olist_order_payments_dataset.csv",
    "avaliacoes": "olist_order_reviews_dataset.csv",
    "pedidos": "olist_orders_dataset.csv",
    "produtos": "olist_products_dataset.csv",
    "vendedores": "olist_sellers_dataset.csv",
    "traducao_categorias": "product_category_name_translation.csv",
}

# --- Janela de análise (decisão D1) ----------------------------------------
# 2016 tem meses quase vazios (set=4, out=324, nov=0, dez=1 pedidos) e
# set–out/2018 têm só 20 pedidos: são cortes da extração, não do negócio.
# Séries temporais usam apenas os 20 meses completos.
INICIO_JANELA = "2017-01-01"
FIM_JANELA = "2018-08-31"

# --- Status (decisão D2) ---------------------------------------------------
# Pedidos que não geraram venda: não entram em receita.
STATUS_SEM_VENDA = {"canceled", "unavailable"}

# --- Avaliação ruim (decisão D6) -------------------------------------------
NOTA_RUIM_MAX = 2  # notas 1 e 2 = cliente insatisfeito

# --- Geografia --------------------------------------------------------------
# Caixa aproximada do território brasileiro (exclui coordenadas erradas).
BBOX_BRASIL = {"lat_min": -33.8, "lat_max": 5.3, "lng_min": -73.99, "lng_max": -34.7}

REGIAO_POR_UF = {
    "AC": "Norte", "AP": "Norte", "AM": "Norte", "PA": "Norte", "RO": "Norte", "RR": "Norte", "TO": "Norte",
    "AL": "Nordeste", "BA": "Nordeste", "CE": "Nordeste", "MA": "Nordeste", "PB": "Nordeste",
    "PE": "Nordeste", "PI": "Nordeste", "RN": "Nordeste", "SE": "Nordeste",
    "DF": "Centro-Oeste", "GO": "Centro-Oeste", "MT": "Centro-Oeste", "MS": "Centro-Oeste",
    "ES": "Sudeste", "MG": "Sudeste", "RJ": "Sudeste", "SP": "Sudeste",
    "PR": "Sul", "RS": "Sul", "SC": "Sul",
}

# Duas categorias existem em `products` mas faltam na tabela de tradução.
TRADUCAO_CATEGORIAS_FALTANTES = {
    "pc_gamer": "pc_gamer",
    "portateis_cozinha_e_preparadores_de_alimentos": "portable_kitchen_food_preparers",
}
