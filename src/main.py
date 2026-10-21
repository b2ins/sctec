"""Ponto de entrada da análise de pedidos da Festa em Cena."""

import sys

from funcoes import (
    aplicar_padronizacao_textual,
    caminho_csv_padrao,
    ler_csv,
    resumir_textos,
    selecionar_amostra,
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


def main() -> None:
    configurar_saida()
    caminho = caminho_csv_padrao()
    print(f"Arquivo: {caminho}")
    dados = ler_csv(caminho)
    exibir_leitura(dados)
    dados = aplicar_padronizacao_textual(dados)
    exibir_textos(dados)


if __name__ == "__main__":
    main()
