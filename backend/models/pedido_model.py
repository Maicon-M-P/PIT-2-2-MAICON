"""Acesso aos dados dos pedidos e dos itens do pedido."""
from models import database


def criar(pedido):
    """Grava pedido e itens em uma única transação."""
    import psycopg2
    from psycopg2.extras import RealDictCursor

    conn = database.get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                INSERT INTO pedidos
                    (numero_pedido, cliente_nome, cliente_whatsapp, cep,
                     endereco_rua, endereco_numero, endereco_complemento,
                     endereco_bairro, endereco_cidade, valor_produtos,
                     valor_frete, valor_total, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, numero_pedido
                """,
                (
                    pedido["numero_pedido"], pedido["cliente_nome"],
                    pedido["cliente_whatsapp"], pedido["cep"],
                    pedido.get("endereco_rua"), pedido["endereco_numero"],
                    pedido.get("endereco_complemento"),
                    pedido.get("endereco_bairro"), pedido.get("endereco_cidade"),
                    pedido["valor_produtos"], pedido["valor_frete"],
                    pedido["valor_total"], pedido["status"],
                ),
            )
            pedido_salvo = dict(cursor.fetchone())
            pedido_id = pedido_salvo["id"]

            for item in pedido["itens"]:
                cursor.execute(
                    """
                    INSERT INTO itens_pedido
                        (pedido_id, produto_id, quantidade, preco_unitario, observacao)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (pedido_id, item["produto_id"], item["quantidade"],
                     item["preco_unitario"], item.get("observacao", "")),
                )
            conn.commit()
            return pedido_salvo
    except psycopg2.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def gerar_numero_pedido():
    linhas = database.consultar("SELECT COALESCE(MAX(id), 0) + 1 AS proximo FROM pedidos")
    return "CUP-{}".format(1000 + linhas[0]["proximo"])


def buscar_por_numero(numero_pedido):
    return database.consultar(
        "SELECT * FROM pedidos WHERE numero_pedido = %s", (numero_pedido,)
    )


def buscar_por_id(pedido_id):
    return database.consultar("SELECT * FROM pedidos WHERE id = %s", (pedido_id,))


def listar_todos():
    return database.consultar("SELECT * FROM pedidos ORDER BY criado_em DESC")


def itens_do_pedido(pedido_id):
    return database.consultar(
        """
        SELECT i.*, p.nome AS produto_nome
        FROM itens_pedido i
        JOIN produtos p ON p.id = i.produto_id
        WHERE i.pedido_id = %s
        """,
        (pedido_id,),
    )


def atualizar_status(pedido_id, status):
    return database.executar(
        "UPDATE pedidos SET status = %s WHERE id = %s RETURNING *", (status, pedido_id)
    )
