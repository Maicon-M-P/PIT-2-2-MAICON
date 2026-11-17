/* Acompanhamento de pedido pelo número, sem cadastro de cliente. */
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("form-acompanhar").addEventListener("submit", async (event) => {
    event.preventDefault();
    const numero = document.getElementById("numero").value.trim();
    const saida = document.getElementById("resultado");
    try {
      const pedido = await api.get("/pedidos/" + encodeURIComponent(numero));
      let html = `<h3>Pedido ${escapar(pedido.numero_pedido)}</h3>
                  <p><strong>Status:</strong> ${escapar(pedido.status)}</p>
                  <p><strong>Total:</strong> ${money(pedido.valor_total)}</p>`;
      if (pedido.status === "Aguardando Pagamento") {
        html += `<p class="mensagem aviso">${escapar(pedido.mensagem)}</p>
                 <p><strong>Chave PIX:</strong> ${escapar(pedido.chave_pix)}</p>
                 <p><strong>WhatsApp:</strong> ${escapar(pedido.whatsapp)}</p>`;
      }
      if (pedido.itens && pedido.itens.length) {
        html += "<h4>Itens</h4><ul>" + pedido.itens.map(i =>
          `<li>${escapar(i.produto_nome)} - ${i.quantidade}x</li>`).join("") + "</ul>";
      }
      saida.className = "card";
      saida.innerHTML = html;
    } catch (erro) {
      saida.className = "mensagem erro";
      saida.textContent = erro.message;
    }
  });
});
