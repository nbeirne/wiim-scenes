from lib.server import routes

app = routes.app

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')

