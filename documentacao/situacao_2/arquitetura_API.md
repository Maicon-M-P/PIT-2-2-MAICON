# Arquitetura e API — Situação 2

## Arquitetura (MVC + REST)

- **View**: HTML/CSS/JS puro consumindo a API via `fetch()`.
- **Controller**: Blueprints Flask com as regras de negócio (`backend/controllers/`).
- **Model**: acesso ao PostgreSQL e ao Supabase Storage (`backend/models/`).
- **Banco**: PostgreSQL + Storage no Supabase.
- **CORS**: `flask-cors` liberando Vercel + localhost, métodos GET/POST/PUT/PATCH/DELETE e header `Authorization`.

## Endpoints

### Públicas

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/produtos?ordenar=preco_asc` | Lista produtos com estoque > 0 |
| GET | `/api/produtos/<id>` | Detalhes, acompanhamentos, média e avaliações |
| GET | `/api/frete/<cep>` | ViaCEP + IBGE → endereço + frete 20,00 ou "Cidade não atendida" |
| GET | `/api/loja/config` | Chave PIX, WhatsApp e cidade atendida |
| POST | `/api/pedidos` | Recalcula valores, cria pedido "Aguardando Pagamento" |
| GET | `/api/pedidos/<numero_pedido>` | Status, itens, total e, se aguardando, PIX + WhatsApp |
| POST | `/api/avaliacoes` | Avaliação validada por pedido "Entregue" |
| GET | `/api/health` | Verificação de saúde da API |

### Administrativas (header `Authorization: Bearer <token>`)

| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/admin/login` | Usuário/senha do `.env` → token |
| GET/PUT | `/api/admin/config` | Lê/atualiza PIX, WhatsApp, CEP/IBGE (ViaCEP atualiza o IBGE) |
| GET | `/api/admin/produtos` | Todos os produtos, inclusive estoque 0 |
| POST/PUT | `/api/admin/produtos[/<id>]` | Cria/edita com upload (foto opcional no PUT) |
| DELETE | `/api/admin/produtos/<id>` | Inativa (estoque = 0) |
| GET | `/api/admin/pedidos` | Todos os pedidos |
| PATCH | `/api/admin/pedidos/<id>/status` | Muda status; baixa estoque ao virar "Pago / Em Preparo" |

## Decisões de implementação

- **Token**: assinado com `itsdangerous` (já vem com Flask) usando `SECRET_KEY`; não foi adicionado JWT porque o `requirements.txt` do planejamento não prevê `PyJWT`.
- **Inativação**: como não há coluna `ativo`, inativar = `estoque = 0` (a vitrine já filtra `estoque > 0`).
- **Upload**: `service_role` fica só no back-end (variável de ambiente); no PUT, `COALESCE(%s, imagem_url)` preserva a foto atual se nenhum arquivo for enviado.
- **Root Directory no Railway**: `backend/` (para `gunicorn app:app` do Procfile funcionar).
