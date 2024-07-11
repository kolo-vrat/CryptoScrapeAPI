import os
import asyncio
import logging
from urllib.parse import urljoin

import httpx
import ua_generator
from bs4 import BeautifulSoup
from lxml import etree

from db import DBInterface

if not os.path.exists("database/"):
    os.mkdir("database")
db = DBInterface("database/crypto_prices.db")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def scrape_links(response):
    soup = BeautifulSoup(response.text, "html.parser")
    elems = soup.select(
        "table[data-coin-table-target='table'] > tbody > tr > td:nth-child(3) > a"
    )
    links = [
        urljoin("https://www.coingecko.com/", elem.get("href"))
        for elem in elems
        if elem.get("href")
    ]
    return links


async def scrape_data(url: str, headers: dict, semaphore: asyncio.Semaphore):
    async with semaphore:
        async with httpx.AsyncClient() as client:
            logger.info(f"Getting URL: {url}")
            response = await client.get(url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            parser = etree.HTMLParser(remove_blank_text=True)
            html = etree.HTML(response.text, parser)
            price = circ_supply = max_supply = all_time_high = all_time_low = 0
            name = ticker = ""
            website = None

            # price
            price_elem = soup.select_one("[data-converter-target='price']")
            if price_elem:
                price = (
                    price_elem.get_text(strip=True).replace("$", "").replace(",", "")
                )
                try:
                    price = float(price)
                except ValueError:
                    price = 0

            # name
            name_elem = soup.select_one(
                "div[data-coin-show-target='staticCoinPrice'] h1 > div"
            )
            if name_elem:
                name = name_elem.get_text(strip=True)

            # ticker
            ticker_elem = soup.select_one(
                "div[data-coin-show-target='staticCoinPrice'] h1 > span"
            )
            if ticker_elem:
                ticker = ticker_elem.get_text(strip=True).replace("Price", "").strip()

            # website
            website_elem = html.xpath(
                "//*[@data-key='tab-info']/parent::div/div[5]/div[1]//a"
            )
            if website_elem:
                website = website_elem[0].get("href", "").strip()

            # circulating_supply
            circ_supply_elem = html.xpath(
                "//*[contains(text(), 'Circulating Supply')]/parent::tr/td"
            )
            if circ_supply_elem:
                circ_supply = circ_supply_elem[0].text.strip().replace(",", "")
                try:
                    circ_supply = int(circ_supply)
                except ValueError:
                    circ_supply = 0

            # max_supply
            max_supply_elem = html.xpath(
                "//*[contains(text(), 'Max Supply')]/parent::tr/td"
            )
            if max_supply_elem:
                max_supply = max_supply_elem[0].text.strip().replace(",", "")
                try:
                    max_supply = int(max_supply)
                except ValueError:
                    max_supply = 0

            # all_time_high
            all_time_high_elem = html.xpath(
                "//h2[@itemprop='about']/parent::div/table/tbody/tr[3]/td/div/span[1]"
            )
            if all_time_high_elem:
                all_time_high = (
                    all_time_high_elem[0].text.strip().replace("$", "").replace(",", "")
                )
                try:
                    all_time_high = float(all_time_high)
                except ValueError:
                    all_time_high = 0

            # all_time_low
            all_time_low_elem = html.xpath(
                "//h2[@itemprop='about']/parent::div/table/tbody/tr[4]/td/div/span[1]"
            )
            if all_time_low_elem:
                all_time_low = (
                    all_time_low_elem[0].text.strip().replace("$", "").replace(",", "")
                )
                try:
                    all_time_low = float(all_time_low)
                except ValueError:
                    all_time_low = 0

        res = db.insert_crypto(
            name, ticker, max_supply, circ_supply, all_time_high, all_time_low, website
        )
        if res:
            logger.info(f"Successfully inserted cryptocurrency: {name} in the DB")

        res = db.insert_crypto_price(price, ticker=ticker)
        if res:
            logger.info("Successfully inserted cryptocurrency price info in the DB")

        await asyncio.sleep(1)


async def main():
    user_agent = ua_generator.generate(
        device="desktop", platform="linux", browser="chrome"
    ).text

    headers = {
        "Accept": "*/*",
        "User-Agent": user_agent,
        "Accept-Language": "en-US,en;q=0.9",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get("https://www.coingecko.com/", headers=headers)

    links = scrape_links(response)

    semaphore = asyncio.Semaphore(3)
    tasks = []
    for link in links[:20]:
        task = asyncio.create_task(scrape_data(link, headers, semaphore))
        tasks.append(task)

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
