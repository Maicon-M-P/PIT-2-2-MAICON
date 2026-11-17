/* Checkout: CEP/ViaCEP, frete, dados do cliente, PIX estático e WhatsApp. */
let freteCalculado = null;

document.addEventListener("DOMContentLoaded", async () => {
  renderizarCarrinho("resumo-pedido");

  try {
    const config = await api.get("/loja/config");
    document.getElementById("config-loja").textContent =
      `Atendemos ${config.cidade_atendida || "nossa cidade"}. Chave PIX: ${config.chave_pix}`;
  } catch (e) { /* a configuração também volta no retorno do pedido */ }

  document.getElementById("btn-calcular").addEventListener("click", async () => {
    const cep = document.getElementById("cep").value.replace(/\D/g, "");
    const saida = document.getElementById("resultado-frete");
    try {
      const dados = await api.get("/frete/" + cep);
      freteCalculado = dados;
      saida.className = "mensagem sucesso";
      saida.innerHTML = `${escapar(dados.logradouro || '')}, ${escapar(dados.bairro || '')} - ` +
                        `${escapar(dados.cidade || '')}<br>Frete: ${money(dados.frete)}`;
      document.getElementById("endereco-rua").value = dados.logradouro || "";
      document.getElementById("endereco-bairro").value = dados.bairro || "";
      document.getElementById("endereco-cidade").value = dados.cidade || "";
    } catch (erro) {
      freteCalculado = null;
      saida.className = "mensagem erro";
      saida.textContent = erro.message;
    }
  });

  document.getElementById("form-checkout").addEventListener("submit", async (event) => {
    event.preventDefault();
    const saida = document.getElementById("resultado-pedido");
    if (!freteCalculado) {
      saida.className = "mensagem erro";
      saida.textContent = "Calcule o frete antes de finalizar.";
      return;
    }
    const itens = lerCarrinho().map(i => ({
      produto_id: i.id, quantidade: i.quantidade, observacao: i.observacao,
    }));
    try {
      const pedido = await api.post("/pedidos", {
        cliente_nome: document.getElementById("cliente-nome").value,
        cliente_whatsapp: document.getElementById("cliente-whatsapp").value,
        cep: document.getElementById("cep").value.replace(/\D/g, ""),
        endereco_numero: document.getElementById("endereco-numero").value,
        endereco_complemento: document.getElementById("endereco-complemento").value,
        itens,
      });
      salvarCarrinho([]);
      saida.className = "mensagem sucesso";
      saida.innerHTML = `
        <h3>Pedido ${escapar(pedido.numero_pedido)} criado!</h3>
        <p>Total: ${money(pedido.valor_total)}</p>
        <p><strong>Chave PIX:</strong> ${escapar(pedido.chave_pix)}</p>
        <p><strong>WhatsApp:</strong> ${escapar(pedido.whatsapp)}</p>
        <p>Envie o comprovante pelo WhatsApp e acompanhe seu pedido:</p>
        <a class="btn" href="acompanhar.html">Acompanhar pedido</a>
      `;
    } catch (erro) {
      saida.className = "mensagem erro";
      saida.textContent = erro.message;
    }
  });
});
