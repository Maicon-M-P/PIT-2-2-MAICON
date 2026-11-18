# Loja de Cupcakes — PIT 2 (Engenharia de Software II)

Projeto de venda de cupcakes gourmet com vitrine, carrinho,
checkout com frete via ViaCEP, pagamento PIX estático + WhatsApp,
acompanhamento de pedido e painel administrativo.

## Arquitetura

| Camada | Tecnologia | Onde roda |
|---|---|---|
| View (front-end) | HTML5, CSS3, JavaScript puro (`fetch`) | Vercel |
| Controller/Model (back-end) | Python + Flask (MVC, REST API em JSON) | Railway (Gunicorn) |
| Banco de dados | PostgreSQL | Supabase |
| Arquivos (fotos) | Supabase Storage (bucket `cupcakes-imagens`) | Supabase |

## Estrutura do repositório

```
.
├── .gitignore / .env.example
├── backend/                 # API Flask (MVC)
│   ├── app.py               # ponto de entrada + CORS
│   ├── config.py            # variáveis de ambiente
│   ├── Procfile             # gunicorn app:app (Railway)
│   ├── models/              # acesso ao PostgreSQL e Storage
│   ├── controllers/         # Blueprints com as rotas REST
│   ├── tests/               # testes pytest (Situação 3)
│   └── requirements.txt
├── frontend/                # site estático (Vercel)
│   ├── index.html, produto.html, checkout.html,
│   │   acompanhar.html, admin.html
│   └── css/ e js/
├── documentacao/
│   ├── situacao_1/          # escopo revisado, UML e banco de dados
│   ├── situacao_2/          # arquitetura, API e manual de uso
│   └── situacao_3/          # testes, formulário e laudo
├── evidencias/              # provas do trabalho (prints, logs)
├── videos/                  # roteiro + link do vídeo
└── relatório PIT 2.docx
```

## Como rodar localmente

1. Copie `.env.example` para `.env` e preencha as variáveis.
2. No Supabase, execute `documentacao/situacao_1/banco_dados/DDL.sql` no SQL Editor.
3. Back-end:

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python app.py
```

4. Front-end: abra `frontend/index.html` (ou sirva a pasta com `python -m http.server`).
   Ajuste `API_URL` em `frontend/js/api.js` se necessário.

## Como rodar os testes

```bash
python3 -m pytest backend/tests/test_api.py -v
```

Os testes usam `test_client()` e mocks, rodam offline e não sujam o banco de produção.
Log salvo em `evidencias/testes_automatizados.log`.

## Escopo implementado

IDs 1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 15 e 16.
Removidos: 4, 12, 13 e 14.
Mensagem padronizada de frete: **"Cidade não atendida"**.
