/* URL base da API. Troque pelo endereço do back-end no Railway ao fazer o deploy. */
const API_URL = "https://pit-2-2-maicon-production.up.railway.app";

function tokenAdmin() {
  return localStorage.getItem("adminToken") || "";
}

async function request(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (options.auth) headers["Authorization"] = "Bearer " + tokenAdmin();

  const config = {
    method: options.method || "GET",
    headers,
  };
  if (options.body !== undefined) config.body = JSON.stringify(options.body);

  const resposta = await fetch(API_URL + path, config);
  let dados;
  try { dados = await resposta.json(); } catch (e) { dados = { erro: "Resposta inválida da API" }; }
  if (!resposta.ok) throw new Error(dados.erro || "Erro na requisição");
  return dados;
}

const api = {
  get: (path, auth = false) => request(path, { auth }),
  post: (path, body, auth = false) => request(path, { method: "POST", body, auth }),
  put: (path, body, auth = false) => request(path, { method: "PUT", body, auth }),
  patch: (path, body, auth = false) => request(path, { method: "PATCH", body, auth }),
  del: (path, auth = false) => request(path, { method: "DELETE", auth }),
};

function money(valor) {
  return "R$ " + Number(valor).toFixed(2).replace(".", ",");
}

function escapar(texto) {
  return String(texto == null ? "" : texto)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}
