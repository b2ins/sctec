# Festa em Cena — análise de pedidos de Halloween

## Descrição do projeto

A Festa em Cena é uma rede fictícia que vende fantasias e acessórios de Halloween. Os pedidos entram por três canais: Mercado (caixa de supermercado parceiro), Loja física (loja própria) e Web (site). A gestão quer organizar os registros antes de comparar os períodos de venda.

O programa lê um único CSV, confere textos, números e datas e resume os pedidos por canal e por ano-mês. Ele não altera o arquivo original, não calcula receita e não treina modelo. Custo unitário e desconto estão no CSV, mas não entram nesta análise.

## O que é uma linha

Cada linha é um pedido distinto de um único produto. O campo `quantidade` diz quantas unidades aquele pedido contém. São 1.500 pedidos, de agosto a novembro de 2024 e de 2025. Os horários são locais de São Paulo e não trazem fuso. O Halloween, nesta atividade, é o dia 31 de outubro de cada ano.

Uma linha não é uma unidade vendida. Os dados são fictícios e contêm erros de propósito. Os números deste repositório não descrevem o mercado real.

## Quatro colunas

- `pedido_id`: identificador do pedido. Nesta base cada valor aparece uma vez, então a contagem de linhas é a contagem de pedidos.
- `data_venda`: momento em que o pedido foi registrado, no texto `aaaa-mm-dd hh:mm:ss`. O programa preserva esse texto e só cria colunas derivadas quando a conversão é válida.
- `canal_venda`: onde o pedido foi feito. O valor esperado, depois da padronização, é Mercado, Loja física ou Web.
- `status_pedido`: situação registrada do pedido (Concluído, Cancelado ou Devolvido). O programa não muda esse campo para “corrigir” a base.

As demais colunas (`produto`, `categoria`, `cidade`, `quantidade`, `preco_unitario`, `custo_unitario`, `desconto_pct`, `publico`, `tamanho`, `data_entrega`) permanecem no DataFrame. As regras de texto, número e data são documentadas nas etapas em que passam a valer.

## Como executar

É preciso Python 3.12 e a biblioteca Pandas.

```text
pip install -r requirements.txt
python src/main.py
```

Os comandos rodam na raiz do repositório. O CSV lido é `data/halloween_vendas.csv`. Além dele, a execução desta etapa usa `src/main.py`, `src/funcoes.py` e `requirements.txt`.

A leitura usa `pd.read_csv` com separador vírgula, `encoding="utf-8"` e todos os campos em texto.
