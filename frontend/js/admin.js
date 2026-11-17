/* Painel administrativo: login, produtos, pedidos e configurações da loja. */
function mostrar(id) { document.getElementById(id).classList.remove("hidden"); }
function esconder(id) { document.getElementById(id).classList.add("hidden"); }
function msg(id, texto, classe) {
  const el = document.getElementById(id);
  el.className = "mensagem " + classe;
  el.textContent = texto;
}

document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("adminToken");
  if (token) { mostrar("painel"); carregarTudo(); }

  document.getElementById("form-login").addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      const dados = await api.post("/admin/login", {
        usuario: document.getElementById("usuario").value,
        senha: document.getElementById("senha").value,
      });
      localStorage.setItem("adminToken", dados.token);
      esconder("login");
      mostrar("painel");
      carregarTudo();
    } catch (erro) {
      msg("msg-login", erro.message, "erro");
    }
  });

  document.getElementById("btn-sair").addEventListener("click", () => {
    localStorage.removeItem("adminToken");
    esconder("painel");
    mostrar("login");
  });

  document.getElementById("form-produto").addEventListener("submit", async (event) => {
    event.preventDefault();
    const id = document.getElementById("produto-id").value;
    const dados = new FormData();
    ["nome", "descricao", "ingredientes", "peso_gramas", "preco", "estoque"].forEach(campo => {
      dados.append(campo, document.getElementById(campo).value);
    });
    dados.append("is_acompanhamento", document.getElementById("is_acompanhamento").checked ? "true" : "false");
    const imagem = document.getElementById("imagem").files[0];
    if (imagem) dados.append("imagem", imagem);

    try {
      const resposta = await fetch(API_URL + (id ? "/admin/produtos/" + id : "/admin/produtos"), {
        method: id ? "PUT" : "POST",
        headers: { "Authorization": "Bearer " + localStorage.getItem("adminToken") },
        body: dados,
      });
      const resultado = await resposta.json();
      if (!resposta.ok) throw new Error(resultado.erro || "Erro ao salvar");
      msg("msg-produto", "Produto salvo com sucesso!", "sucesso");
      document.getElementById("form-produto").reset();
      document.getElementById("produto-id").value = "";
      carregarProdutosAdmin();
    } catch (erro) { msg("msg-produto", erro.message, "erro"); }
  });

  document.getElementById("form-config").addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      await api.put("/admin/config", {
        chave_pix: document.getElementById("chave-pix").value,
        whatsapp: document.getElementById("whatsapp").value,
        cep_loja: document.getElementById("cep-loja").value.replace(/\D/g, ""),
      }, true);
      msg("msg-config", "Configurações salvas!", "sucesso");
    } catch (erro) { msg("msg-config", erro.message, "erro"); }
  });
});

function carregarTudo() { carregarProdutosAdmin(); carregarPedidos(); carregarConfig(); }

async function carregarProdutosAdmin() {
  try {
    const produtos = await api.get("/admin/produtos", true);
    const tabela = document.getElementById("tabela-produtos");
    tabela.innerHTML = produtos.map(p => `
      <tr>
        <td>${p.id}</td><td>${escapar(p.nome)}</td><td>${money(p.preco)}</td><td>${p.estoque}</td>
        <td>${p.is_acompanhamento ? "Sim" : "Não"}</td>
        <td>
          <button onclick="editarProduto(${p.id})">Editar</button>
          <button class="btn-secondary" onclick="inativarProduto(${p.id})">Inativar</button>
        </td>
      </tr>`).join("");
    window._produtosAdmin = produtos;
  } catch (erro) { msg("msg-produto", erro.message, "erro"); }
}

function editarProduto(id) {
  const p = (window._produtosAdmin || []).find(x => x.id === id);
  if (!p) return;
  document.getElementById("produto-id").value = p.id;
  ["nome", "descricao", "ingredientes", "peso_gramas", "preco", "estoque"].forEach(campo => {
    document.getElementById(campo).value = p[campo] == null ? "" : p[campo];
  });
  document.getElementById("is_acompanhamento").checked = !!p.is_acompanhamento;
  document.getElementById("form-produto").scrollIntoView({ behavior: "smooth" });
}

async function inativarProduto(id) {
  if (!confirm("Inativar este produto?")) return;
  try { await api.del("/admin/produtos/" + id, true); carregarProdutosAdmin(); }
  catch (erro) { msg("msg-produto", erro.message, "erro"); }
}

const rotuloStatus = {
  "Aguardando Pagamento": "status-aguardando",
  "Pago / Em Preparo": "status-pago",
  "Saiu para Entrega": "status-pago",
  "Entregue": "status-entregue",
  "Cancelado": "",
};

async function carregarPedidos() {
  try {
    const pedidos = await api.get("/admin/pedidos", true);
    document.getElementById("tabela-pedidos").innerHTML = pedidos.map(p => `
      <tr>
        <td>${escapar(p.numero_pedido)}</td><td>${escapar(p.cliente_nome)}</td>
        <td>${money(p.valor_total)}</td>
        <td><span class="status ${rotuloStatus[p.status] || ''}">${escapar(p.status)}</span></td>
        <td>
          <select onchange="alterarStatus(${p.id}, this.value)">
            ${["Aguardando Pagamento", "Pago / Em Preparo", "Saiu para Entrega", "Entregue", "Cancelado"]
              .map(s => `<option ${s === p.status ? "selected" : ""}>${s}</option>`).join("")}
          </select>
        </td>
      </tr>`).join("");
  } catch (erro) { msg("msg-pedidos", erro.message, "erro"); }
}

async function alterarStatus(id, status) {
  try {
    await api.patch("/admin/pedidos/" + id + "/status", { status }, true);
    carregarPedidos();
    carregarProdutosAdmin();
  } catch (erro) { msg("msg-pedidos", erro.message, "erro"); }
}

async function carregarConfig() {
  try {
    const c = await api.get("/admin/config", true);
    document.getElementById("chave-pix").value = c.chave_pix || "";
    document.getElementById("whatsapp").value = c.whatsapp || "";
    document.getElementById("cep-loja").value = c.cep_loja || "";
  } catch (erro) { msg("msg-config", erro.message, "erro"); }
}
