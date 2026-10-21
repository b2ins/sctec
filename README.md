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

As demais colunas (`produto`, `categoria`, `cidade`, `quantidade`, `preco_unitario`, `custo_unitario`, `desconto_pct`, `publico`, `tamanho`, `data_entrega`) permanecem no DataFrame. Custo e desconto não entram nas contas.

## Regras de texto

`categoria` passa por `strip()`, `lower()` e `re.sub()`. A regex `[^a-z\s]` remove pontuação e qualquer caractere que não seja letra sem acento ou espaço. Espaços repetidos viram um só. Se o resultado fica vazio, a categoria passa a ser `sem categoria`, em minúsculas, porque a padronização já aplicou `lower()`. O nome do produto não preenche esse vazio.

A contagem trata os dois grupos em separado:

- categoria vazia preenchida: o campo original só tinha espaço ou estava em branco;
- categoria não vazia alterada: havia texto e o resultado ficou diferente do original.

`canal_venda` também perde espaço nas pontas e espaço repetido. Os únicos valores aceitos depois da regra são `Mercado`, `Loja física` e `Web`. `loja fisica`, sem acento, entra em Loja física. Qualquer outro texto fica sem canal reconhecido e não ganha um nome inventado.

## Regras de quantidade e preço

`quantidade` é válida quando o texto é um inteiro maior que zero. Vazio, decimal, zero e número negativo ficam marcados. O valor `-1` encontrado na base não é substituído.

`preco_unitario` é válido quando está preenchido e é maior ou igual a zero. Vazio não vira zero. Preço negativo também seria marcado. O ponto é o separador decimal do arquivo.

O programa conta os problemas de cada campo e, à parte, os pedidos afetados. Esse total é a união dos dois campos. Somar as duas contagens repetiria um pedido com falha nos dois. A linha permanece no DataFrame: o erro não encerra o processamento e não apaga o texto original.

## Regras de data e de entrega

`data_venda` passa por `datetime.strptime` no formato `aaaa-mm-dd hh:mm:ss`. O texto original fica na coluna. Quando a conversão funciona, o programa extrai ano, mês, dia e hora e monta `dd/mm/aaaa` com `strftime`. Data vazia ou em outro formato fica marcada, o laço continua e a data de hoje não ocupa o lugar.

`data_entrega` só é observada quanto ao vazio. A hipótese é que todo pedido sem essa data tem `status_pedido` igual a `Cancelado`, comparado depois de `strip()`. Um contraexemplo torna a hipótese falsa nesta base. O status não é corrigido e nenhuma data de entrega é criada.

A contagem por canal usa só canal reconhecido e inclui todos os status. A contagem por período usa só `data_venda` válida, também com todos os status, no recorte ano-mês. Exclusões aparecem ao lado das contagens. Problema de quantidade ou de preço não tira o pedido dessas contas. As duas contagens são de pedidos registrados. Não são receita nem vendas concluídas.

## Como executar

É preciso Python 3.12 e a biblioteca Pandas.

```text
pip install -r requirements.txt
python src/main.py
```

Os comandos rodam na raiz do repositório. O CSV lido é `data/halloween_vendas.csv`. Além dele, a execução desta etapa usa `src/main.py`, `src/funcoes.py` e `requirements.txt`.

A leitura usa `pd.read_csv` com separador vírgula, `encoding="utf-8"` e todos os campos em texto.
