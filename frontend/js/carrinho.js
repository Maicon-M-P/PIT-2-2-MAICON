/* Carrinho salvo no localStorage (sem login do cliente). */
const CHAVE_CARRINHO = "carrinho";

function lerCarrinho() {
  try { return JSON.parse(localStorage.getItem(CHAVE_CARRINHO)) || []; }
  catch (e) { return []; }
}

function salvarCarrinho(itens) {
  localStorage.setItem(CHAVE_CARRINHO, JSON.stringify(itens));
  atualizarBadge();
}

function adicionarItem(produto) {
  const itens = lerCarrinho();
  const existente = itens.find(i => i.id === produto.id);
  if (existente) {
    if (existente.quantidade < produto.estoque) existente.quantidade++;
  } else {
    itens.push({
      id: produto.id,
      nome: produto.nome,
      preco: Number(produto.preco),
      estoque: produto.estoque,
      imagem_url: produto.imagem_url,
      quantidade: 1,
      observacao: "",
    });
  }
  salvarCarrinho(itens);
}

function alterarQuantidade(id, delta) {
  const itens = lerCarrinho();
  const item = itens.find(i => i.id === id);
  if (!item) return;
  const nova = item.quantidade + delta;
  if (nova < 1) return removerItem(id);
  if (nova > item.estoque) return;
  item.quantidade = nova;
  salvarCarrinho(itens);
}

function removerItem(id) {
  if (!confirm("Tem certeza que deseja remover este item do carrinho?")) return;
  salvarCarrinho(lerCarrinho().filter(i => i.id !== id));
}

function definirObservacao(id, texto) {
  const itens = lerCarrinho();
  const item = itens.find(i => i.id === id);
  if (item) { item.observacao = texto.slice(0, 50); salvarCarrinho(itens); }
}

function subtotal() {
  return lerCarrinho().reduce((s, i) => s + i.preco * i.quantidade, 0);
}

function atualizarBadge() {
  const badge = document.getElementById("badge-carrinho");
  if (badge) badge.textContent = lerCarrinho().reduce((s, i) => s + i.quantidade, 0);
}

function renderizarCarrinho(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;
  const itens = lerCarrinho();

  if (itens.length === 0) {
    container.innerHTML = "<p>Seu carrinho está vazio.</p>";
    return;
  }

  container.innerHTML = itens.map(i => `
    <div class="item-carrinho">
      <div><strong>${escapar(i.nome)}</strong><br>${money(i.preco)}</div>
      <div class="qtd">
        <button data-acao="menos" data-id="${i.id}">-</button>
        <span>${i.quantidade}</span>
        <button data-acao="mais" data-id="${i.id}">+</button>
      </div>
      <div>
        <input maxlength="50" placeholder="Observação (máx. 50)" value="${escapar(i.observacao)}"
               data-acao="obs" data-id="${i.id}">
        <small class="contador-obs" data-contador="${i.id}">${i.observacao.length}/50</small>
      </div>
      <div>${money(i.preco * i.quantidade)}</div>
      <button class="btn-secondary" data-acao="remover" data-id="${i.id}">🗑 Remover</button>
    </div>
  `).join("") + `<div class="total">Subtotal: ${money(subtotal())}</div>`;

  container.querySelectorAll("button[data-acao]").forEach(btn => {
    btn.addEventListener("click", () => {
      const id = Number(btn.dataset.id);
      if (btn.dataset.acao === "mais") alterarQuantidade(id, 1);
      if (btn.dataset.acao === "menos") alterarQuantidade(id, -1);
      if (btn.dataset.acao === "remover") removerItem(id);
      renderizarCarrinho(containerId);
    });
  });
  container.querySelectorAll("input[data-acao='obs']").forEach(input => {
    input.addEventListener("input", () => {
      const id = Number(input.dataset.id);
      definirObservacao(id, input.value);
      const contador = container.querySelector(`[data-contador="${id}"]`);
      if (contador) contador.textContent = input.value.length + "/50";
    });
  });
}

document.addEventListener("DOMContentLoaded", atualizarBadge);
