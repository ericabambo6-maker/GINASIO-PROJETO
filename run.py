import os
from app import create_app
from config import DEBUG

app = create_app()

if __name__ == "__main__":
    if DEBUG:
        # Modo de desenvolvimento (teu PC)
        app.run(debug=True, host="0.0.0.0", port=5000)
    else:
        # Modo de produção (Render)
        # O Render injeta a porta correta na variável "PORT"
        port = int(os.environ.get("PORT", 8080))
        from waitress import serve
        print(f"STAE em produção rodando na porta {port}")
        serve(app, host="0.0.0.0", port=port)