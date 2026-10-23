"""Checagens de qualidade reutilizáveis: inventário, chaves e coerência temporal."""
from __future__ import annotations

import pandas as pd


def inventario(tabelas: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Linhas, colunas, células nulas e linhas duplicadas de cada tabela."""
    linhas = []
    for nome, df in tabelas.items():
        nulos = df.isna().sum()
        linhas.append({
            "tabela": nome,
            "linhas": len(df),
            "colunas": df.shape[1],
            "colunas_com_nulo": int((nulos > 0).sum()),
            "celulas_nulas_%": round(100 * nulos.sum() / df.size, 2),
            "linhas_duplicadas": int(df.duplicated().sum()),
        })
    return pd.DataFrame(linhas).set_index("tabela")


def nulos_por_coluna(df: pd.DataFrame) -> pd.DataFrame:
    """Colunas com algum valor ausente, em quantidade e %."""
    n = df.isna().sum()
    n = n[n > 0]
    return pd.DataFrame({"nulos": n, "%": (100 * n / len(df)).round(2)}).sort_values("nulos", ascending=False)


def integridade_chaves(t: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Verifica se as chaves estrangeiras encontram correspondência (joins não perdem linhas)."""
    pedidos, itens = t["pedidos"], t["itens"]
    regras = [
        ("pedidos.order_id é único", int(pedidos["order_id"].duplicated().sum())),
        ("pedidos sem cliente", int((~pedidos["customer_id"].isin(t["clientes"]["customer_id"])).sum())),
        ("pedidos sem itens", int((~pedidos["order_id"].isin(itens["order_id"])).sum())),
        ("pedidos sem pagamento", int((~pedidos["order_id"].isin(t["pagamentos"]["order_id"])).sum())),
        ("pedidos sem avaliação", int((~pedidos["order_id"].isin(t["avaliacoes"]["order_id"])).sum())),
        ("itens sem produto", int((~itens["product_id"].isin(t["produtos"]["product_id"])).sum())),
        ("itens sem vendedor", int((~itens["seller_id"].isin(t["vendedores"]["seller_id"])).sum())),
        ("pedidos com mais de 1 avaliação",
         int(t["avaliacoes"]["order_id"].value_counts().gt(1).sum())),
    ]
    return pd.DataFrame(regras, columns=["checagem", "ocorrencias"]).set_index("checagem")


def coerencia_datas(pedidos: pd.DataFrame) -> pd.DataFrame:
    """Conta pedidos em que uma etapa aparece antes da anterior."""
    c, a = "order_purchase_timestamp", "order_approved_at"
    p, e = "order_delivered_carrier_date", "order_delivered_customer_date"
    regras = [
        ("aprovação antes da compra", (pedidos[a] < pedidos[c]).sum()),
        ("postagem antes da aprovação", (pedidos[p] < pedidos[a]).sum()),
        ("postagem antes da compra", (pedidos[p] < pedidos[c]).sum()),
        ("entrega antes da postagem", (pedidos[e] < pedidos[p]).sum()),
        ("entrega antes da compra", (pedidos[e] < pedidos[c]).sum()),
    ]
    return pd.DataFrame(regras, columns=["inconsistência", "pedidos"]).set_index("inconsistência")
