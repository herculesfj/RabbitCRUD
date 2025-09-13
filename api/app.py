from flask import Flask, jsonify
from controllers.user_controller import bp as users_bp
import logging
from config import MONGO_URI, RABBITMQ_HOST

def create_app():
    app = Flask(__name__)
    app.register_blueprint(users_bp)

    # basic health endpoints
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status":"ok"}), 200

    logging.basicConfig(level=logging.INFO)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
