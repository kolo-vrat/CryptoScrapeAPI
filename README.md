# Cryptocurrencies price scraping

This project is designed in two parts:

 - Scraping cryptocurrencies info and prices from [www.coingecko.com](https://www.coingecko.com/)
 - Expose the info as an API using Flask

## Installation

1. **Clone the repo**
    ```bash
    git clone https://github.com/kolo-vrat/CryptoScrapeAPI.git
    cd CryptoScrapeAPI
    ```

2. **Create a virtual environment**
    ```bash
    python -m venv venv
    . venv/bin/activate 
    ```

3. **Install requirements**
    ```bash
    pip install -r requirements.txt
    ```

## Running the scraper

To run the scraper and get latest cryptocurrency data:
```bash
python scrape/run.py
```

Data will be saved under `database/crypto_prices.db`

## Running the API

First modify the SQLALCHEMY_DATABASE_URI setting in the corresponding env file under the conf folder.

To start the Flask API server:
```bash
python run.py
```
The API will be accessible at `http://127.0.0.1:5000/`.

### API endpoints

 - GET `/crypto/<int:id_>` - Get info for the crypto with the specified id
 - GET `/crypto/all` - Get info for all cryptocurrencies in the database
 - GET `/crypto/price/<int:id_>` - Get the price of the crypto with the specified id
 - GET `/crypto/price/all` - Get price info for all cryptocurrencies in the database
