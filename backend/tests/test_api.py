"""
Testes automatizados da API real - PIT 2 / Situação 3
=====================================================
Usa o app.test_client() do Flask com unittest.mock para simular as queries do
banco e as chamadas ao ViaCEP. Assim os testes rodam rápido, offline e sem
sujar o PostgreSQL de produção.

Executar: python3 -m pytest backend/tests/test_api.py -v
"""
import importlib

import pytest
from app import create_app

# Módulos reais (para aplicar os mocks nos lugares certos)
pedido_model = importlib.import_module("models.pedido_model")
produto_model = importlib.import_module("models.produto_model")
config_model = importlib.import_module("models.config_model")
avaliacao_model = importlib.import_module("models.avaliacao_model")
admin_controller = importlib.import_module("controllers.admin_controller")


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as cliente:
        yield cliente


@pytest.fixture
def token():
    return admin_controller.gerar_token()


# ---------------------------------------------------------------------------
# Frete (ViaCEP + IBGE da loja)
# ---------------------------------------------------------------------------
def test_frete_cidade_atendida(client):
    """CEP com IBGE igual ao da loja retorna endereço e frete R$ 20,00."""
    with pytest.MonkeyPatch.context() as m:
        m.setattr(config_model, "consultar_viacep", lambda cep: {
            "cep": cep, "logradouro": "Rua Teste", "bairro": "Centro",
            "localidade": "Araucária", "ibge": "4101804",
        })
        m.setattr(config_model, "buscar_ibge_loja", lambda: "4101804")
        resposta = client.get("/api/frete/83702000")

    assert resposta.status_code == 200
    dados = resposta.get_json()
    assert dados["frete"] == 20.00
    assert dados["cidade"] == "Araucária"


def test_frete_outra_cidade(client):
    """IBGE diferente retorna a mensagem padronizada 'Cidade não atendida'."""
    with pytest.MonkeyPatch.context() as m:
        m.setattr(config_model, "consultar_viacep", lambda cep: {
            "cep": cep, "localidade": "Curitiba", "ibge": "4106902",
        })
        m.setattr(config_model, "buscar_ibge_loja", lambda: "4101804")
        resposta = client.get("/api/frete/80000000")

    assert resposta.status_code == 400
    assert resposta.get_json()["erro"] == "Cidade não atendida"


# ---------------------------------------------------------------------------
# Produtos
# ---------------------------------------------------------------------------
def test_preco_negativo_no_cadastro(client, token):
    """O administrador não consegue cadastrar produto com preço negativo."""
    with pytest.MonkeyPatch.context() as m:
        m.setattr(produto_model, "criar", lambda dados, imagem: pytest.fail("Não deveria gravar"))
        resposta = client.post(
            "/api/admin/produtos",
            headers={"Authorization": "Bearer " + token},
            data={"nome": "Cupcake Teste", "preco": "-5", "estoque": "10",
                  "ingredientes": "Farinha, açúcar"},
        )

    assert resposta.status_code == 400
    assert "maior que zero" in resposta.get_json()["erro"]


# ---------------------------------------------------------------------------
# Pedidos
# ---------------------------------------------------------------------------
def test_pedido_recalcula_totais_no_servidor(client):
    """Preços do front são ignorados: totais vêm do banco e observação é higienizada."""
    produtos = [
        {"id": 1, "preco": 10.00, "estoque": 5, "nome": "Cupcake A"},
        {"id": 2, "preco": 7.50, "estoque": 3, "nome": "Cupcake B"},
    ]
    salvos = {}

    def fake_criar(pedido):
        salvos["pedido"] = pedido
        return {"id": 1, "numero_pedido": "CUP-1001"}

    with pytest.MonkeyPatch.context() as m:
        m.setattr(config_model, "consultar_viacep", lambda cep: {
            "cep": cep, "logradouro": "Rua Teste", "bairro": "Centro",
            "localidade": "Araucária", "ibge": "4101804",
        })
        m.setattr(config_model, "buscar_ibge_loja", lambda: "4101804")
        m.setattr(config_model, "buscar_config", lambda: [{
            "chave_pix": "11999999999", "whatsapp": "554199999999",
        }])
        m.setattr(produto_model, "buscar_por_ids", lambda ids: produtos)
        m.setattr(pedido_model, "gerar_numero_pedido", lambda: "CUP-1001")
        m.setattr(pedido_model, "criar", fake_criar)
        resposta = client.post("/api/pedidos", json={
            "cliente_nome": "Maria", "cliente_whatsapp": "5541998888888",
            "cep": "83702000", "endereco_numero": "100",
            "itens": [
                {"produto_id": 1, "quantidade": 2, "preco": 0.01,
                 "observacao": "sem <granulado>!"},
                {"produto_id": 2, "quantidade": 1, "preco": 0.01, "observacao": ""},
            ],
        })

    assert resposta.status_code == 201
    dados = resposta.get_json()
    assert dados["numero_pedido"] == "CUP-1001"
    assert dados["valor_total"] == 47.50  # 2*10 + 1*7,50 + 20

    pedido = salvos["pedido"]
    assert pedido["itens"][0]["preco_unitario"] == 10.00
    assert pedido["itens"][0]["observacao"] == "sem granulado"
    assert pedido["status"] == "Aguardando Pagamento"


