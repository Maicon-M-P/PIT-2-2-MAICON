"""Ponto de entrada da API - Loja de Cupcakes (PIT 2)."""
from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from controllers import (
    admin_controller,
    avaliacao_controller,
    frete_controller,
    pedido_controller,
    produto_controller,
)


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = Config.SECRET_KEY

    # CORS: libera o domínio da Vercel e o localhost para testes locais.
    CORS(
        app,
        origins=[
            Config.FRONTEND_URL,
            "http://localhost:5500",
            "http://127.0.0.1:5500",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "null",
        ],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
        supports_credentials=True,
    )

    # Blueprints (controllers)
    app.register_blueprint(produto_controller.bp)
    app.register_blueprint(pedido_controller.bp)
    app.register_blueprint(frete_controller.bp)
    app.register_blueprint(avaliacao_controller.bp)
    app.register_blueprint(admin_controller.bp)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"}), 200

    @app.errorhandler(404)
    def nao_encontrado(erro):
        return jsonify({"erro": "Recurso não encontrado"}), 404

    @app.errorhandler(405)
    def metodo_nao_permitido(erro):
        return jsonify({"erro": "Método não permitido"}), 405

    @app.errorhandler(500)
    def erro_interno(erro):
        return jsonify({"erro": "Erro interno do servidor"}), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=Config.PORT, debug=True)
