# Online Product Availability Checker

A Python-based web scraping project that checks product availability, extracts product details, and maintains a history of availability checks in a CSV file.

This project is a personal reimplementation based on the concept of an earlier academic project. It is currently developed and tested using the Books to Scrape website, a practice website designed for web scraping.

## Features

- Extracts product name and price.
- Checks whether a product is in stock or out of stock.
- Attempts to extract product information from JSON-LD structured data.
- Uses website-specific XPath extraction as a fallback.
- Checks product availability automatically at regular intervals.
- Records availability history in a CSV file.
- Includes URL validation and error handling.
- Displays the website and extraction method used.

## Technologies Used

- Python
- Requests
- lxml
- Schedule
- CSV
- JSON
- Regular Expressions

## Project Structure

```text
Online-Product-Availability-Checker/
│
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation and Setup

1. Clone this repository:

   ```bash
   git clone https://github.com/YOUR-USERNAME/online-product-availability-checker.git
   ```

2. Navigate to the project folder:

   ```bash
   cd online-product-availability-checker
   ```

3. Install the required libraries:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Run the application:

   ```bash
   python main.py
   ```

## How It Works

1. The user enters a product page URL.
2. The application sends an HTTP request to retrieve the webpage.
3. It attempts to extract product information using JSON-LD structured data.
4. If structured data is unavailable, it uses XPath selectors designed for Books to Scrape.
5. The application identifies the product's availability status.
6. Product details are stored in a CSV file with a timestamp.
7. The process repeats automatically every minute until the user stops it.

## Output

The application displays:

- Website name
- Product name
- Product price
- Availability status
- Available quantity, when provided by the website
- Extraction method

It also creates an `availability_history.csv` file containing the recorded checks.

## Current Limitations

- The project is currently tested with Books to Scrape.
- XPath selectors are specific to the Books to Scrape website.
- JSON-LD extraction is attempted where supported by the webpage.
- Different shopping websites may require different extraction logic.
- The project does not currently use official shopping-platform APIs.

## Future Enhancements

- Support for multiple product URLs.
- Support for additional e-commerce websites.
- Price-change notifications.
- Availability alerts.
- Product availability analysis and visualisation.

## Purpose

This project demonstrates practical Python skills in web scraping, data extraction, automation, error handling, and storing structured data for further analysis.