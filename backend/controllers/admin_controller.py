"""Rotas administrativas protegidas por token e configurações da loja."""
from functools import wraps

from flask import Blueprint, jsonify, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from config import Config
from models import config_model, pedido_model, produto_model

bp = Blueprint("admin", __name__, url_prefix="/api")

serializador = URLSafeTimedSerializer(Config.SECRET_KEY)


def gerar_token():
    return serializador.dumps({"usuario": Config.ADMIN_USER})


def verificar_token(token):
    try:
        dados = serializador.loads(token, max_age=86400)
        return dados.get("usuario") == Config.ADMIN_USER
    except (BadSignature, SignatureExpired):
        return False


def admin_required(funcao):
    @wraps(funcao)
    def decorada(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        token = header.replace("Bearer ", "").strip()
        if not token or not verificar_token(token):
            return jsonify({"erro": "Não autorizado"}), 401
        return funcao(*args, **kwargs)
    return decorada


def dados_produto():
    """Lê os campos do formulário (multipart/form-data)."""
    return {
        "nome": request.form.get("nome"),
        "descricao": request.form.get("descricao"),
        "ingredientes": request.form.get("ingredientes"),
        "peso_gramas": request.form.get("peso_gramas") or None,
        "preco": request.form.get("preco"),
        "estoque": request.form.get("estoque", 0),
        "is_acompanhamento": request.form.get("is_acompanhamento") in ("true", "1", "on"),
    }


def validar_produto(dados):
    try:
        preco = float(dados["preco"])
        estoque = int(dados["estoque"])
    except (TypeError, ValueError):
        return None, "Preço e estoque devem ser números"
    if preco <= 0:
        return None, "Preço deve ser maior que zero"
    if estoque < 0:
        return None, "Estoque não pode ser negativo"
    return (preco, estoque), None


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------
@bp.post("/admin/login")
def login():
    dados = request.get_json(silent=True) or request.form
    if (dados.get("usuario") == Config.ADMIN_USER and
            dados.get("senha") == Config.ADMIN_PASSWORD):
        return jsonify({"token": gerar_token()}), 200
    return jsonify({"erro": "Usuário ou senha inválidos"}), 401


# ---------------------------------------------------------------------------
# Configurações da loja
# ---------------------------------------------------------------------------
@bp.get("/loja/config")
def config_publica():
    linhas = config_model.buscar_config()
    if not linhas:
        return jsonify({"erro": "Configuração da loja não encontrada"}), 404
    config = linhas[0]
    endereco = config_model.consultar_viacep(config["cep_loja"])
    return jsonify({
        "chave_pix": config["chave_pix"],
        "whatsapp": config["whatsapp"],
        "cidade_atendida": endereco.get("localidade") if endereco else None,
    }), 200


@bp.get("/admin/config")
@admin_required
def get_config():
    linhas = config_model.buscar_config()
    return jsonify(linhas[0] if linhas else {}), 200


@bp.put("/admin/config")
@admin_required
def put_config():
    dados = request.get_json(silent=True) or {}
    cep_loja = dados.get("cep_loja")
    ibge = dados.get("codigo_ibge_loja")

    if cep_loja:
        endereco = config_model.consultar_viacep(cep_loja)
        if endereco is None:
            return jsonify({"erro": "CEP inválido"}), 400
        ibge = endereco.get("ibge")

    config = config_model.atualizar_config(
        dados.get("chave_pix"), dados.get("whatsapp"), cep_loja, ibge
    )
    return jsonify(config), 200


# ---------------------------------------------------------------------------
# Produtos
# ---------------------------------------------------------------------------
@bp.get("/admin/produtos")
@admin_required
def listar_produtos_admin():
    return jsonify(produto_model.listar_admin()), 200


@bp.post("/admin/produtos")
@admin_required
def criar_produto():
    dados = dados_produto()
    valores, erro = validar_produto(dados)
    if erro:
        return jsonify({"erro": erro}), 400
    dados["preco"], dados["estoque"] = valores

    imagem_url = None
    if "imagem" in request.files and request.files["imagem"].filename:
        imagem_url = produto_model.upload_imagem(request.files["imagem"])

    produto = produto_model.criar(dados, imagem_url)
    return jsonify(produto), 201


@bp.put("/admin/produtos/<int:produto_id>")
@admin_required
def editar_produto(produto_id):
    dados = dados_produto()
    valores, erro = validar_produto(dados)
    if erro:
        return jsonify({"erro": erro}), 400
    dados["preco"], dados["estoque"] = valores

    imagem_url = None
    if "imagem" in request.files and request.files["imagem"].filename:
        imagem_url = produto_model.upload_imagem(request.files["imagem"])

    produto = produto_model.atualizar(produto_id, dados, imagem_url)
    if produto is None:
        return jsonify({"erro": "Produto não encontrado"}), 404
    return jsonify(produto), 200


@bp.delete("/admin/produtos/<int:produto_id>")
@admin_required
def remover_produto(produto_id):
    produto = produto_model.inativar(produto_id)
    if produto is None:
        return jsonify({"erro": "Produto não encontrado"}), 404
    return jsonify({"mensagem": "Produto inativado"}), 200


# ---------------------------------------------------------------------------
# Pedidos
# ---------------------------------------------------------------------------
@bp.get("/admin/pedidos")
@admin_required
def listar_pedidos_admin():
    pedidos = pedido_model.listar_todos()
    return jsonify(pedidos), 200


@bp.patch("/admin/pedidos/<int:pedido_id>/status")
@admin_required
def alterar_status(pedido_id):
    dados = request.get_json(silent=True) or {}
    status = dados.get("status")

    if status not in Config.STATUS_PEDIDO:
        return jsonify({"erro": "Status inválido"}), 400

    if status == "Pago / Em Preparo":
        itens = pedido_model.itens_do_pedido(pedido_id)
        for item in itens:
            if produto_model.verificar_estoque(item["produto_id"]) < item["quantidade"]:
                return jsonify({"erro": "Estoque insuficiente"}), 400
        for item in itens:
            produto_model.baixar_estoque(item["produto_id"], item["quantidade"])

    pedido = pedido_model.atualizar_status(pedido_id, status)
    if pedido is None:
        return jsonify({"erro": "Pedido não encontrado"}), 404
    return jsonify(pedido), 200
