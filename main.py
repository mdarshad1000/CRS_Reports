import httpx
import random
import time
import json
import logging
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from fastapi import FastAPI, HTTPException
from mangum import Mangum
import uvicorn
from fake_useragent import UserAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
handler = Mangum(app)

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


def fetch_data_per_category(category: str, search_term: str, page_number: int = 0):
    url = build_url(category, search_term, page_number)
    headers = get_headers()
    
    with httpx.Client() as client:
        retries = 5
        for attempt in range(retries):
            try:
                res = client.get(url, headers=headers, timeout=30)
                
                if res.status_code == 200:
                    logger.info("Success: %s", res)
                    return res.text
                elif res.status_code == 403:
                    logger.warning(f"403 Forbidden error on attempt {attempt + 1}")
                    time.sleep(random.uniform(5, 10))  # Random delay between 5 and 10 seconds
                else:
                    logger.warning(f"Failed attempt {attempt + 1}: Status code {res.status_code}")
            except httpx.RequestError as e:
                logger.error(f"Request error on attempt {attempt + 1}: {e}")
            
            time.sleep(random.uniform(2, 5))  # Random delay between attempts

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


def fetch_final_data(
    categories: List[str], start_date: str, end_date: str, search_term: str = ""
):
    start_date_dt, end_date_dt = parse_dates(start_date, end_date)

    final_data = []
    for category in categories:
        page_number = 1
        more_pages = True

        while more_pages:
            json_data = fetch_data_per_category(category, search_term, page_number)
            page_data = parse_data(json_data, start_date_dt, end_date_dt)

            # Break if no data is returned
            if not page_data:
                break

            final_data.extend(page_data)

            # Check if the last item is within the end date, if not, stop fetching more pages
            if datetime.strptime(page_data[-1]["date"], "%Y-%m-%d") < start_date_dt:
                more_pages = False
            else:
                page_number += 1

    return final_data, len(final_data)


class RequestBody(BaseModel):
    categories: List[str]
    start_date: Optional[str]
    end_date: Optional[str]


@app.post("/fetch-data")
async def fetch_data_endpoint(request_body: RequestBody):
    categories = request_body.categories
    start_date = request_body.start_date
    end_date = request_body.end_date
    try:
        data = fetch_final_data(
            categories=categories, start_date=start_date, end_date=end_date
        )
        return data
    except Exception as e:
        logger.error(f"Error in fetch_data_endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)


{
    "date": "Thu, 05 Sep 2024 22:49:00 GMT",
    "content-type": "text/html; charset=UTF-8",
    "transfer-encoding": "chunked",
    "connection": "close",
    "accept-ch": "Sec-CH-UA-Bitness, Sec-CH-UA-Arch, Sec-CH-UA-Full-Version, Sec-CH-UA-Mobile, Sec-CH-UA-Model, Sec-CH-UA-Platform-Version, Sec-CH-UA-Full-Version-List, Sec-CH-UA-Platform, Sec-CH-UA, UA-Bitness, UA-Arch, UA-Full-Version, UA-Mobile, UA-Model, UA-Platform-Version, UA-Platform, UA",
    "critical-ch": "Sec-CH-UA-Bitness, Sec-CH-UA-Arch, Sec-CH-UA-Full-Version, Sec-CH-UA-Mobile, Sec-CH-UA-Model, Sec-CH-UA-Platform-Version, Sec-CH-UA-Full-Version-List, Sec-CH-UA-Platform, Sec-CH-UA, UA-Bitness, UA-Arch, UA-Full-Version, UA-Mobile, UA-Model, UA-Platform-Version, UA-Platform, UA",
    "cross-origin-embedder-policy": "require-corp",
    "cross-origin-opener-policy": "same-origin",
    "cross-origin-resource-policy": "same-origin",
    "origin-agent-cluster": "?1",
    "permissions-policy": "accelerometer=(),autoplay=(),browsing-topics=(),camera=(),clipboard-read=(),clipboard-write=(),geolocation=(),gyroscope=(),hid=(),interest-cohort=(),magnetometer=(),microphone=(),payment=(),publickey-credentials-get=(),screen-wake-lock=(),serial=(),sync-xhr=(),usb=()",
    "referrer-policy": "same-origin",
    "x-content-options": "nosniff",
    "x-frame-options": "SAMEORIGIN",
    "cf-mitigated": "challenge",
    "cf-chl-out": "aGe495ub57I0zk+8J7Pcyl2Mb68qtMg94FvEhMVOQROSurPHuH8evUM4MsxEyEVscqGwT5enU+MbQz1okt5wACXkmoZMqStji6L2LO8QsBCbgq/S81wttqSfYyf0YUDDQ4ObJTgPA3cIAFlb2G2BXg==$P1zCQByfMmWh6ot2xDlOmA==",
    "cache-control": "private, max-age=0, no-store, no-cache, must-revalidate, post-check=0, pre-check=0",
    "expires": "Thu, 01 Jan 1970 00:00:01 GMT",
    "vary": "Accept-Encoding",
    "server": "cloudflare",
    "cf-ray": "8be9c5227fd95fcf-SIN",
    "content-encoding": "gzip",
}
{
    "date": "Thu, 05 Sep 2024 22:45:34 GMT",
    "content-type": "application/json; charset=utf-8",
    "transfer-encoding": "chunked",
    "connection": "keep-alive",
    "pragma": "no-cache",
    "expires": "-1",
    "age": "0",
    "content-security-policy": "frame-ancestors 'none'",
    "strict-transport-security": "max-age=31536000; includeSubDomains; preload",
    "cache-control": "no-cache, no-store, must-revalidate, max-age=0, s-maxage=0",
    "x-frame-options": "SAMEORIGIN",
    "cf-cache-status": "DYNAMIC",
    "server": "cloudflare",
    "cf-ray": "8be9c0089eb4898b-DEL",
    "content-encoding": "gzip",
}