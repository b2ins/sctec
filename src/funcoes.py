"""Funções da análise de pedidos da Festa em Cena.

O CSV original não é modificado. Os campos são lidos como texto e só são
convertidos quando uma regra precisa de número ou de data.
"""

import os
import re
from datetime import datetime

import pandas as pd

FORMATO_DATA_VENDA = "%Y-%m-%d %H:%M:%S"

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


def validar_quantidade(valor: str) -> tuple[bool, str]:
    """Quantidade válida é um inteiro maior que zero.

    O texto original não é substituído. Decimal não vira inteiro e valor
    negativo ou zero não é trocado por outro número. O motivo só explica
    a marcação do problema.
    """
    if valor is None:
        texto = ""
    else:
        texto = str(valor).strip()

    if texto == "":
        return False, "ausente"
    if re.fullmatch(r"-?[0-9]+", texto):
        if int(texto) > 0:
            return True, ""
        else:
            return False, "nao_positivo"
    else:
        return False, "nao_inteiro"


def validar_preco(valor: str) -> tuple[bool, str]:
    """Preço válido está preenchido e é maior ou igual a zero.

    Zero passa, porque a regra pede valor não negativo. Campo vazio não
    vira zero. O separador decimal do arquivo é o ponto.
    """
    if valor is None:
        texto = ""
    else:
        texto = str(valor).strip()

    if texto == "":
        return False, "ausente"
    if re.fullmatch(r"-?[0-9]+(\.[0-9]+)?", texto):
        if float(texto) < 0:
            return False, "negativo"
        else:
            return True, ""
    else:
        return False, "nao_numerico"


def aplicar_validacao_numerica(dados: pd.DataFrame) -> pd.DataFrame:
    """Marca quantidade e preço inválidos e mantém todas as linhas.

    Um erro não interrompe o laço. As colunas originais continuam com o
    texto lido do CSV, para a marcação não parecer uma correção.
    """
    tratado = dados.copy()
    quantidade_ok = []
    motivo_quantidade = []
    preco_ok = []
    motivo_preco = []
    pedido_afetado = []

    for _, linha in tratado.iterrows():
        q_valida, q_motivo = validar_quantidade(linha["quantidade"])
        p_valido, p_motivo = validar_preco(linha["preco_unitario"])
        quantidade_ok.append(q_valida)
        motivo_quantidade.append(q_motivo)
        preco_ok.append(p_valido)
        motivo_preco.append(p_motivo)
        if (not q_valida) or (not p_valido):
            pedido_afetado.append(True)
        else:
            pedido_afetado.append(False)

    tratado["quantidade_valida"] = quantidade_ok
    tratado["motivo_quantidade"] = motivo_quantidade
    tratado["preco_valido"] = preco_ok
    tratado["motivo_preco"] = motivo_preco
    tratado["pedido_com_problema_numerico"] = pedido_afetado
    return tratado


def resumir_problemas_numericos(dados: pd.DataFrame) -> dict:
    """Conta problemas por campo e pedidos afetados sem somar os campos.

    O total de pedidos é a união. Somar a contagem de quantidade com a de
    preço contaria duas vezes um pedido que falhou nos dois campos.
    """
    resumo = {
        "linhas": len(dados),
        "problemas_quantidade": 0,
        "problemas_preco": 0,
        "motivos_quantidade": {},
        "motivos_preco": {},
        "pedidos_afetados": 0,
        "pedidos_com_os_dois": 0,
        "exemplos": [],
    }

    for _, linha in dados.iterrows():
        q_invalida = not bool(linha["quantidade_valida"])
        p_invalido = not bool(linha["preco_valido"])

        if q_invalida:
            resumo["problemas_quantidade"] += 1
            motivo = linha["motivo_quantidade"]
            motivos = resumo["motivos_quantidade"]
            motivos[motivo] = motivos.get(motivo, 0) + 1
        if p_invalido:
            resumo["problemas_preco"] += 1
            motivo = linha["motivo_preco"]
            motivos = resumo["motivos_preco"]
            motivos[motivo] = motivos.get(motivo, 0) + 1
        if q_invalida and p_invalido:
            resumo["pedidos_com_os_dois"] += 1
        if q_invalida or p_invalido:
            resumo["pedidos_afetados"] += 1
            if len(resumo["exemplos"]) < 5:
                resumo["exemplos"].append(
                    {
                        "pedido_id": linha["pedido_id"],
                        "quantidade": linha["quantidade"],
                        "motivo_quantidade": linha["motivo_quantidade"],
                        "preco_unitario": linha["preco_unitario"],
                        "motivo_preco": linha["motivo_preco"],
                    }
                )

    return resumo