def test_acompanhamento_aguardando_mostra_pix(client):
    """Pedido aguardando pagamento retorna a mensagem do WhatsApp e a chave PIX."""
    pedido = {
        "id": 1, "numero_pedido": "CUP-1001", "status": "Aguardando Pagamento",
        "valor_total": 47.50,
    }
    with pytest.MonkeyPatch.context() as m:
        m.setattr(pedido_model, "buscar_por_numero", lambda numero: [pedido])
        m.setattr(pedido_model, "itens_do_pedido", lambda pid: [])
        m.setattr(config_model, "buscar_config", lambda: [{
            "chave_pix": "11999999999", "whatsapp": "554199999999",
        }])
        resposta = client.get("/api/pedidos/CUP-1001")

    assert resposta.status_code == 200
    dados = resposta.get_json()
    assert dados["mensagem"] == "Enviar comprovante para o número WhatsApp"
    assert dados["chave_pix"] == "11999999999"


# ---------------------------------------------------------------------------
# Baixa de estoque
# ---------------------------------------------------------------------------
def test_baixa_estoque_ao_marcar_como_pago(client, token):
    """Estoque só é descontado ao mudar o status para 'Pago / Em Preparo'."""
    itens = [{"produto_id": 1, "quantidade": 2, "preco_unitario": 10.00}]
    baixas = []
    with pytest.MonkeyPatch.context() as m:
        m.setattr(pedido_model, "itens_do_pedido", lambda pid: itens)
        m.setattr(produto_model, "verificar_estoque", lambda pid: 5)
        m.setattr(produto_model, "baixar_estoque", lambda pid, qtd: baixas.append((pid, qtd)))
        m.setattr(pedido_model, "atualizar_status", lambda pid, status: {"id": pid, "status": status})
        resposta = client.patch(
            "/api/admin/pedidos/1/status",
            headers={"Authorization": "Bearer " + token},
            json={"status": "Pago / Em Preparo"},
        )

    assert resposta.status_code == 200
    assert baixas == [(1, 2)]


def test_sem_baixa_estoque_em_outro_status(client, token):
    """Mudar para 'Saiu para Entrega' não desconta estoque."""
    with pytest.MonkeyPatch.context() as m:
        m.setattr(pedido_model, "itens_do_pedido", lambda pid: pytest.fail("Não deve buscar itens"))
        m.setattr(pedido_model, "atualizar_status", lambda pid, status: {"id": pid, "status": status})
        resposta = client.patch(
            "/api/admin/pedidos/1/status",
            headers={"Authorization": "Bearer " + token},
            json={"status": "Saiu para Entrega"},
        )

    assert resposta.status_code == 200


# ---------------------------------------------------------------------------
# Avaliação por número do pedido
# ---------------------------------------------------------------------------
def test_avaliacao_so_com_pedido_entregue(client):
    """Pedido não entregue não pode ser avaliado."""
    with pytest.MonkeyPatch.context() as m:
        m.setattr(pedido_model, "buscar_por_numero", lambda numero: [{
            "id": 1, "status": "Aguardando Pagamento",
        }])
        resposta = client.post("/api/avaliacoes", json={
            "numero_pedido": "CUP-1001", "produto_id": 1, "nota": 5,
        })

    assert resposta.status_code == 400
    assert resposta.get_json()["erro"] == "Pedido ainda não foi entregue"


def test_avaliacao_pedido_entregue(client):
    """Pedido entregue, com o produto e sem avaliação anterior: avaliação salva."""
    with pytest.MonkeyPatch.context() as m:
        m.setattr(pedido_model, "buscar_por_numero", lambda numero: [{
            "id": 1, "status": "Entregue",
        }])
        m.setattr(pedido_model, "itens_do_pedido", lambda pid: [
            {"produto_id": 1, "quantidade": 1},
        ])
        m.setattr(avaliacao_model, "ja_avaliado", lambda pid, prod: False)
        m.setattr(avaliacao_model, "criar", lambda prod, pid, nota, comentario: {"id": 1})
        resposta = client.post("/api/avaliacoes", json={
            "numero_pedido": "CUP-1001", "produto_id": 1, "nota": 5,
            "comentario": "Delicioso!",
        })

    assert resposta.status_code == 201


# ---------------------------------------------------------------------------
# Segurança do painel administrativo
# ---------------------------------------------------------------------------
def test_admin_sem_token_e_bloqueado(client):
    """Rotas administrativas exigem token no header Authorization."""
    resposta = client.get("/api/admin/produtos")
    assert resposta.status_code == 401
