"""Rotas públicas de criação e acompanhamento de pedidos."""
import re

from flask import Blueprint, jsonify, request

from config import Config
from controllers import frete_controller
from models import config_model, pedido_model, produto_model

bp = Blueprint("pedidos", __name__, url_prefix="/api/pedidos")


def higienizar(texto):
    """Remove caracteres especiais e limita a 50 caracteres."""
    limpo = re.sub(r"[^A-Za-zÀ-ÿ0-9 ,.\-]", "", str(texto or ""))
    return limpo[:50].strip()


@bp.post("")
@bp.post("/")
def criar_pedido():
    dados = request.get_json(silent=True) or {}

    endereco, erro = frete_controller.validar_cep(dados.get("cep", ""))
    if erro:
        return jsonify({"erro": erro}), 400

    itens_enviados = dados.get("itens", [])
    if not itens_enviados:
        return jsonify({"erro": "Carrinho vazio"}), 400

    produtos = {
        p["id"]: p
        for p in produto_model.buscar_por_ids([i["produto_id"] for i in itens_enviados])
    }

    valor_produtos = 0.0
    itens_validados = []
    for item in itens_enviados:
        produto = produtos.get(item["produto_id"])
        if produto is None:
            return jsonify({"erro": "Produto não encontrado"}), 400

        quantidade = int(item["quantidade"])
        if quantidade <= 0 or quantidade > produto["estoque"]:
            return jsonify({"erro": "Estoque insuficiente"}), 400

        preco_unitario = float(produto["preco"])
        subtotal = round(preco_unitario * quantidade, 2)
        valor_produtos += subtotal
        itens_validados.append({
            "produto_id": produto["id"],
            "quantidade": quantidade,
            "preco_unitario": preco_unitario,
            "observacao": higienizar(item.get("observacao", "")),
        })

    valor_produtos = round(valor_produtos, 2)
    valor_total = round(valor_produtos + Config.FRETE_FIXO, 2)

    pedido = {
        "numero_pedido": pedido_model.gerar_numero_pedido(),
        "cliente_nome": dados.get("cliente_nome"),
        "cliente_whatsapp": dados.get("cliente_whatsapp"),
        "cep": dados.get("cep"),
        "endereco_rua": endereco.get("logradouro"),
        "endereco_numero": dados.get("endereco_numero"),
        "endereco_complemento": dados.get("endereco_complemento"),
        "endereco_bairro": endereco.get("bairro"),
        "endereco_cidade": endereco.get("localidade"),
        "valor_produtos": valor_produtos,
        "valor_frete": Config.FRETE_FIXO,
        "valor_total": valor_total,
        "status": "Aguardando Pagamento",
        "itens": itens_validados,
    }
    pedido_salvo = pedido_model.criar(pedido)

    config = config_model.buscar_config()
    config = config[0] if config else {}
    return jsonify({
        "numero_pedido": pedido_salvo["numero_pedido"],
        "valor_total": valor_total,
        "status": "Aguardando Pagamento",
        "chave_pix": config.get("chave_pix"),
        "whatsapp": config.get("whatsapp"),
    }), 201


@bp.get("/<numero_pedido>")
def acompanhar_pedido(numero_pedido):
    pedidos = pedido_model.buscar_por_numero(numero_pedido)
    if not pedidos:
        return jsonify({"erro": "Pedido não encontrado"}), 404

    pedido = pedidos[0]
    resposta = {
        "numero_pedido": pedido["numero_pedido"],
        "status": pedido["status"],
        "valor_total": float(pedido["valor_total"]),
        "itens": pedido_model.itens_do_pedido(pedido["id"]),
    }

    if pedido["status"] == "Aguardando Pagamento":
        config = config_model.buscar_config()
        config = config[0] if config else {}
        resposta["mensagem"] = "Enviar comprovante para o número WhatsApp"
        resposta["whatsapp"] = config.get("whatsapp")
        resposta["chave_pix"] = config.get("chave_pix")

    return jsonify(resposta), 200
