/* Vitrine: listagem, ordenação sem recarregar e adicionar ao carrinho. */
async function carregarProdutos(ordenar) {
  const Grid = document.getElementById("grid-produtos");
  if (!Grid) return;
  Grid.innerHTML = "<p>Carregando...</p>";
  try {
    const produtos = await api.get("/produtos" + (ordenar ? "?ordenar=" + ordenar : ""));
    if (produtos.length === 0) {
      Grid.innerHTML = "<p>Nenhum cupcake disponível no momento.</p>";
      return;
    }
    Grid.innerHTML = produtos.map(p => `
      <div class="card produto">
        <img src="${escapar(p.imagem_url || '')}" alt="${escapar(p.nome)}"
             onerror="this.style.display='none'">
        <h3>${escapar(p.nome)}</h3>
        <div class="preco">${money(p.preco)}</div>
        <p>${escapar(p.descricao || '').slice(0, 80)}</p>
        <button data-id="${p.id}">Adicionar ao carrinho</button>
        <a class="btn btn-secondary" href="produto.html?id=${p.id}">Ver detalhes</a>
      </div>
    `).join("");

    const produtosPorId = {};
    produtos.forEach(p => produtosPorId[p.id] = p);
    Grid.querySelectorAll("button[data-id]").forEach(btn => {
      btn.addEventListener("click", () => {
        adicionarItem(produtosPorId[Number(btn.dataset.id)]);
        btn.textContent = "Adicionado!";
      });
    });
  } catch (erro) {
    Grid.innerHTML = '<p class="mensagem erro">Não foi possível carregar os produtos: ' + escapar(erro.message) + '</p>';
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const select = document.getElementById("ordenar");
  carregarProdutos(select ? select.value : "");
  if (select) {
    select.addEventListener("change", () => carregarProdutos(select.value));
  }
  renderizarCarrinho("carrinho-resumo");
});
