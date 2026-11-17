# Manual de Uso — Loja de Cupcakes

## Cliente

1. **Vitrine** (`index.html`): veja os cupcakes (foto, nome, preço). Use "Mais baratos primeiro" para ordenar sem recarregar. Produtos com estoque 0 não aparecem.
2. **Detalhes** (`produto.html`): veja descrição, ingredientes, peso e avaliações. A seção "Você também pode gostar" sugere acompanhamentos. Clique em "Adicionar ao carrinho".
3. **Carrinho** (`index.html` / `checkout.html`): use `+` e `-` (travando no estoque), a lixeira para remover e o campo de observação (máx. 50 caracteres). O subtotal é recalculado na hora.
4. **Checkout** (`checkout.html`): informe o CEP e clique em "Calcular frete".
   - CEP fora da área atendida → mensagem **"Cidade não atendida"** e checkout bloqueado.
   - CEP atendido → endereço preenchido e frete de R$ 20,00.
   - Preencha nome/WhatsApp/número e finalize. O sistema mostra o número do pedido, a chave PIX e o WhatsApp. Envie o comprovante pelo WhatsApp.
5. **Acompanhar** (`acompanhar.html`): digite o número do pedido. Se estiver "Aguardando Pagamento", aparece "Enviar comprovante para o número WhatsApp" + chave PIX.
6. **Avaliar** (`produto.html`): informe número de pedido entregue, nota (1–5) e comentário. Não é preciso login.

## Administrador

1. Acesse `admin.html` e faça login com usuário/senha definidos no `.env`.
2. **Produtos**: cadastre com nome, ingredientes, preço, estoque e foto (upload real). Marque "É acompanhamento" para aparecer nas sugestões. Edição sem nova foto preserva a imagem. "Inativar" zera o estoque.
3. **Pedidos**: alterne o status pelo seletor. Ao marcar "Pago / Em Preparo", o estoque é baixado automaticamente (com validação).
4. **Configurações**: altere chave PIX, WhatsApp e CEP da loja. Ao salvar um novo CEP, o IBGE é atualizado pelo ViaCEP.
