from crypto_prices import create_app

if __name__ == "__main__":
    app = create_app(env="dev")
    with app.app_context():
        from crypto_prices import views

    app.run()
