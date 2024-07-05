import argparse
import datetime
import logging

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    create_engine,
    func,
    insert,
    select,
    and_,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Session

Base = declarative_base()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Crypto(Base):
    __tablename__ = "crypto"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    ticker: Mapped[str] = mapped_column(String(10))
    website: Mapped[str] = mapped_column(String(256), nullable=True)
    max_supply: Mapped[int]
    circulating_supply: Mapped[int]
    all_time_high: Mapped[float]
    all_time_low: Mapped[float]


class CryptoPrice(Base):
    __tablename__ = "crypto_prices"
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(), primary_key=True)
    crypto_id = mapped_column(ForeignKey("crypto.id"), primary_key=True)
    price: Mapped[float]


class DBInterface:
    def __init__(self, uri: str):
        """
        Initialize the interface to the DB. Create connection and create the tables.

        :param uri: Locator to the DB file
        :type uri: str
        """
        self.engine = create_engine(f"sqlite:///{uri}")
        # Reflect the tables to the base metadata if they exist
        self.reflect_tables()
        # Create tables if they do not exist
        Base.metadata.create_all(self.engine)

    def reflect_tables(self):
        # Reflect the tables to the Base metadata
        Base.metadata.reflect(bind=self.engine)

    def insert_crypto(
        self,
        name: str,
        ticker: str,
        max_supply: int,
        circulating_supply: int,
        all_time_high: float,
        all_time_low: float,
        website: str = None,
    ) -> bool:
        """
        Insert new record in the crypto table. If there is a
        cryptocurrency with the same name and ticker it won't
        be inserted.

        :param name: Name of cryptocurrency.
        :type name: str
        :param ticker: The ticker of the cryptocurrency.
        :type ticker: str
        :param website: Official website.
        :type website: str
        :param max_supply: Maximum supply.
        :type max_supply: int
        :param circulating_supply: Circulating supply.
        :type circulating_supply: int
        :param all_time_high: All time high price.
        :type all_time_high: float
        :param all_time_low: All time low price.
        :type all_time_low: float
        :return: True if the record is inserted, False otherwise.
        :rtype: bool
        """
        stmt = select(Crypto).where(and_(Crypto.name == name, Crypto.ticker == ticker))
        try:
            with Session(self.engine) as session, session.begin():
                existing_crypto = session.scalars(stmt).first()
                if existing_crypto is None:
                    crypto = Crypto(
                        name=name,
                        ticker=ticker,
                        website=website,
                        max_supply=max_supply,
                        circulating_supply=circulating_supply,
                        all_time_high=all_time_high,
                        all_time_low=all_time_low,
                    )
                    session.add(crypto)
                else:
                    logger.debug("Cryptocurrency is already in the DB")
                    return False
            return True
        except Exception as e:
            logger.error(e)
            return False

    def insert_crypto_price(
        self, price: float, crypto_id: int = None, ticker: str = None
    ) -> bool:
        """
        Insert price info in the DB by the id or ticker of the cryptocurrency.

        :param crypto_id: The id of the crypto located in the crypto table.
        :type crypto_id: int
        :param ticker: The ticker of the crypto.
        :type ticker: str
        :return: True if the record is inserted, False otherwise.
        :rtype: bool
        """
        if crypto_id is None and ticker is None:
            raise ValueError("You need to provide either crypto_id or ticker")

        if crypto_id is not None:
            stmt = insert(CryptoPrice).values(
                timestamp=func.now(),
                crypto_id=crypto_id,
                price=price,
            )
            try:
                with Session(self.engine) as session, session.begin():
                    session.execute(stmt)
                return True
            except Exception as e:
                logger.error(e)
                return False
        elif ticker is not None:
            try:
                with Session(self.engine) as session, session.begin():
                    crypto = session.scalars(
                        select(Crypto).where(Crypto.ticker == ticker)
                    ).one()
                    stmt = insert(CryptoPrice).values(
                        timestamp=func.now(),
                        crypto_id=crypto.id,
                        price=price,
                    )
                    session.execute(stmt)
                return True
            except Exception as e:
                logger.error(e)
                return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Initialize the database and provide interface for manipulating it"
    )
    parser.add_argument("db_path", help="Path to the DB file where data will be stored")
    args = parser.parse_args()
    try:
        db = DBInterface(args.db_path)
    except Exception:
        print("Failed initializing the DB")
