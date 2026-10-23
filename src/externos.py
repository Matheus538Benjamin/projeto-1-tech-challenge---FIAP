"""Dados externos: IPCA (deflator) e população por UF (IBGE). Fontes em data/external/FONTES.md."""
import numpy as np
import pandas as pd

from . import config


def fator_ipca(base: str = "2018-08") -> pd.Series:
    """Fator que leva valores de cada mês a preços do mês-base (padrão: ago/2018).

    Valor real = valor nominal × fator.
    """
    ipca = pd.read_csv(config.DADOS_EXTERNOS / "ipca_mensal_2017_2018.csv")
    ipca["mes"] = pd.to_datetime(ipca["mes"])
    indice = np.cumprod(1 + ipca["ipca_var_mensal_pct"] / 100)
    indice.index = ipca["mes"]
    return (indice.loc[pd.Timestamp(f"{base}-01")] / indice).rename("fator_ipca")


def populacao_uf() -> pd.DataFrame:
    pop = pd.read_csv(config.DADOS_EXTERNOS / "populacao_uf_2018.csv").set_index("uf")
    pop["regiao"] = pop.index.map(config.REGIAO_POR_UF)
    return pop
