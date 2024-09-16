import traceback
import httpx
import random
import json
import logging
import uvicorn
import asyncio
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from fake_useragent import UserAgent
from fastapi import FastAPI, HTTPException
from httpx_socks import SyncProxyTransport, AsyncProxyTransport


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


category_navid_mapping = {
    "Foreign Affairs": 4294967243,
    "Law, Constitution & Civil Liberties": 4294966571,
    "Energy & Natural Resources": 4294967023,
    "Defense & Intelligence": 4294967138,
    "Appropriations": 4294967053,
    "Health Care": 4294967223,
    "Science & Technology": 4294967090,
    "Economy & Finance": 4294966669,
    "Homeland Security & Emergency Management": 4294966649,
    "Commerce & Small Business": 4294966993,
    "Environmental Policy": 4294967091,
    "Budget, Public Finance & Taxation": 4294967181,
    "Trade & International Finance": 4294966155,
    "Federal Government Management & Organization": 4294966133,
    "Agriculture, Food & Rural Policy": 4294966840,
    "Justice & Law Enforcement": 4294966559,
    "Retirement Security & Social Insurance": 4294966041,
    "Congressional Administration & Elections": 4294967151,
    "Legislative & Budget Process": 4294967164,
    "Labor & Employment": 4294967222,
    "Immigration": 4294966648,
    "Social Welfare": 4294966503,
    "Education": 4294966969,
    "Transportation": 4294966933,
    "Housing": 4294966212,
    "Veterans": 4294966968,
}


def parse_dates(start_date: str, end_date: str):
    """
    Args:
        start_date: str
        end_date: str
    Returns:
        return: tuple of datetime objects
    """
    return datetime.strptime(start_date, "%Y-%m-%d"), datetime.strptime(
        end_date, "%Y-%m-%d"
    )


def build_url(category: str, search_term: str, page_number: int):
    """
    Args:
        category: str
        search_term: str
        page_number: int
    Returns:
        constructed url: str 
    """
    nav_id = category_navid_mapping[category]
    random_six = random.randint(1000000, 9999999)
    return f"https://crsreports.congress.gov/search/results?term{search_term}=&r={random_six}&orderBy=Date&navids={nav_id}&pageNumber={page_number}&"


def get_headers():
    ua = UserAgent()
    return {
        # "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "User-Agent": ua.random,
        "Referer": "https://crsreports.congress.gov/search/",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8,ht;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Priority": "u=1, i",
        "Origin": "https://crsreports.congress.gov",
        "Connection": "keep-alive",
        "TE": "Trailers",
        "Accept": "application/json, text/plain, */*",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Sec-CH-UA": '"Chromium";v="128", "Google Chrome";v="128", ";Not A Brand";v="99"',
        "Sec-CH-UA-Mobile": "?0",
        "Sec-CH-UA-Platform": '"macOS"',
    }


def get_cookies():
    return {
        "AMCVS_0D15148954E6C5100A4C98BC%40AdobeOrg": "1",
        "s_ecid": "MCMID%7C81710461424735814132251758168733180272",
        "s_cc": "true",
        "ASP.NET_SessionId": "ciimk4xwu5rhyhbebipfcmi2",
        "s_sq": "%5B%5BB%5D%5D",
        "__cfruid": "a9722f8935700119f2bde35a08cef557a10e0fe0-1725492540",
        "__cf_bm": "ikDMJYfuzjjvTU22I.vOsZWm51_g7Da8DsO18ypvkug-1725576204-1.0.1.1-NNZU17qrGVUpfWJrN0me6L12AhRrGu0u6BoVEepXSDhzbGpOj7nov7qKyEv_ywkBzPlNa18X7foZ9i_q_8T88g",
        "AMCV_0D15148954E6C5100A4C98BC%40AdobeOrg": "179643557%7CMCIDTS%7C19971%7CMCMID%7C81710461424735814132251758168733180272%7CMCAAMLH-1726106414%7C12%7CMCAAMB-1726106414%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1725508814s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C5.5.0",
    }


