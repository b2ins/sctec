# Relatório — pedidos da Festa em Cena

A análise cobre 1.500 pedidos fictícios de agosto a novembro de 2024 e de 2025. Cada linha é um pedido de um único produto e pode reunir várias unidades. Os números abaixo são pedidos registrados. Não são unidades, receita nem vendas concluídas, e não descrevem o mercado real de Halloween.

A categoria veio vazia em 18 pedidos e foi preenchida com "sem categoria", sem consultar o produto. Outros 1.482 tinham texto e mudaram na padronização: 1.427 só pela capitalização ou pelo espaço nas pontas, e 55 também pela pontuação, no padrão de "FANTASIA!!!" e "ACESSORIO!!!". O canal tinha o mesmo problema de espaço. Depois da regra ficaram Web com 666 pedidos, Loja física com 551 e Mercado com 283. Nenhum canal deixou de ser reconhecido.

Sete pedidos trazem quantidade -1. Doze deixam o preço vazio. Ninguém falha nos dois campos, então a união é 19 pedidos afetados. Os textos originais foram mantidos e as 1.500 linhas seguiram no processamento. Quatro vendas trazem a data "data_invalida" e saíram só da contagem de período. A data de hoje não ocupou esse lugar.

Há 109 cancelados. A hipótese de que toda entrega vazia é cancelamento é falsa. Os sem entrega e cancelados são 109. Os sem entrega com outro status são 34, todos concluídos, entre eles os pedidos 1170, 990 e 740. No outro sentido, nenhum cancelado tem data de entrega. Falta de data, portanto, não identifica sozinha um cancelamento. Status e data de entrega não foram corrigidos.

No canal, a Web tem 666 dos 1.500 pedidos (44,4%) e 70 dos 109 cancelamentos (64,2%). A taxa de cancelamento é 10,5% na Web, 5,6% na Loja física e 2,8% no Mercado. O site concentra o registro e o cancelamento. A taxa usa o status informado e não explica a causa. Zero pedidos saíram dessa conta por canal ilegível.

No período, outubro é o pico nos dois anos, e a conta é ano-mês para 2024 não se misturar com 2025. Outubro de 2024 tem 393 pedidos, contra 77 em agosto (5,1 vezes). Outubro de 2025 tem 410, contra 62 em agosto (6,6 vezes). Os dois outubros somam 803 dos 1.496 pedidos com data válida (53,7%). O pico de 2025 fica pouco acima do de 2024. O mês inteiro não se resume ao dia 31, e as quatro datas inválidas ficaram de fora.

Essas escolhas importam se a tabela for para Machine Learning. Categoria adivinhada pelo produto, preço vazio trocado por zero ou data inválida trocada por hoje mudariam o que o modelo veria. A limpeza organiza o registro. Ela não torna a amostra representativa nem evita, sozinha, overfitting ou underfitting, que também dependem do modelo e da avaliação.
