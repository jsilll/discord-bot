# Description: Get the current price of bitcoin
# Import the requests library
import time
import datetime
import requests

supported_cryptos = ["bitcoin", "ethereum"]


def get_latest_crypto_price(*cryptos):
    # Function to get the latest crypto currency price for a specific "crypto" (bitcoin, litecoin, ethereum)
    # Get the URL ticker to get the .json file of the crypto currency
    TICKER_API_URL = "https://api.coinmarketcap.com/v1/ticker/"
    output = []
    for crypto in cryptos:
        if crypto.lower() not in supported_cryptos:
            continue

        response = requests.get(TICKER_API_URL + crypto)
        response_json = response.json()
        output.append((response_json[0]["name"], float(
            response_json[0]["price_usd"])))

    return output


def track_crypto(crypto, filename):
    def my_time():
        time = datetime.datetime.now()
        return (time.day, time.month, time.year, time.hour, time.minute, time.second)
    if isinstance(crypto, str) and isinstance(filename, str):
        if crypto not in supported_cryptos:
            raise ValueError("track_crypto: invalid arguments")
        with open(filename, "w") as f:
            last_price = None
            while True:
                new_price = get_latest_crypto_price(crypto)[0][1]
                if new_price != last_price:
                    last_price = new_price
                    # save on file
                    output = str((my_time(), new_price))
                    print(output)
                    f.write(output + "\n")
                time.sleep(1)
    else:
        raise ValueError("track_crypto: invalid arguments")
