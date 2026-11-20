
import requests
from lxml import html
import schedule
import time
import csv
import os
import re
import json

from datetime import datetime
from urllib.parse import urlparse


csv_file = "availability_history.csv"


# --------------------------------------------------
# 1. SAVE PRODUCT DETAILS INTO CSV
# --------------------------------------------------

def save_to_csv(name, price, status, quantity, website):

    file_exists = os.path.isfile(csv_file)

    with open(csv_file, "a", newline="", encoding="utf-8") as file:

        writer = csv.writer(file)

        if not file_exists or os.path.getsize(csv_file) == 0:

            writer.writerow([
                "Date and Time",
                "Website",
                "Product Name",
                "Price",
                "Availability Status",
                "Quantity Available"
            ])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            website,
            name,
            price,
            status,
            quantity
        ])

    print("Product details saved to CSV successfully!")


# --------------------------------------------------
# 2. FIND PRODUCT INFORMATION IN JSON-LD
# --------------------------------------------------

def find_product_data(data):

    products = []

    if isinstance(data, list):

        for item in data:
            products.extend(find_product_data(item))

    elif isinstance(data, dict):

        product_type = data.get("@type", [])

        if isinstance(product_type, str):
            product_type = [product_type]

        if "Product" in product_type:
            products.append(data)

        # Search inside @graph
        if "@graph" in data:
            products.extend(find_product_data(data["@graph"]))

    return products


def extract_jsonld(tree):

    scripts = tree.xpath(
        '//script[@type="application/ld+json"]/text()'
    )

    for script in scripts:

        try:

            data = json.loads(script.strip())

            products = find_product_data(data)

            for product in products:

                name = product.get("name")

                offers = product.get("offers", {})

                if isinstance(offers, list):
                    offers = offers[0] if offers else {}

                if not isinstance(offers, dict):
                    offers = {}

                price = (
                    offers.get("price")
                    or offers.get("lowPrice")
                    or product.get("price")
                )

                currency = offers.get("priceCurrency", "")

                if price is not None and currency:
                    price = str(price) + " " + currency

                availability = str(
                    offers.get("availability", "")
                ).lower()

                # Determine stock status
                if "outofstock" in availability:

                    status = "OUT OF STOCK"
                    quantity = 0

                elif (
                    "instock" in availability
                    or "limitedavailability" in availability
                ):

                    status = "IN STOCK"

                    # Quantity is optional in structured data
                    inventory = offers.get("inventoryLevel", {})

                    if isinstance(inventory, dict):
                        quantity = inventory.get("value", "Unknown")
                    else:
                        quantity = "Unknown"

                else:

                    status = "AVAILABILITY UNKNOWN"
                    quantity = "Unknown"

                if name:
                    return name, price or "Not specified", status, quantity

        except (json.JSONDecodeError, TypeError, AttributeError):
            continue

    return None


# --------------------------------------------------
# 3. FALLBACK EXTRACTION FOR BOOKS TO SCRAPE
# --------------------------------------------------

def extract_books_data(tree):

    name_list = tree.xpath(
        '//div[contains(@class,"product_main")]/h1/text()'
    )

    price_list = tree.xpath(
        '//p[contains(@class,"price_color")]/text()'
    )

    stock_text = tree.xpath(
        'string(//p[contains(@class,"instock") or contains(@class,"out_of_stock")])'
    ).strip()

    if not name_list or not price_list:
        return None

    name = name_list[0].strip()
    price = price_list[0].strip()

    if "out of stock" in stock_text.lower():

        status = "OUT OF STOCK"
        quantity = 0

    elif "in stock" in stock_text.lower():

        status = "IN STOCK"

        match = re.search(
            r'\(\s*(\d+)\s+available\)',
            stock_text,
            re.IGNORECASE
        )

        if match:
            quantity = int(match.group(1))
        else:
            quantity = "Quantity not specified"

    else:

        status = "AVAILABILITY UNKNOWN"
        quantity = "Unknown"

    return name, price, status, quantity


# --------------------------------------------------
# 4. CHECK PRODUCT AVAILABILITY
# --------------------------------------------------

def check_product_availability():

    print("\nChecking product availability...")
    print("-----------------------------------")

    try:

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        tree = html.fromstring(response.content)

        # First try structured product information
        product_data = extract_jsonld(tree)

        if product_data:

            name, price, status, quantity = product_data
            extraction_method = "JSON-LD"

        else:

            # Try the Books to Scrape fallback
            product_data = extract_books_data(tree)

            if product_data:

                name, price, status, quantity = product_data
                extraction_method = "Books to Scrape XPath"

            else:

                print("Product information could not be extracted.")
                print("This website may require a custom extraction method.")
                return

        website = urlparse(url).netloc

        print("Website:", website)
        print("Extraction Method:", extraction_method)
        print("Product Name:", name)
        print("Price:", price)
        print("Availability:", status)
        print("Quantity Available:", quantity)

        save_to_csv(
            name,
            price,
            status,
            quantity,
            website
        )

    except requests.exceptions.Timeout:

        print("Error: The website took too long to respond.")

    except requests.exceptions.HTTPError as e:

        print("HTTP Error:", e)

    except requests.exceptions.RequestException as e:

        print("Request Error:", e)

    except Exception as e:

        print("An unexpected error occurred:", e)


# --------------------------------------------------
# 5. GET AND VALIDATE PRODUCT URL
# --------------------------------------------------

while True:

    url = input("\nEnter the product URL: ").strip()

    parsed_url = urlparse(url)

    if (
        parsed_url.scheme in ["http", "https"]
        and parsed_url.netloc
    ):

        break

    else:

        print("Invalid URL! Enter a valid HTTP or HTTPS URL.")


# --------------------------------------------------
# 6. RUN FIRST CHECK
# --------------------------------------------------

check_product_availability()


# --------------------------------------------------
# 7. AUTOMATIC CHECK EVERY ONE MINUTE
# --------------------------------------------------

schedule.every(1).minutes.do(check_product_availability)

print("\nAutomatic product availability monitoring started.")
print("The program will check the product every 1 minute.")
print("Press CTRL + C to stop monitoring.")


try:

    while True:

        schedule.run_pending()
        time.sleep(1)

except KeyboardInterrupt:

    print("\nProduct availability monitoring stopped.")
