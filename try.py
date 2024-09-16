import httpx
from httpx_socks import SyncProxyTransport, AsyncProxyTransport
import traceback
with open("socks4.txt", "r") as f:
    proxy_url = f.readlines()



headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
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


cookies = {
        "AMCVS_0D15148954E6C5100A4C98BC%40AdobeOrg": "1",
        "s_ecid": "MCMID%7C81710461424735814132251758168733180272",
        "s_cc": "true",
        "ASP.NET_SessionId": "ciimk4xwu5rhyhbebipfcmi2",
        "s_sq": "%5B%5BB%5D%5D",
        "__cfruid": "a9722f8935700119f2bde35a08cef557a10e0fe0-1725492540",
        "__cf_bm": "ikDMJYfuzjjvTU22I.vOsZWm51_g7Da8DsO18ypvkug-1725576204-1.0.1.1-NNZU17qrGVUpfWJrN0me6L12AhRrGu0u6BoVEepXSDhzbGpOj7nov7qKyEv_ywkBzPlNa18X7foZ9i_q_8T88g",
        "AMCV_0D15148954E6C5100A4C98BC%40AdobeOrg": "179643557%7CMCIDTS%7C19971%7CMCMID%7C81710461424735814132251758168733180272%7CMCAAMLH-1726106414%7C12%7CMCAAMB-1726106414%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1725508814s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C5.5.0",
    }
'''
64.139.79.35:54321
138.117.63.102:3629
31.13.239.4:5678
31.209.96.173:51688
'''
for item in proxy_url:
    proxy_url = "socks4://" + item.strip()

    # Create a transport with the SOCKS4 proxy
    transport = SyncProxyTransport.from_url(proxy_url)

    success = False

    while not success:
        try:
            # Create an httpx client with the transport
            with httpx.Client(transport=transport, verify=False) as client:
                # Make an HTTPS request to a web page
                response = client.get("https://crsreports.congress.gov/search/#/0?termsToSearch=&orderBy=Date&navIds=4294967223", headers=headers, cookies=cookies)

                # If the request was successful, set success flag to True
                success = True

                # Print the response content
                print(response)

        except Exception as e:
            # If an error occurs, print the error and break to use the next proxy
            print(f"An error occurred: {e}")
            break  # Break out of the while loop to try the next proxy

    if success:
        print(item)  # If successful, break out of the for loop to stop trying proxies