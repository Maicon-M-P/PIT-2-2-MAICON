"""Acesso à configuração da loja e consulta ao ViaCEP."""
import requests

from models import database


def buscar_config():
    return database.consultar("SELECT * FROM configuracoes_loja WHERE id = 1")


def atualizar_config(chave_pix, whatsapp, cep_loja, codigo_ibge_loja):
    return database.executar(
        """
        UPDATE configuracoes_loja SET
            chave_pix = %s, whatsapp = %s,
            cep_loja = %s, codigo_ibge_loja = %s
        WHERE id = 1
        RETURNING *
        """,
        (chave_pix, whatsapp, cep_loja, codigo_ibge_loja),
    )


def consultar_viacep(cep):
    """Consulta o ViaCEP e devolve o JSON (ou None se inválido)."""
    resposta = requests.get(
        "https://viacep.com.br/ws/{}/json/".format(cep), timeout=5
    )
    if resposta.status_code != 200:
        return None
    dados = resposta.json()
    if dados.get("erro"):
        return None
    return dados


def buscar_ibge_loja():
    linhas = buscar_config()
    return linhas[0]["codigo_ibge_loja"] if linhas else None