def converter_data_venda(valor: str) -> dict:
    """Converte data_venda com strptime e devolve as partes pedidas.

    O texto original não é reescrito. Se strptime falha, a data fica
    marcada como inválida e os campos derivados ficam vazios. A data de
    hoje não entra no lugar: um erro de calendário não vira "agora".
    """
    resultado = {
        "valida": False,
        "ano": "",
        "mes": "",
        "dia": "",
        "hora": "",
        "data_br": "",
        "ano_mes": "",
    }
    if valor is None:
        texto = ""
    else:
        texto = str(valor).strip()

    try:
        momento = datetime.strptime(texto, FORMATO_DATA_VENDA)
    except ValueError:
        return resultado

    resultado["valida"] = True
    resultado["ano"] = momento.year
    resultado["mes"] = momento.month
    resultado["dia"] = momento.day
    resultado["hora"] = momento.hour
    resultado["data_br"] = momento.strftime("%d/%m/%Y")
    resultado["ano_mes"] = momento.strftime("%Y-%m")
    return resultado


def aplicar_datas(dados: pd.DataFrame) -> pd.DataFrame:
    """Cria colunas de data a partir de data_venda e preserva o texto lido."""
    tratado = dados.copy()
    valida = []
    ano = []
    mes = []
    dia = []
    hora = []
    data_br = []
    ano_mes = []

    for _, linha in tratado.iterrows():
        convertido = converter_data_venda(linha["data_venda"])
        valida.append(convertido["valida"])
        ano.append(convertido["ano"])
        mes.append(convertido["mes"])
        dia.append(convertido["dia"])
        hora.append(convertido["hora"])
        data_br.append(convertido["data_br"])
        ano_mes.append(convertido["ano_mes"])

    tratado["data_venda_valida"] = valida
    tratado["ano"] = ano
    tratado["mes"] = mes
    tratado["dia"] = dia
    tratado["hora"] = hora
    tratado["data_venda_br"] = data_br
    tratado["ano_mes"] = ano_mes
    return tratado


def _entrega_vazia(valor: str) -> bool:
    if valor is None:
        return True
    return str(valor).strip() == ""


def investigar_entrega(dados: pd.DataFrame) -> dict:
    """Testa se todo pedido sem data de entrega está cancelado.

    A hipótese cai com um único contraexemplo. status_pedido e
    data_entrega não são alterados, e nenhuma data é inventada.
    A comparação do status é exata, depois de strip, com "Cancelado".
    """
    resumo = {
        "sem_entrega_cancelado": 0,
        "sem_entrega_outro_status": 0,
        "cancelados": 0,
        "cancelados_com_entrega": 0,
        "hipotese_verdadeira": False,
        "exemplos_contraexemplo": [],
    }

    for _, linha in dados.iterrows():
        status = str(linha["status_pedido"]).strip()
        if status == "Cancelado":
            resumo["cancelados"] += 1

        if _entrega_vazia(linha["data_entrega"]):
            if status == "Cancelado":
                resumo["sem_entrega_cancelado"] += 1
            else:
                resumo["sem_entrega_outro_status"] += 1
                if len(resumo["exemplos_contraexemplo"]) < 3:
                    resumo["exemplos_contraexemplo"].append(
                        {
                            "pedido_id": linha["pedido_id"],
                            "status_pedido": linha["status_pedido"],
                            "data_venda": linha["data_venda"],
                            "canal_venda": linha["canal_venda"],
                            "produto": linha["produto"],
                        }
                    )
        elif status == "Cancelado":
            resumo["cancelados_com_entrega"] += 1

    if resumo["sem_entrega_outro_status"] == 0:
        resumo["hipotese_verdadeira"] = True
    else:
        resumo["hipotese_verdadeira"] = False
    return resumo


