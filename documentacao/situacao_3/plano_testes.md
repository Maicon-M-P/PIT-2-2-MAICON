# Plano de Testes — Situação 3

## 1. Testes automatizados (back-end)

Arquivo: `backend/tests/test_api.py` — 10 testes com `test_client()` + mocks (offline, sem sujar o banco).

Execução: `python3 -m pytest backend/tests/test_api.py -v`
Evidência: `evidencias/testes_automatizados.log`

| # | Teste | Verifica |
|---|---|---|
| 1 | frete cidade atendida | IBGE igual → endereço + R$ 20,00 |
| 2 | frete outra cidade | IBGE diferente → "Cidade não atendida" |
| 3 | preço negativo | Produto com preço ≤ 0 é recusado |
| 4 | pedido recalcula totais | Ignora preço do front; higieniza observação |
| 5 | acompanhamento aguardando | Retorna mensagem do WhatsApp + chave PIX |
| 6 | baixa de estoque pago | Desconta estoque ao virar "Pago / Em Preparo" |
| 7 | sem baixa em outro status | "Saiu para Entrega" não desconta estoque |
| 8 | avaliação pedido não entregue | É recusada |
| 9 | avaliação pedido entregue | É salva |
| 10 | admin sem token | Rota administrativa bloqueada (401) |

## 2. Testes com 5 colegas (manual)

1. Envie o link da solução e o `formulario_colegas.pdf` para 5 colegas.
2. Cada um preenche: nome, data, o que funcionou, o que não funcionou + correção, funcionalidade não testada + por quê, e anexa snapshot de erro.
3. Consolide em `consolidacao_opinioes.pdf`.
4. Registre erros e correções no `laudo_qualidade.pdf`.
5. Salve os prints antes/depois em `evidencias/`.

Sugestão de fluxos para testar: vitrine, ordenação, detalhes + acompanhamentos, carrinho, frete (CEP atendido e não atendido), checkout PIX, acompanhamento, avaliação e painel admin.
