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

É preciso Python 3.12 e Pandas.

```text
pip install -r requirements.txt
python src/main.py
```

Os comandos rodam na raiz do repositório. O CSV fica em `data/halloween_vendas.csv`. A execução usa esse arquivo, `src/main.py`, `src/funcoes.py` e `requirements.txt`. Nada é gravado por cima do CSV.

A leitura usa `pd.read_csv` com separador vírgula, `encoding="utf-8"` e todos os campos em texto. A saída, nesta ordem, mostra o volume e três pedidos, o antes e o depois dos textos, os problemas numéricos, as datas, a hipótese de entrega, as contagens e as duas descobertas.

## Resultados

A execução leu 1.500 linhas. Como `pedido_id` não se repete, são 1.500 pedidos.

Categorias vazias preenchidas com `sem categoria`: 18. Categorias não vazias alteradas: 1.482. Dessas, 1.427 mudaram só por capitalização ou por `strip()`, e 55 também perderam pontuação, como `FANTASIA!!!`. Canais depois da regra: Web 666, Loja física 551 e Mercado 283. Nenhum canal ficou de fora.

Problemas de quantidade: 7, todos com o texto `-1`. Problemas de preço: 12, todos ausentes. Pedidos com falha nos dois campos: 0. Pedidos afetados, pela união: 19. As 1.500 linhas continuam no processamento.

Datas de venda inválidas: 4, com o texto `data_invalida`. Elas não foram trocadas pela data de hoje. Cancelados: 109.

### Entrega sem data

A hipótese é falsa nesta base. Há 109 pedidos sem entrega e cancelados, e 34 sem entrega com outro status, todos `Concluído`. Os três primeiros contraexemplos são os pedidos 1170, 990 e 740. Nenhum cancelado tem data de entrega, mas o caminho inverso não fecha: falta de data não identifica sozinha um cancelamento, porque também aparece em pedido concluído. Status e data de entrega não foram alterados.

### Descoberta por canal

Web registra 666 de 1.500 pedidos com canal reconhecido (44,4%), à frente de Loja física (551) e Mercado (283). Web reúne 70 dos 109 cancelamentos (64,2%). A taxa é 10,5% na Web, 5,6% na Loja física e 2,8% no Mercado. Leitura: o site concentra pedidos registrados e cancelamentos. A conta não é receita nem venda concluída, e não usa `quantidade` como se cada unidade fosse um pedido. Limite: a base é fictícia; zero pedidos saíram por canal não reconhecido; a taxa usa o status informado e não explica o motivo do cancelamento.

### Descoberta por período

Outubro é o pico nos dois anos. Em 2024, outubro tem 393 pedidos e agosto tem 77 (5,1 vezes). Em 2025, outubro tem 410 e agosto tem 62 (6,6 vezes). Os dois outubros somam 803 dos 1.496 pedidos com data válida (53,7%). O restante com data válida fica em 2024-08 (77), 2024-09 (104), 2024-11 (174), 2025-08 (62), 2025-09 (94) e 2025-11 (182). Leitura: o mês do Halloween concentra os pedidos registrados, e o pico de 2025 fica pouco acima do de 2024. A conta não é receita nem venda concluída, e o mês inteiro não se resume ao dia 31. Limite: a base é fictícia; o recorte é ano-mês para 2024 e 2025 não se misturarem; 4 datas inválidas ficaram de fora.

## Qualidade dos dados e Machine Learning

Antes de interpretar a tabela ou levá-la a um modelo, é preciso ver o que está ausente, escrito de formas diferentes ou com data inválida. Esses defeitos mudam as contagens e mudariam o que o modelo aprenderia. Preencher a categoria com o nome do produto, trocar preço vazio por zero ou trocar `data_invalida` pela data de hoje inventaria sinal.

A limpeza não evita, sozinha, overfitting nem underfitting. Também pesam a representatividade da amostra, a escolha do modelo e a forma de avaliá-lo. Este CSV é fictício e foi sujo de propósito. A frequência de outubro ou da Web não estima o mercado real de Halloween. O projeto para na preparação e na exploração. As regras acima fazem parte do resultado, porque definem o que um modelo posterior teria permissão de ver.

A base não traz dimensões físicas. Os campos numéricos pedidos pelo enunciado são `quantidade` e `preco_unitario`.

## Branches

Cada sprint foi uma branch e entrou em `main` por fast-forward.

- `sprint-1-ingestao`: ler o CSV, conferir 1.500 linhas e registrar o que é um pedido.
- `sprint-2-strings`: limpar categoria com `strip()`, `lower()` e `re.sub()`, e padronizar o canal.
- `sprint-3-validacao`: marcar quantidade e preço inválidos sem imputar valor.
- `sprint-4-regras-datas`: converter `data_venda`, testar a hipótese da entrega e contar canal e ano-mês.
- `sprint-5-relatorio`: fechar este README e o `report.md`.

O arquivo `report.md` repete a leitura em formato de relatório. A contagem conferida com `len()` em Python, no arquivo UTF-8 e incluindo espaços, é 2.588 caracteres. Sem as quebras de linha, são 2.573. Os dois valores ficam entre 1.500 e 3.000.

O vídeo de 5 a 7 minutos é outra entrega, no AVA. Este repositório não o contém.

Um passo posterior, fora deste escopo, seria revisar com quem registrou os pedidos os 34 concluídos sem data de entrega, antes de usar a tabela em um modelo. Custo e desconto continuam sem uso. Não há gráfico nem teste automatizado além de executar `src/main.py`.
