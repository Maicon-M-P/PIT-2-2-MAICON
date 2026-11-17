"""Rota pública de avaliação validada por número do pedido."""
from flask import Blueprint, jsonify, request

from models import avaliacao_model, pedido_model

bp = Blueprint("avaliacoes", __name__, url_prefix="/api/avaliacoes")


@bp.post("")
@bp.post("/")
def criar_avaliacao():
    dados = request.get_json(silent=True) or {}
    numero_pedido = dados.get("numero_pedido")
    produto_id = dados.get("produto_id")
    nota = dados.get("nota")

    try:
        nota = int(nota)
    except (TypeError, ValueError):
        return jsonify({"erro": "Nota deve ser um número de 1 a 5"}), 400

    if nota < 1 or nota > 5:
        return jsonify({"erro": "Nota deve ser de 1 a 5"}), 400

    pedidos = pedido_model.buscar_por_numero(numero_pedido)
    if not pedidos:
        return jsonify({"erro": "Pedido não encontrado"}), 404

    pedido = pedidos[0]
    if pedido["status"] != "Entregue":
        return jsonify({"erro": "Pedido ainda não foi entregue"}), 400

    itens = pedido_model.itens_do_pedido(pedido["id"])
    if not any(item["produto_id"] == produto_id for item in itens):
        return jsonify({"erro": "Produto não pertence ao pedido"}), 400

    if avaliacao_model.ja_avaliado(pedido["id"], produto_id):
        return jsonify({"erro": "Produto já avaliado neste pedido"}), 400

    avaliacao_model.criar(produto_id, pedido["id"], nota, dados.get("comentario", ""))
    return jsonify({"mensagem": "Avaliação registrada com sucesso"}), 201
