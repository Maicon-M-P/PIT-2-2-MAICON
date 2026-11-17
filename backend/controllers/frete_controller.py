"""Rotas e regras do cálculo de frete (ViaCEP + IBGE da loja)."""
from flask import Blueprint, jsonify

from config import Config
from models import config_model

bp = Blueprint("frete", __name__, url_prefix="/api")


def validar_cep(cep):
    """Devolve (endereco, None) se atendido ou (None, mensagem) se não atendido."""
    endereco = config_model.consultar_viacep(cep)
    if endereco is None:
        return None, "Cidade não atendida"

    if endereco.get("ibge") != config_model.buscar_ibge_loja():
        return None, "Cidade não atendida"

    return endereco, None


@bp.get("/frete/<cep>")
def calcular_frete(cep):
    endereco, erro = validar_cep(cep)
    if erro:
        return jsonify({"erro": erro}), 400
    return jsonify({
        "cep": endereco.get("cep"),
        "logradouro": endereco.get("logradouro"),
        "bairro": endereco.get("bairro"),
        "cidade": endereco.get("localidade"),
        "frete": Config.FRETE_FIXO,
    }), 200
