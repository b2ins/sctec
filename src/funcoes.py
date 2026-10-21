"""Funções da análise de pedidos da Festa em Cena.

O CSV original não é modificado. Os campos são lidos como texto e só são
convertidos quando uma regra precisa de número ou de data.
"""

import os
import re

import pandas as pd

# Minúscula de propósito: a limpeza aplica .lower() antes de preencher o vazio.
CATEGORIA_AUSENTE = "sem categoria"


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


def limpar_categoria(valor: str) -> str:
    """Padroniza a categoria com strip, lower e re.sub.

    A primeira regex tira pontuação e qualquer caractere que não seja letra
    sem acento ou espaço. A segunda junta espaços repetidos. Categorias
    preenchidas deste CSV usam letras sem acento, então o intervalo a-z basta.

    Se não sobrar texto, o resultado é "sem categoria". O produto da linha
    não é consultado: inventar a categoria esconderia o dado ausente.
    """
    if valor is None:
        texto = ""
    else:
        texto = str(valor)

    texto = texto.strip().lower()
    texto = re.sub(r"[^a-z\s]", "", texto)
    texto = re.sub(r"\s+", " ", texto).strip()

    if texto == "":
        return CATEGORIA_AUSENTE
    else:
        return texto


def classificar_ajuste_categoria(original: str, limpa: str) -> str:
    """Separa categoria vazia preenchida de categoria não vazia alterada.

    Texto só com espaço conta como vazio. Texto só com pontuação não conta
    como vazio: havia caracteres, e a limpeza é que o esvaziou.
    """
    if original is None:
        bruto = ""
    else:
        bruto = str(original)

    if bruto.strip() == "":
        return "vazia_preenchida"
    elif bruto != limpa:
        return "nao_vazia_alterada"
    else:
        return "inalterada"


def padronizar_canal(valor: str) -> str | None:
    """Devolve Mercado, Loja física ou Web. Canal desconhecido vira None.

    None não é substituído por um rótulo genérico. A contagem por canal
    deixa esse pedido de fora e informa a exclusão.
    """
    if valor is None:
        bruto = ""
    else:
        bruto = str(valor)

    texto = bruto.strip().lower()
    texto = re.sub(r"\s+", " ", texto)

    if texto == "mercado":
        return "Mercado"
    elif texto == "loja física" or texto == "loja fisica":
        return "Loja física"
    elif texto == "web":
        return "Web"
    else:
        return None


def _mudou_so_caixa_ou_strip(original: str, limpa: str) -> bool:
    """True quando a regex de pontuação não altera o texto já cortado."""
    etapa = str(original).strip().lower()
    sem_pontuacao = re.sub(r"[^a-z\s]", "", etapa)
    sem_pontuacao = re.sub(r"\s+", " ", sem_pontuacao).strip()
    if sem_pontuacao == "":
        sem_pontuacao = CATEGORIA_AUSENTE
    return sem_pontuacao == etapa and sem_pontuacao == limpa


def aplicar_padronizacao_textual(dados: pd.DataFrame) -> pd.DataFrame:
    """Acrescenta categoria e canal tratados e preserva os textos originais."""
    tratado = dados.copy()
    categorias = []
    ajustes = []
    canais = []
    reconhecidos = []

    for _, linha in tratado.iterrows():
        limpa = limpar_categoria(linha["categoria"])
        ajuste = classificar_ajuste_categoria(linha["categoria"], limpa)
        canal = padronizar_canal(linha["canal_venda"])
        categorias.append(limpa)
        ajustes.append(ajuste)
        if canal is None:
            canais.append("")
            reconhecidos.append(False)
        else:
            canais.append(canal)
            reconhecidos.append(True)

    tratado["categoria_limpa"] = categorias
    tratado["ajuste_categoria"] = ajustes
    tratado["canal_padrao"] = canais
    tratado["canal_reconhecido"] = reconhecidos
    return tratado


def resumir_textos(dados: pd.DataFrame) -> dict:
    """Conta correções de categoria e a redistribuição dos canais."""
    resumo = {
        "vazias_preenchidas": 0,
        "nao_vazias_alteradas": 0,
        "inalteradas": 0,
        "alteradas_so_caixa_ou_strip": 0,
        "alteradas_com_pontuacao": 0,
        "exemplos_categoria": [],
        "canais_origem": {},
        "canais_padrao": {},
        "canais_nao_reconhecidos": 0,
    }
    vistos = set()

    for _, linha in dados.iterrows():
        original = linha["categoria"]
        limpa = linha["categoria_limpa"]
        ajuste = linha["ajuste_categoria"]

        if ajuste == "vazia_preenchida":
            resumo["vazias_preenchidas"] += 1
        elif ajuste == "nao_vazia_alterada":
            resumo["nao_vazias_alteradas"] += 1
            if _mudou_so_caixa_ou_strip(original, limpa):
                resumo["alteradas_so_caixa_ou_strip"] += 1
            else:
                resumo["alteradas_com_pontuacao"] += 1
        else:
            resumo["inalteradas"] += 1

        if original not in vistos:
            vistos.add(original)
            resumo["exemplos_categoria"].append((original, limpa))

        origem = linha["canal_venda"]
        resumo["canais_origem"][origem] = resumo["canais_origem"].get(origem, 0) + 1
        if linha["canal_reconhecido"]:
            canal = linha["canal_padrao"]
            resumo["canais_padrao"][canal] = resumo["canais_padrao"].get(canal, 0) + 1
        else:
            resumo["canais_nao_reconhecidos"] += 1

    return resumo
