"""Funções da análise de pedidos da Festa em Cena.

O CSV original não é modificado. Os campos são lidos como texto e só são
convertidos quando uma regra precisa de número ou de data.
"""

import os

import pandas as pd


def caminho_csv_padrao() -> str:
    """Devolve o caminho de data/halloween_vendas.csv a partir deste arquivo."""
    raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(raiz, "data", "halloween_vendas.csv")


def ler_csv(caminho: str) -> pd.DataFrame:
    """Lê o CSV com Pandas, em texto, sem alterar o arquivo de origem.

    sep="," e encoding="utf-8" seguem o formato do arquivo.
    dtype=str mantém cada campo como texto para a conversão ficar explícita.
    keep_default_na=False impede que um vazio vire NaN e que um texto
    legítimo seja tratado como nulo. Quantidade, preço e data continuam
    sendo validados nas etapas seguintes.
    """
    if not os.path.isfile(caminho):
        raise FileNotFoundError(
            "CSV não encontrado em "
            f"'{caminho}'. Coloque halloween_vendas.csv na pasta data/."
        )

    dados = pd.read_csv(
        caminho,
        sep=",",
        encoding="utf-8",
        dtype=str,
        keep_default_na=False,
    )
    return dados


def selecionar_amostra(dados: pd.DataFrame, quantidade: int = 3) -> list[dict]:
    """Percorre as linhas e devolve os primeiros registros como dicionários."""
    if quantidade < 1:
        return []

    amostra = []
    for _, linha in dados.iterrows():
        if len(amostra) >= quantidade:
            break
        registro = {}
        for coluna in dados.columns:
            registro[coluna] = linha[coluna]
        amostra.append(registro)
    return amostra
