"""Identidade visual única para todos os gráficos do projeto.

Regra de storytelling: uma cor de destaque para o que importa, cinza para o
contexto. Paleta categórica em ordem fixa (validada para daltonismo) só quando
o gráfico precisa distinguir várias séries.
"""
import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

from . import config

SUPERFICIE = "#fcfcfb"
TINTA = "#0b0b0b"
TINTA_SECUNDARIA = "#52514e"
TINTA_SUAVE = "#898781"
GRADE = "#e1e0d9"
EIXO = "#c3c2b7"
CONTEXTO = "#c3c2b7"   # cinza para séries/barras que não são o foco

DESTAQUE = "#2a78d6"   # azul: a série que conta a história
ALERTA = "#e34948"     # vermelho: o problema (atraso, nota ruim)

CATEGORICA = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]


def aplicar_estilo():
    """Chame uma vez no início de cada notebook."""
    mpl.rcParams.update({
        "figure.facecolor": SUPERFICIE,
        "axes.facecolor": SUPERFICIE,
        "savefig.facecolor": SUPERFICIE,
        "figure.dpi": 110,
        "savefig.dpi": 200,
        "figure.figsize": (10, 4.5),
        "font.family": "sans-serif",
        "font.size": 10.5,
        "text.color": TINTA,
        "axes.labelcolor": TINTA_SECUNDARIA,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.titlepad": 14,
        "axes.edgecolor": EIXO,
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "axes.grid.axis": "y",
        "grid.color": GRADE,
        "grid.linewidth": 0.8,
        "grid.linestyle": "-",
        "axes.prop_cycle": mpl.cycler(color=CATEGORICA),
        "xtick.color": TINTA_SUAVE,
        "ytick.color": TINTA_SUAVE,
        "xtick.labelcolor": TINTA_SECUNDARIA,
        "ytick.labelcolor": TINTA_SECUNDARIA,
        "lines.linewidth": 2,
        "lines.solid_capstyle": "round",
        "legend.frameon": False,
    })


def titulo(ax, titulo: str, subtitulo: str | None = None):
    """Título que já diz a conclusão + subtítulo com o que está sendo medido."""
    ax.set_title(titulo, loc="left", pad=28 if subtitulo else 14)
    if subtitulo:
        ax.text(0, 1.04, subtitulo, transform=ax.transAxes, color=TINTA_SECUNDARIA, fontsize=10, va="bottom")


def fonte(fig, texto="Fonte: Brazilian E-Commerce Public Dataset by Olist (Kaggle). Elaboração própria."):
    """Nota de fonte abaixo de tudo (rótulos de eixo incluídos). Chame depois de montar o gráfico."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    base = min(ax.get_tightbbox(r).transformed(fig.transFigure.inverted()).y0 for ax in fig.axes)
    fig.text(0.01, base - 0.02, texto, color=TINTA_SUAVE, fontsize=8.5, ha="left", va="top")


def salvar_figura(fig, nome: str):
    config.FIGURAS.mkdir(parents=True, exist_ok=True)
    fig.savefig(config.FIGURAS / f"{nome}.png", bbox_inches="tight")


def formato_milhar(x, _pos=None):
    return f"{x:,.0f}".replace(",", ".")


MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def eixo_mensal(ax, intervalo: int = 3):
    """Rótulos de mês em português (jan/17, abr/17...)."""
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=intervalo))
    ax.xaxis.set_major_formatter(mtick.FuncFormatter(
        lambda x, _p: (lambda d: f"{MESES[d.month - 1]}/{d:%y}")(mdates.num2date(x))))


def formato_pct(casas: int = 0):
    """Formatador de eixo em % com vírgula decimal (padrão brasileiro)."""
    return mtick.FuncFormatter(lambda x, _p: f"{x:.{casas}f}%".replace(".", ","))
