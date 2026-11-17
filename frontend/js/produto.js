/* Detalhes do produto: acompanhamentos, avaliações e avaliação por número do pedido. */
function estrelas(nota) {
  return "★".repeat(Number(nota)) + "☆".repeat(5 - Number(nota));
}

document.addEventListener("DOMContentLoaded", async () => {
  const id = new URLSearchParams(location.search).get("id");
  const area = document.getElementById("detalhe");
  if (!id || !area) return;

  try {
    const dados = await api.get("/produtos/" + id);
    const p = dados.produto;
    document.getElementById("titulo-produto").textContent = p.nome;
    document.getElementById("foto-produto").src = p.imagem_url || "";
    document.getElementById("foto-produto").alt = p.nome;
    document.getElementById("desc-produto").textContent = p.descricao || "";
    document.getElementById("ingredientes").textContent = p.ingredientes || "";
    document.getElementById("peso").textContent = p.peso_gramas ? p.peso_gramas + " g" : "-";
    document.getElementById("preco-produto").textContent = money(p.preco);

    const media = dados.media_notas || {};
    document.getElementById("media").textContent =
      media.media ? `${estrelas(Math.round(media.media))} ${media.media} (${media.total} avaliações)` : "Ainda sem avaliações";

    const lista = document.getElementById("lista-avaliacoes");
    lista.innerHTML = (dados.avaliacoes || []).length
      ? dados.avaliacoes.map(a => `<p><strong>${estrelas(a.nota)}</strong> ${escapar(a.comentario || '')}</p>`).join("")
      : "<p>Nenhuma avaliação ainda.</p>";

    const acomp = document.getElementById("acompanhamentos");
    acomp.innerHTML = (dados.acompanhamentos || []).map(a => `
      <div class="card">
        <strong>${escapar(a.nome)}</strong> - ${money(a.preco)}
        <button data-id="${a.id}">Adicionar</button>
      </div>
    `).join("") || "<p>Nenhum acompanhamento cadastrado.</p>";
    acomp.querySelectorAll("button[data-id]").forEach(btn => {
      btn.addEventListener("click", () => {
        const item = dados.acompanhamentos.find(a => a.id === Number(btn.dataset.id));
        adicionarItem(item);
        btn.textContent = "Adicionado!";
      });
    });

    const botao = document.getElementById("adicionar");
    botao.addEventListener("click", () => { adicionarItem(p); botao.textContent = "Adicionado!"; });

    document.getElementById("form-avaliacao").addEventListener("submit", async (event) => {
      event.preventDefault();
      const msg = document.getElementById("msg-avaliacao");
      try {
        await api.post("/avaliacoes", {
          numero_pedido: document.getElementById("numero-pedido").value.trim(),
          produto_id: Number(id),
          nota: Number(document.getElementById("nota").value),
          comentario: document.getElementById("comentario").value,
        });
        msg.className = "mensagem sucesso";
        msg.textContent = "Avaliação registrada com sucesso!";
      } catch (erro) {
        msg.className = "mensagem erro";
        msg.textContent = erro.message;
      }
    });
  } catch (erro) {
    area.innerHTML = '<p class="mensagem erro">' + escapar(erro.message) + '</p>';
  }
});
