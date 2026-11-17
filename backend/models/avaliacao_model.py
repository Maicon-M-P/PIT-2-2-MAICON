"""Acesso aos dados das avaliações."""
from models import database


def criar(produto_id, pedido_id, nota, comentario):
    return database.executar(
        """
        INSERT INTO avaliacoes (produto_id, pedido_id, nota, comentario)
        VALUES (%s, %s, %s, %s)
        RETURNING *
        """,
        (produto_id, pedido_id, nota, comentario),
    )


def listar_por_produto(produto_id):
    return database.consultar(
        """
        SELECT a.*, p.numero_pedido
        FROM avaliacoes a
        JOIN pedidos p ON p.id = a.pedido_id
        WHERE a.produto_id = %s
        ORDER BY a.criado_em DESC
        """,
        (produto_id,),
    )


def ja_avaliado(pedido_id, produto_id):
    linhas = database.consultar(
        "SELECT id FROM avaliacoes WHERE pedido_id = %s AND produto_id = %s",
        (pedido_id, produto_id),
    )
    return len(linhas) > 0
