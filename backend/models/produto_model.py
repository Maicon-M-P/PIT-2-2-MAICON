"""Acesso aos dados dos produtos e upload de imagens."""
from config import Config
from models import database


def listar(ordenar=None):
    sql = "SELECT * FROM produtos WHERE estoque > 0"
    if ordenar == "preco_asc":
        sql += " ORDER BY preco ASC, nome ASC"
    else:
        sql += " ORDER BY id ASC"
    return database.consultar(sql)


def listar_admin():
    """Lista todos os produtos, inclusive com estoque zerado."""
    return database.consultar("SELECT * FROM produtos ORDER BY id")


def buscar_por_id(produto_id):
    return database.consultar("SELECT * FROM produtos WHERE id = %s", (produto_id,))


def listar_acompanhamentos():
    return database.consultar(
        "SELECT * FROM produtos WHERE is_acompanhamento = TRUE AND estoque > 0 ORDER BY nome"
    )


def buscar_por_ids(ids):
    if not ids:
        return []
    return database.consultar("SELECT * FROM produtos WHERE id = ANY(%s)", (list(ids),))


def criar(dados, imagem_url=None):
    sql = """
        INSERT INTO produtos
            (nome, descricao, ingredientes, peso_gramas, preco, estoque,
             is_acompanhamento, imagem_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *
    """
    params = (
        dados.get("nome"),
        dados.get("descricao"),
        dados.get("ingredientes"),
        dados.get("peso_gramas"),
        dados.get("preco"),
        dados.get("estoque", 0),
        bool(dados.get("is_acompanhamento", False)),
        imagem_url,
    )
    return database.executar(sql, params)


def atualizar(produto_id, dados, imagem_url=None):
    """Se imagem_url for None, o COALESCE preserva a imagem já cadastrada."""
    sql = """
        UPDATE produtos SET
            nome = %s, descricao = %s, ingredientes = %s, peso_gramas = %s,
            preco = %s, estoque = %s, is_acompanhamento = %s,
            imagem_url = COALESCE(%s, imagem_url)
        WHERE id = %s
        RETURNING *
    """
    params = (
        dados.get("nome"),
        dados.get("descricao"),
        dados.get("ingredientes"),
        dados.get("peso_gramas"),
        dados.get("preco"),
        dados.get("estoque", 0),
        bool(dados.get("is_acompanhamento", False)),
        imagem_url,
        produto_id,
    )
    return database.executar(sql, params)


def excluir(produto_id):
    return database.executar("DELETE FROM produtos WHERE id = %s", (produto_id,))


def inativar(produto_id):
    """Inativa sem apagar: estoque 0 esconde o produto da vitrine."""
    return database.executar(
        "UPDATE produtos SET estoque = 0 WHERE id = %s RETURNING *", (produto_id,)
    )


def verificar_estoque(produto_id):
    linhas = database.consultar("SELECT estoque FROM produtos WHERE id = %s", (produto_id,))
    return linhas[0]["estoque"] if linhas else 0


def baixar_estoque(produto_id, quantidade):
    return database.executar(
        "UPDATE produtos SET estoque = estoque - %s "
        "WHERE id = %s AND estoque >= %s",
        (quantidade, produto_id, quantidade),
    )


def media_notas(produto_id):
    linhas = database.consultar(
        "SELECT ROUND(AVG(nota)::numeric, 1) AS media, COUNT(*) AS total "
        "FROM avaliacoes WHERE produto_id = %s",
        (produto_id,),
    )
    return linhas[0] if linhas else {"media": None, "total": 0}


def upload_imagem(arquivo):
    """Envia o arquivo para o bucket público e devolve a URL pública.

    A service_role fica apenas no back-end (variável de ambiente do Railway).
    """
    from supabase import create_client

    cliente = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    nome_arquivo = arquivo.filename.replace(" ", "_")
    cliente.storage.from_(Config.BUCKET_IMAGENS).upload(
        nome_arquivo, arquivo.read(), {"content-type": arquivo.mimetype, "upsert": "true"}
    )
    return cliente.storage.from_(Config.BUCKET_IMAGENS).get_public_url(nome_arquivo)
