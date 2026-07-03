import os

from flask import Flask, send_from_directory

from app.backend import init_db
from config import DEBUG, SECRET_KEY, UPLOAD_DIR

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, "templates"),
        static_folder=os.path.join(BASE_DIR, "static"),
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///stae.db")
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["DEBUG"] = DEBUG

    init_db()

    from app.routes.auth import auth_bp
    from app.routes.registos import registos_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(registos_bp)
    app.register_blueprint(admin_bp)

    # Serve uploaded files
    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        return send_from_directory(os.path.join(BASE_DIR, 'uploads'), filename)
    
    # Serve uploaded files at root level for compatibility
    @app.route('/documentos/<path:filename>')
    def serve_documentos(filename):
        # For production, we'll use Supabase Storage
        # For now, serve from local directory
        try:
            return send_from_directory(UPLOAD_DIR, filename)
        except FileNotFoundError:
            return "Foto não encontrada", 404

    return app