proxy_url = "socks4://64.139.79.35:54321"
# Create a transport with the SOCKS4 proxy
# Replace SyncProxyTransport with AsyncProxyTransport for async operations
transport = AsyncProxyTransport.from_url(proxy_url)

async def fetch_data_per_category(category: str, search_term: str, page_number: int = 0) -> str:
    """Fetch data for a specific category and page number."""
    url = build_url(category, search_term, page_number)
    headers = get_headers()
    cookies = get_cookies()

    # Increase the connection timeout
    timeout = httpx.Timeout(10.0, connect=80.0)  # 10 seconds for overall timeout, 60 seconds for connection timeout
  
    async with httpx.AsyncClient(transport=transport, timeout=timeout) as client:
        for attempt in range(5):
            try:
                res = await client.get(url, headers=headers, timeout=200, cookies=cookies)

                if res.status_code == 200:
                    logger.info("Success: %s", res)
                    return res.text
                elif res.status_code == 403:
                    logger.warning(f"403 Forbidden error on attempt {attempt + 1}")
                    await asyncio.sleep(random.uniform(5, 10))
                else:
                    logger.warning(f"Failed attempt {attempt + 1}: Status code {res.status_code}")
            except httpx.RequestError as e:
                logger.error(f"Request error on attempt {attempt + 1}: {e}")
                logger.error(traceback.format_exc())  # Log the full traceback

            
            await asyncio.sleep(random.uniform(2, 5))

    raise HTTPException(status_code=500, detail="Failed to fetch data after multiple attempts")


def parse_data(json_data: str, start_date: datetime, end_date: datetime):
    data = json.loads(json_data)
    search_result = data["SearchResults"]

    final_data = []
    for item in search_result:
        title = item["Title"]
        date = item["CoverDate"][:10]
        product_number = item["ProductNumber"]
        product_code = item["ProductTypeCode"]
        pdf_url = f"https://crsreports.congress.gov/product/pdf/{product_code}/{product_number}"
        authors = [i["FirstName"] for i in item["Authors"]]
        no_of_pages = item["NumberOfPages"]

        # convert date to datetime object for comparison
        date = datetime.strptime(date, "%Y-%m-%d")

        if start_date <= date <= end_date:
            final_data.append(
                {
                    "title": title,
                    "date": date.strftime("%Y-%m-%d"),
                    "pdf_url": pdf_url,
                    "authors": authors,
                    "no_of_pages": no_of_pages,
                }
            )

    return final_data


async def fetch_final_data(categories: List[str], start_date: str, end_date: str, search_term: str = "") -> List[dict]:
    """Fetch and compile data for all specified categories."""
    start_date_dt, end_date_dt = parse_dates(start_date, end_date)

    final_data = []
    for category in categories:
        page_number = 1
        while True:
            json_data = await fetch_data_per_category(category, search_term, page_number)
            page_data = parse_data(json_data, start_date_dt, end_date_dt)

            if not page_data:
                break

            final_data.extend(page_data)

            if datetime.strptime(page_data[-1]["date"], "%Y-%m-%d") < start_date_dt:
                break

            page_number += 1

    return final_data


async def upload_pdf(item: dict):
    """Upload a PDF file to the specified endpoint."""
    async with httpx.AsyncClient() as client:
        pdf_response = await client.get(item["pdf_url"], headers=get_headers())
        if pdf_response.status_code == 200:
            files = {'file': (f'{item["title"]}.pdf', pdf_response.content, 'application/pdf')}
            upload_response = await client.post('http://localhost:9000/accept-pdf', files=files)
            
            if upload_response.status_code == 200:
                logger.info(f"Successfully uploaded {item['title']}")
            else:
                logger.error(f"Failed to upload {item['title']}: {upload_response.content}")


class RequestBody(BaseModel):
    categories: List[str]
    start_date: str
    end_date: str


@app.post("/fetch-data")
async def fetch_data_endpoint(request_body: RequestBody):
    try:
        data = await fetch_final_data(
            categories=request_body.categories,
            start_date=request_body.start_date,
            end_date=request_body.end_date
        )
        
        # Upload PDFs synchronously
        for item in data:
            await upload_pdf(item)

        return data

    except Exception as e:
        logger.error(f"Error in fetch_data_endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)