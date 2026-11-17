"""Configurações da aplicação lidas de variáveis de ambiente."""
import os

# Permite carregar o .env quando estiver rodando localmente.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Config:
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    ADMIN_USER = os.getenv("ADMIN_USER", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "senha123")
    SECRET_KEY = os.getenv("SECRET_KEY", "chave-local-de-desenvolvimento")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5500")
    PORT = int(os.getenv("PORT", 5000))

    # Nome do bucket público de imagens no Supabase Storage
    BUCKET_IMAGENS = "cupcakes-imagens"

    # Frete fixo da loja
    FRETE_FIXO = 20.00

    # Status válidos do pedido
    STATUS_PEDIDO = (
        "Aguardando Pagamento",
        "Pago / Em Preparo",
        "Saiu para Entrega",
        "Entregue",
        "Cancelado",
    )
