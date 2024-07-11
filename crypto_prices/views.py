from flask import current_app, jsonify
from sqlalchemy import func, desc, and_

from crypto_prices import db
from crypto_prices.models import Crypto, CryptoPrices


def get_crypto(id_: int) -> Crypto | None:
    """
    Retrieve the crypto with the specified id from the database

    :param id_: The id of the cryptocrrency in the database
    :type id_: int
    :return: The Crypto object or None if the id is not present in the database
    :rtype: Crypto | None
    """
    c = Crypto.query.filter_by(id=id_).first()
    return c


@current_app.route("/crypto/<int:id_>")
def crypto(id_: int):
    """
    Get info for the crypto with the specified id
    """
    c = get_crypto(id_)
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


@current_app.route("/crypto/all")
def crypto_all():
    """
    Get info for all cryptocurrencies in the database
    """
    query_result = Crypto.query.all()
    crypto_list = [
        {
            "id": c.id,
            "name": c.name,
            "ticker": c.ticker,
            "website": c.website,
            "max_supply": c.max_supply,
            "circulating_supply": c.circulating_supply,
            "all_time_high": c.all_time_high,
            "all_time_low": c.all_time_low,
        }
        for c in query_result
    ]
    return jsonify({"result": crypto_list})


@current_app.route("/crypto/price/<int:id_>")
def crypto_price(id_: int):
    """
    Get the price of the crypto with the specified id
    """
    query_result = (
        CryptoPrices.query.filter_by(crypto_id=id_).order_by(desc("time")).first()
    )
    if query_result is None:
        return jsonify(
            {"error": "Price for the specified id is not present in the database"}
        ), 404
    c = get_crypto(id_)
    if c is None:
        return jsonify(
            {"error": "The specified crypto id is not present in the database"}
        ), 404
    return jsonify(
        {
            "result": {
                "name": c.name,
                "ticker": c.ticker,
                "price": query_result.price,
                "time": query_result.time,
            }
        }
    )


@current_app.route("/crypto/price/all")
def crypto_price_all():
    """
    Get price info for all cryptocurrencies in the database
    """
    subquery = (
        db.session.query(
            CryptoPrices.crypto_id, func.max(CryptoPrices.time).label("latest_time")
        )
        .group_by(CryptoPrices.crypto_id)
        .subquery()
    )
    query_result = (
        db.session.query(CryptoPrices.time, CryptoPrices.price, Crypto.name)
        .where(CryptoPrices.crypto_id == Crypto.id)
        .join(
            subquery,
            and_(
                CryptoPrices.crypto_id == subquery.c.crypto_id,
                CryptoPrices.time == subquery.c.latest_time,
            ),
        )
        .order_by(desc(CryptoPrices.price))
    ).all()
    crypto_list = [
        {
            "name": row[2],
            "price": row[1],
        }
        for row in query_result
    ]
    return jsonify({"result": crypto_list})
