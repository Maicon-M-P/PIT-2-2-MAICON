# Evidências das melhorias — Situação 3 (PIT 2)

Cinco melhorias simples implementadas no front-end a partir das sugestões dos colegas que testaram a solução. Os trechos `antes/depois` abaixo foram extraídos de `git diff -- frontend/`.

| # | Melhoria | Arquivo(s) | Status |
|---|---|---|---|
| 1 | Campo de busca por nome na vitrine | `frontend/index.html`, `frontend/js/vitrine.js` | Corrigido |
| 2 | Confirmação antes de remover item do carrinho | `frontend/js/carrinho.js` | Corrigido |
| 3 | Aviso de CEP incompleto no checkout | `frontend/js/checkout.js` | Corrigido |
| 4 | Contador de caracteres (0/50) na observação | `frontend/js/carrinho.js`, `frontend/css/style.css` | Corrigido |
| 5 | Validação do WhatsApp com DDD | `frontend/js/checkout.js` | Corrigido |

## Resumo antes → depois

1. **Busca na vitrine** — antes, a vitrine só tinha o seletor "Ordenar por" e não havia como localizar um cupcake pelo nome. Depois, há um campo `type="search"` que filtra a lista pelo nome (sem recarregar e sem alterar o back-end), com mensagem "Nenhum cupcake encontrado para ..." quando não há resultado.
2. **Confirmação ao remover** — antes, `removerItem()` excluía o item na hora. Depois, `confirm("Tem certeza que deseja remover este item do carrinho?")` impede exclusões acidentais.
3. **CEP incompleto** — antes, um CEP com menos de 8 dígitos era enviado à API e retornava uma mensagem genérica. Depois, o checkout valida localmente e exibe "Digite os 8 números do CEP." sem chamar a API.
4. **Contador da observação** — antes, o campo de observação limitava a 50 caracteres, mas não mostrava quantos haviam sido digitados. Depois, um `<small class="contador-obs">` mostra `0/50` e atualiza a cada tecla.
5. **WhatsApp** — antes, o campo aceitava qualquer texto. Depois, o submit valida 10 ou 11 dígitos (com DDD) e exibe "Digite o WhatsApp com DDD (10 ou 11 números)."

## Diferenças de código (`git diff -- frontend/`)

