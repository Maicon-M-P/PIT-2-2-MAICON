"""Conexão e helpers de acesso ao PostgreSQL."""
from config import Config


def get_connection():
    """Abre uma conexão com o banco. Import local para não exigir psycopg2 nos testes."""
    import psycopg2

    return psycopg2.connect(Config.DATABASE_URL)


def consultar(sql, params=None):
    """Executa um SELECT e devolve uma lista de dicionários."""
    from psycopg2.extras import RealDictCursor

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql, params)
            return [dict(linha) for linha in cursor.fetchall()]
    finally:
        conn.close()


def executar(sql, params=None):
    """Executa INSERT/UPDATE/DELETE. Com RETURNING, devolve a linha."""
    from psycopg2.extras import RealDictCursor

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql, params)
            if cursor.description:
                linha = cursor.fetchone()
                resultado = dict(linha) if linha else None
            else:
                resultado = cursor.rowcount
            conn.commit()
            return resultado
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
