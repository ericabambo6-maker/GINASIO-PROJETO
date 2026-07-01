from app import create_app
from config import DEBUG, HOST, PORT

app = create_app()

if __name__ == "__main__":
    if DEBUG:
        app.run(debug=True, host=HOST, port=PORT)
    else:
        from waitress import serve
        print(f"STAE em produção: http://{HOST}:{PORT}")
        serve(app, host=HOST, port=PORT)