```diff
diff --git a/frontend/css/style.css b/frontend/css/style.css
index d284bb7..92ecea8 100644
--- a/frontend/css/style.css
+++ b/frontend/css/style.css
@@ -91,6 +91,7 @@ th { background: #fce6ef; }
   flex-wrap: wrap;
 }
 .badge { background: white; color: var(--rosa-escuro); border-radius: 20px; padding: 2px 9px; }
+.contador-obs { font-size: 12px; color: #888; }
 .status { font-weight: bold; padding: 4px 8px; border-radius: 5px; background: #eee; }
 .status-pago { background: #d9f0dd; color: #176b2b; }
 .status-entregue { background: #d9e8f5; color: #1d5c8a; }
diff --git a/frontend/index.html b/frontend/index.html
index dc8ba88..c775335 100644
--- a/frontend/index.html
+++ b/frontend/index.html
@@ -25,6 +25,8 @@
         <option value="">Padrão</option>
         <option value="preco_asc">Mais baratos primeiro</option>
       </select>
+      <label for="busca">Buscar cupcake pelo nome:</label>
+      <input id="busca" type="search" placeholder="Ex.: chocolate">
     </div>
     <div id="grid-produtos" class="grid" style="margin-top:16px"></div>
 
diff --git a/frontend/js/carrinho.js b/frontend/js/carrinho.js
index 3ae5ee0..960aca0 100644
--- a/frontend/js/carrinho.js
+++ b/frontend/js/carrinho.js
@@ -42,6 +42,7 @@ function alterarQuantidade(id, delta) {
 }
 
 function removerItem(id) {
+  if (!confirm("Tem certeza que deseja remover este item do carrinho?")) return;
   salvarCarrinho(lerCarrinho().filter(i => i.id !== id));
 }
 
@@ -81,6 +82,7 @@ function renderizarCarrinho(containerId) {
       <div>
         <input maxlength="50" placeholder="Observação (máx. 50)" value="${escapar(i.observacao)}"
                data-acao="obs" data-id="${i.id}">
+        <small class="contador-obs" data-contador="${i.id}">${i.observacao.length}/50</small>
       </div>
       <div>${money(i.preco * i.quantidade)}</div>
       <button class="btn-secondary" data-acao="remover" data-id="${i.id}">🗑 Remover</button>
@@ -97,7 +99,12 @@ function renderizarCarrinho(containerId) {
     });
   });
   container.querySelectorAll("input[data-acao='obs']").forEach(input => {
-    input.addEventListener("input", () => definirObservacao(Number(input.dataset.id), input.value));
+    input.addEventListener("input", () => {
+      const id = Number(input.dataset.id);
+      definirObservacao(id, input.value);
+      const contador = container.querySelector(`[data-contador="${id}"]`);
+      if (contador) contador.textContent = input.value.length + "/50";
+    });
   });
 }
 
diff --git a/frontend/js/checkout.js b/frontend/js/checkout.js
index 905754a..6e23f18 100644
--- a/frontend/js/checkout.js
+++ b/frontend/js/checkout.js
@@ -13,6 +13,11 @@ document.addEventListener("DOMContentLoaded", async () => {
   document.getElementById("btn-calcular").addEventListener("click", async () => {
     const cep = document.getElementById("cep").value.replace(/\D/g, "");
     const saida = document.getElementById("resultado-frete");
+    if (cep.length !== 8) {
+      saida.className = "mensagem erro";
+      saida.textContent = "Digite os 8 números do CEP.";
+      return;
+    }
     try {
       const dados = await api.get("/frete/" + cep);
       freteCalculado = dados;
@@ -32,6 +37,12 @@ document.addEventListener("DOMContentLoaded", async () => {
   document.getElementById("form-checkout").addEventListener("submit", async (event) => {
     event.preventDefault();
     const saida = document.getElementById("resultado-pedido");
+    const whatsapp = document.getElementById("cliente-whatsapp").value.replace(/\D/g, "");
+    if (whatsapp.length < 10 || whatsapp.length > 11) {
+      saida.className = "mensagem erro";
+      saida.textContent = "Digite o WhatsApp com DDD (10 ou 11 números).";
+      return;
+    }
     if (!freteCalculado) {
       saida.className = "mensagem erro";
       saida.textContent = "Calcule o frete antes de finalizar.";
diff --git a/frontend/js/vitrine.js b/frontend/js/vitrine.js
index fcfa5f2..845bb55 100644
--- a/frontend/js/vitrine.js
+++ b/frontend/js/vitrine.js
@@ -1,15 +1,21 @@
 /* Vitrine: listagem, ordenação sem recarregar e adicionar ao carrinho. */
-async function carregarProdutos(ordenar) {
+async function carregarProdutos(ordenar, busca = "") {
   const Grid = document.getElementById("grid-produtos");
   if (!Grid) return;
   Grid.innerHTML = "<p>Carregando...</p>";
   try {
     const produtos = await api.get("/produtos" + (ordenar ? "?ordenar=" + ordenar : ""));
-    if (produtos.length === 0) {
-      Grid.innerHTML = "<p>Nenhum cupcake disponível no momento.</p>";
+    const termo = busca.trim().toLowerCase();
+    const visiveis = termo
+      ? produtos.filter(p => String(p.nome || "").toLowerCase().includes(termo))
+      : produtos;
+    if (visiveis.length === 0) {
+      Grid.innerHTML = termo
+        ? `<p>Nenhum cupcake encontrado para "${escapar(busca)}".</p>`
+        : "<p>Nenhum cupcake disponível no momento.</p>";
       return;
     }
-    Grid.innerHTML = produtos.map(p => `
+    Grid.innerHTML = visiveis.map(p => `
       <div class="card produto">
         <img src="${escapar(p.imagem_url || '')}" alt="${escapar(p.nome)}"
              onerror="this.style.display='none'">
@@ -36,9 +42,10 @@ async function carregarProdutos(ordenar) {
 
 document.addEventListener("DOMContentLoaded", () => {
   const select = document.getElementById("ordenar");
-  carregarProdutos(select ? select.value : "");
-  if (select) {
-    select.addEventListener("change", () => carregarProdutos(select.value));
-  }
+  const busca = document.getElementById("busca");
+  const recarregar = () => carregarProdutos(select ? select.value : "", busca ? busca.value : "");
+  recarregar();
+  if (select) select.addEventListener("change", recarregar);
+  if (busca) busca.addEventListener("input", recarregar);
   renderizarCarrinho("carrinho-resumo");
 });

```
