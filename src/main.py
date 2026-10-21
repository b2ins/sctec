"""Ponto de entrada da análise de pedidos da Festa em Cena."""

import sys

from funcoes import caminho_csv_padrao, ler_csv, selecionar_amostra

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


def main() -> None:
    configurar_saida()
    caminho = caminho_csv_padrao()
    print(f"Arquivo: {caminho}")
    dados = ler_csv(caminho)
    exibir_leitura(dados)


if __name__ == "__main__":
    main()
