"""Rotas públicas da vitrine e do detalhe do produto."""
from flask import Blueprint, jsonify, request

from models import avaliacao_model, produto_model

bp = Blueprint("produtos", __name__, url_prefix="/api/produtos")


@bp.get("")
@bp.get("/")
def listar_produtos():
    ordenar = request.args.get("ordenar")
    produtos = produto_model.listar(ordenar)
    return jsonify(produtos), 200


@bp.get("/<int:produto_id>")
def detalhes_produto(produto_id):
    produtos = produto_model.buscar_por_id(produto_id)
    if not produtos:
        return jsonify({"erro": "Produto não encontrado"}), 404

    produto = produtos[0]
    avaliacoes = avaliacao_model.listar_por_produto(produto_id)
    return jsonify({
        "produto": produto,
        "acompanhamentos": produto_model.listar_acompanhamentos(),
        "media_notas": produto_model.media_notas(produto_id),
        "avaliacoes": avaliacoes,
    }), 200