def explorar_contagens(dados: pd.DataFrame) -> dict:
    """Conta pedidos por canal reconhecido e por ano-mês com data válida.

    As duas contagens incluem todos os status. Canal não reconhecido sai
    só da contagem de canal. Data inválida sai só da contagem de período.
    Problema numérico não exclui a linha: o pedido continua registrado.
    """
    por_canal = {}
    cancelados_por_canal = {}
    por_ano_mes = {}
    excluidos_canal = 0
    excluidos_data = 0
    exemplos_data_valida = []
    exemplos_data_invalida = []

    for _, linha in dados.iterrows():
        if bool(linha["canal_reconhecido"]):
            canal = linha["canal_padrao"]
            por_canal[canal] = por_canal.get(canal, 0) + 1
            if str(linha["status_pedido"]).strip() == "Cancelado":
                cancelados_por_canal[canal] = cancelados_por_canal.get(canal, 0) + 1
        else:
            excluidos_canal += 1

        if bool(linha["data_venda_valida"]):
            chave = linha["ano_mes"]
            por_ano_mes[chave] = por_ano_mes.get(chave, 0) + 1
            if len(exemplos_data_valida) < 3:
                exemplos_data_valida.append(
                    {
                        "pedido_id": linha["pedido_id"],
                        "data_venda": linha["data_venda"],
                        "data_venda_br": linha["data_venda_br"],
                        "ano": linha["ano"],
                        "mes": linha["mes"],
                        "dia": linha["dia"],
                        "hora": linha["hora"],
                    }
                )
        else:
            excluidos_data += 1
            if len(exemplos_data_invalida) < 3:
                exemplos_data_invalida.append(
                    {
                        "pedido_id": linha["pedido_id"],
                        "data_venda": linha["data_venda"],
                    }
                )

    return {
        "por_canal": por_canal,
        "cancelados_por_canal": cancelados_por_canal,
        "excluidos_canal": excluidos_canal,
        "por_ano_mes": por_ano_mes,
        "excluidos_data": excluidos_data,
        "exemplos_data_valida": exemplos_data_valida,
        "exemplos_data_invalida": exemplos_data_invalida,
    }


def _percentual(parte: int, total: int) -> str:
    if total == 0:
        return "0,0%"
    texto = f"{(100 * parte / total):.1f}"
    return texto.replace(".", ",") + "%"


def _vezes(numerador: int, denominador: int) -> str:
    if denominador == 0:
        return "não calculado"
    return f"{(numerador / denominador):.1f}".replace(".", ",")


def texto_descoberta_canal(contagens: dict) -> str:
    """Descoberta por canal, com número, leitura e limite."""
    por_canal = contagens["por_canal"]
    cancelados = contagens["cancelados_por_canal"]
    total = sum(por_canal.values())
    total_cancelados = sum(cancelados.values())
    web = por_canal.get("Web", 0)
    loja = por_canal.get("Loja física", 0)
    mercado = por_canal.get("Mercado", 0)
    web_c = cancelados.get("Web", 0)
    loja_c = cancelados.get("Loja física", 0)
    mercado_c = cancelados.get("Mercado", 0)
    excluidos = contagens["excluidos_canal"]

    return (
        f"Por canal, Web registra {web} de {total} pedidos com canal reconhecido "
        f"({_percentual(web, total)}), à frente de Loja física ({loja}) e Mercado "
        f"({mercado}). Web também reúne {web_c} dos {total_cancelados} cancelamentos "
        f"({_percentual(web_c, total_cancelados)}). A taxa de cancelamento é "
        f"{_percentual(web_c, web)} na Web, {_percentual(loja_c, loja)} na Loja física "
        f"e {_percentual(mercado_c, mercado)} no Mercado. Leitura: o site concentra "
        f"pedidos registrados e cancelamentos. A conta não é receita nem venda "
        f"concluída. Limite: a base é fictícia; {excluidos} pedidos ficaram de fora "
        f"por canal não reconhecido; a taxa usa o status informado e não explica "
        f"o motivo do cancelamento."
    )


def texto_descoberta_periodo(contagens: dict) -> str:
    """Descoberta por ano-mês, com número, leitura e limite."""
    por_ano_mes = contagens["por_ano_mes"]
    validos = sum(por_ano_mes.values())
    outubro_2024 = por_ano_mes.get("2024-10", 0)
    outubro_2025 = por_ano_mes.get("2025-10", 0)
    agosto_2024 = por_ano_mes.get("2024-08", 0)
    agosto_2025 = por_ano_mes.get("2025-08", 0)
    outubros = outubro_2024 + outubro_2025
    excluidos = contagens["excluidos_data"]

    return (
        f"Por período, outubro é o pico nos dois anos. Em 2024, outubro tem "
        f"{outubro_2024} pedidos e agosto tem {agosto_2024} "
        f"({_vezes(outubro_2024, agosto_2024)} vezes). Em 2025, outubro tem "
        f"{outubro_2025} e agosto tem {agosto_2025} "
        f"({_vezes(outubro_2025, agosto_2025)} vezes). Os dois outubros somam "
        f"{outubros} dos {validos} pedidos com data válida "
        f"({_percentual(outubros, validos)}). Leitura: o mês do Halloween concentra "
        f"os pedidos registrados, e o pico de 2025 ({outubro_2025}) fica pouco "
        f"acima do de 2024 ({outubro_2024}). A conta não é receita nem venda "
        f"concluída, e o mês inteiro não se resume ao dia 31. Limite: a base é "
        f"fictícia; o recorte é ano-mês para 2024 e 2025 não se misturarem; "
        f"{excluidos} pedidos com data inválida ou vazia ficaram de fora."
    )
