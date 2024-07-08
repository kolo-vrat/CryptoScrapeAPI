from flask import current_app, jsonify

from crypto_prices.models import Crypto, CryptoPrices


@current_app.route("/crypto/<int:id_>")
def crypto(id_: int):
    c = Crypto.query.filter_by(id=id_).first()
    if c is None:
        return jsonify(
            {"error": "The specified id is not present in the database"}
        ), 404
    return jsonify(
        {
            "result": {
                "id": c.id,
                "name": c.name,
                "ticker": c.ticker,
                "website": c.website,
                "max_supply": c.max_supply,
                "circulating_supply": c.circulating_supply,
                "all_time_high": c.all_time_high,
                "all_time_low": c.all_time_low,
            }
        }
    )
