from crypto_prices import db


class Crypto(db.Model):
    __table__ = db.Model.metadata.tables["crypto"]


class CryptoPrices(db.Model):
    __table__ = db.Model.metadata.tables["crypto_prices"]
