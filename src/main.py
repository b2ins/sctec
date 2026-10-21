"""Ponto de entrada da análise de pedidos da Festa em Cena."""

import sys

from funcoes import (
    aplicar_datas,
    aplicar_padronizacao_textual,
    aplicar_validacao_numerica,
    caminho_csv_padrao,
    explorar_contagens,
    investigar_entrega,
    ler_csv,
    resumir_problemas_numericos,
    resumir_textos,
    selecionar_amostra,
    texto_descoberta_canal,
    texto_descoberta_periodo,
)

# Colunas mostradas na amostra. O DataFrame conserva todas as outras.
COLUNAS_EXIBICAO = [
    "pedido_id",
    "data_venda",
    "produto",
    "categoria",
    "canal_venda",
    "quantidade",
    "preco_unitario",
    "status_pedido",
    "data_entrega",
]


def configurar_saida() -> None:
    """Usa UTF-8 na saída para preservar acentos como 'física' e 'Concluído'."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def exibir_leitura(dados) -> None:
    """Informa o volume lido e mostra três pedidos para conferência."""
    print(f"Linhas lidas: {len(dados)}")
    print(f"Colunas ({len(dados.columns)}): {', '.join(dados.columns)}")
    print()
    print(
        "Cada linha é um pedido de um único produto e pode reunir "
        "várias unidades em quantidade. A base é fictícia."
    )
    print()

    amostra = selecionar_amostra(dados, 3)
    print(f"Três primeiros registros ({len(amostra)}):")
    numero = 0
    for registro in amostra:
        numero += 1
        print(f"--- registro {numero} ---")
        for coluna in COLUNAS_EXIBICAO:
            valor = registro.get(coluna, "")
            if valor == "":
                valor = "(vazio)"
            print(f"  {coluna}: {valor}")


def _entre_colchetes(valor: str) -> str:
    """Mostra vazio e espaço nas pontas, que o print comum esconderia."""
    if valor == "":
        return "[(vazio)]"
    return f"[{valor}]"


def exibir_textos(dados) -> None:
    """Mostra antes e depois e as contagens separadas de correção."""
    resumo = resumir_textos(dados)
    print()
    print("Padronização de categoria")
    print(f"  Vazias preenchidas com 'sem categoria': {resumo['vazias_preenchidas']}")
    print(f"  Não vazias alteradas: {resumo['nao_vazias_alteradas']}")
    print(f"  Inalteradas: {resumo['inalteradas']}")
    print(
        "  Das alteradas, só capitalização ou strip: "
        f"{resumo['alteradas_so_caixa_ou_strip']}"
    )
    print(
        "  Das alteradas, também pontuação ou espaço interno: "
        f"{resumo['alteradas_com_pontuacao']}"
    )
    print("  Exemplos de antes e depois:")
    for original, limpa in resumo["exemplos_categoria"]:
        print(f"    {_entre_colchetes(original)} -> {_entre_colchetes(limpa)}")

    print()
    print("Padronização de canal")
    print("  Antes:")
    for canal, quantidade in resumo["canais_origem"].items():
        print(f"    {_entre_colchetes(canal)}: {quantidade}")
    print("  Depois:")
    for canal, quantidade in resumo["canais_padrao"].items():
        print(f"    {_entre_colchetes(canal)}: {quantidade}")
    print(f"  Canais não reconhecidos: {resumo['canais_nao_reconhecidos']}")


def _rotulo_motivo(motivo: str) -> str:
    nomes = {
        "ausente": "ausente",
        "nao_positivo": "não é maior que zero",
        "nao_inteiro": "não é inteiro",
        "negativo": "negativo",
        "nao_numerico": "não numérico",
        "": "ok",
    }
    if motivo in nomes:
        return nomes[motivo]
    return motivo


def exibir_numericos(dados) -> None:
    """Informa problemas por campo e o total de pedidos, sem somar os dois."""
    resumo = resumir_problemas_numericos(dados)
    print()
    print("Validação numérica")
    print(f"  Linhas que seguem no processamento: {resumo['linhas']}")
    print(f"  Problemas em quantidade: {resumo['problemas_quantidade']}")
    for motivo, quantidade in resumo["motivos_quantidade"].items():
        print(f"    {_rotulo_motivo(motivo)}: {quantidade}")
    print(f"  Problemas em preco_unitario: {resumo['problemas_preco']}")
    for motivo, quantidade in resumo["motivos_preco"].items():
        print(f"    {_rotulo_motivo(motivo)}: {quantidade}")
    print(
        "  Pedidos com problema nos dois campos: "
        f"{resumo['pedidos_com_os_dois']}"
    )
    print(
        "  Pedidos afetados (união, sem somar os campos): "
        f"{resumo['pedidos_afetados']}"
    )
    print("  Exemplos marcados, com o valor original preservado:")
    for exemplo in resumo["exemplos"]:
        print(
            "    pedido "
            f"{exemplo['pedido_id']}: quantidade="
            f"{_entre_colchetes(exemplo['quantidade'])} "
            f"({_rotulo_motivo(exemplo['motivo_quantidade'])}), "
            f"preco_unitario="
            f"{_entre_colchetes(exemplo['preco_unitario'])} "
            f"({_rotulo_motivo(exemplo['motivo_preco'])})"
        )


def exibir_regras_e_exploracao(dados) -> None:
    """Mostra datas, a hipótese de entrega e as duas descobertas."""
    entrega = investigar_entrega(dados)
    contagens = explorar_contagens(dados)

    print()
    print("Datas de venda")
    print(
        "  Inválidas ou vazias: "
        f"{contagens['excluidos_data']}"
    )
    print("  Conversões válidas (texto original preservado):")
    for exemplo in contagens["exemplos_data_valida"]:
        print(
            f"    pedido {exemplo['pedido_id']}: "
            f"{_entre_colchetes(exemplo['data_venda'])} -> "
            f"{exemplo['data_venda_br']} "
            f"(ano {exemplo['ano']}, mês {exemplo['mes']}, "
            f"dia {exemplo['dia']}, hora {exemplo['hora']})"
        )
    print("  Exemplos inválidos, sem troca pela data de hoje:")
    for exemplo in contagens["exemplos_data_invalida"]:
        print(
            f"    pedido {exemplo['pedido_id']}: "
            f"{_entre_colchetes(exemplo['data_venda'])}"
        )

    print()
    print(f"Total de cancelados: {entrega['cancelados']}")
    if entrega["hipotese_verdadeira"]:
        conclusao = "verdadeira nesta base"
    else:
        conclusao = "falsa nesta base"
    print(
        "Hipótese: todo pedido com data_entrega vazia tem status Cancelado. "
        f"Resultado: {conclusao}."
    )
    print(
        "  Sem entrega e cancelados: "
        f"{entrega['sem_entrega_cancelado']}"
    )
    print(
        "  Sem entrega e com outro status: "
        f"{entrega['sem_entrega_outro_status']}"
    )
    print(
        "  Cancelados que têm data de entrega: "
        f"{entrega['cancelados_com_entrega']}"
    )
    print("  Até três contraexemplos:")
    if len(entrega["exemplos_contraexemplo"]) == 0:
        print("    nenhum")
    for exemplo in entrega["exemplos_contraexemplo"]:
        print(
            f"    pedido {exemplo['pedido_id']}: status "
            f"{exemplo['status_pedido']}, produto {exemplo['produto']}, "
            f"canal {_entre_colchetes(exemplo['canal_venda'])}, "
            f"data_venda {_entre_colchetes(exemplo['data_venda'])}, "
            "data_entrega (vazia)"
        )

    print()
    print(
        "Pedidos por canal (todos os status; canal não reconhecido fica de fora)"
    )
    print(f"  Excluídos: {contagens['excluidos_canal']}")
    for canal in sorted(contagens["por_canal"]):
        print(f"  {canal}: {contagens['por_canal'][canal]}")

    print()
    print(
        "Pedidos por ano-mês (todos os status; data inválida ou vazia fica de fora)"
    )
    print(f"  Excluídos: {contagens['excluidos_data']}")
    for periodo in sorted(contagens["por_ano_mes"]):
        print(f"  {periodo}: {contagens['por_ano_mes'][periodo]}")

    print()
    print("Descobertas")
    print(texto_descoberta_canal(contagens))
    print()
    print(texto_descoberta_periodo(contagens))


def main() -> None:
    configurar_saida()
    caminho = caminho_csv_padrao()
    print(f"Arquivo: {caminho}")
    dados = ler_csv(caminho)
    exibir_leitura(dados)
    dados = aplicar_padronizacao_textual(dados)
    exibir_textos(dados)
    dados = aplicar_validacao_numerica(dados)
    exibir_numericos(dados)
    dados = aplicar_datas(dados)
    exibir_regras_e_exploracao(dados)


if __name__ == "__main__":
    main()
