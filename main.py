# If debug is enabled, the program will not search for stock information online
debug = False

from datetime import datetime   # For getting the current date and time
import sqlite3  # For database management
from requests_html import HTMLSession   # https://github.com/psf/requests-html  # For web scraping
from tkinter import *       # For GUI
from tkinter.ttk import *   # For GUI

# API keys (stored in secrets.txt)
try:
    with open("secrets.txt", "r") as file:
        exchange_rate_api_key = file.readline()
except:
    exchange_rate_api_key = "Error"

# Functions
def open_database(filename):
    connection = sqlite3.connect(filename)
    connection.row_factory = sqlite3.Row
    return connection

def read_database(connection, sql):
    cursor = connection.cursor()
    cursor.execute(sql)
    result = [ dict(row) for row in cursor.fetchall() ]
    return result

def write_database(connection, sql):
    cursor = connection.cursor()
    rows_affected = cursor.execute(sql).rowcount
    connection.commit()
    return rows_affected

def close_database(connection):
    connection.close()

def search(URL):
    # If debug is enabled, don't search (as if it's offline)
    if debug:
        return ""

    # Search the given link and return the data in a dictionary
    session = HTMLSession()
    result = session.get(URL)
    result = result.json()
    return result

def get_stock_name(stock_code):
    URL = f"https://query2.finance.yahoo.com/v6/finance/options/{stock_code}"
    result = search(URL)

    # Get the stock's name
    try:
        name = result["optionChain"]["result"][0]["quote"]["shortName"]
    except:
        name = "Error"

    return name

def get_stock_currency(stock_code):
    URL = f"https://query2.finance.yahoo.com/v6/finance/options/{stock_code}"
    result = search(URL)

    # Get the stock's trading currency
    try:
        currency = result["optionChain"]["result"][0]["quote"]["currency"]
    except:
        currency = "Error"

    return currency

def get_exchange_rate(currency1, currency2):
    URL = f"https://v6.exchangerate-api.com/v6/{exchange_rate_api_key}/latest/{currency1}"
    result = search(URL)

    # Get the exchange rate between two currencies
    try:
        rate = float(result["conversion_rates"][currency2])
    except:
        rate = "Error"

    return rate

def get_stock_info(stock_code):
    URL = f"https://query2.finance.yahoo.com/v6/finance/options/{stock_code}"

    return_info = []

    try:
        result = search(URL)
        return_info.append(result["optionChain"]["result"][0]["quote"]["regularMarketPrice"])

        update_stock_current_price(stock_code, return_info[-1])
    except:
        return_info.append("Error")

    try:
        stock_price_change = result["optionChain"]["result"][0]["quote"]["regularMarketChangePercent"]

        if stock_price_change > 0:
            return_info.append("↑")
        else:
            return_info.append("↓")

        update_stock_price_change(stock_code, return_info[-1])
    except:
        return_info.append("Error")

    return return_info

def add_stock():
    code = input_code_field.get()
    price = float(input_price_field.get())
    quantity = int(input_quantity_field.get())
    true_currency = get_stock_currency(code)
    currency = currency_field.get()

    if "" in [code, currency] or price <= 0 or quantity <= 0:
        return

    if true_currency != "Error":
        exchange_rate = get_exchange_rate(currency, true_currency)
        if exchange_rate != "Error":
            price *= exchange_rate
            currency = true_currency

    # Add to the database
    write_database(connection, f"INSERT INTO stocks (stock_code, stock_name, quantity, buying_price, currency) VALUES ('{code}', '{get_stock_name(code)}', {quantity}, {price}, '{currency}');")
    add_successful_text = Label(text=f"{quantity} {code} stocks added successfully! Please restart the application to update your portfolio.", master=add_frame)
    add_successful_text.grid(row=2, columnspan=4)

def remove_stock(stock_code):
    # Remove from database
    write_database(connection, f"DELETE FROM stocks WHERE stock_code='{stock_code}';")
    remove_successful_text = Label(text=f"{stock_code} stocks removed successfully! Please restart the program to remove it from your portfolio.", master=window)
    remove_successful_text.grid(row=2, column=0)

def update_stock_update_date(stock_code):
    write_database(connection, f"UPDATE stocks SET last_updated=datetime('now', 'localtime') WHERE stock_code='{stock_code}';")

def update_stock_current_price(stock_code, current_price):
    write_database(connection, f"UPDATE stocks SET selling_price={current_price} WHERE stock_code='{stock_code}';")

def update_stock_price_change(stock_code, price_change):
    write_database(connection, f"UPDATE stocks SET price_change='{price_change}' WHERE stock_code='{stock_code}';")

# Open database
file_name = "stocks.db"
connection = open_database(file_name)
table = read_database(connection, "SELECT * FROM stocks;")

# Show app
window = Tk()
window.configure()  # Can change bg colour here
window.title("Stock Tracker")

font_family = "Arial"
body_font_size = 14
title_font_size = 24

# Title frame
title_frame = Frame(master=window, padding=25)
txt_title = Label(text="Portfolio", master=title_frame, font=(font_family, title_font_size))
txt_title.pack()

# Stock information frame
padding = 5
stock_info_frame = Frame(master=window, padding=10)
stocks = []

# Column information
stocks.append([
    Label(text="", master=stock_info_frame, padding=padding, font=(font_family, body_font_size)),
    Label(text="Stock Code", master=stock_info_frame, padding=padding, font=(font_family, body_font_size)),
    Label(text="Stock Name", master=stock_info_frame, padding=padding, font=(font_family, body_font_size)),
    Label(text="Currency", master=stock_info_frame, padding=padding, font=(font_family, body_font_size)),
    Label(text="Stock Price", master=stock_info_frame, padding=padding, font=(font_family, body_font_size)),
    Label(text="Quantity", master=stock_info_frame, padding=padding, font=(font_family, body_font_size)),
    Label(text="Price Paid", master=stock_info_frame, padding=padding, font=(font_family, body_font_size)),
    Label(text="Price Change", master=stock_info_frame, padding=padding, font=(font_family, body_font_size)),
    Label(text="Profit/Loss", master=stock_info_frame, padding=padding, font=(font_family, body_font_size)),
    Label(text="Last Updated", master=stock_info_frame, padding=padding, font=(font_family, body_font_size)),
    Label(text="", master=stock_info_frame, padding=padding, font=(font_family, body_font_size)),
])

# Get all the stock information and save it
print("\nGetting latest stock information, please wait...")
i = 0
while i < len(table):
    stock = table[i]

    stock_info = get_stock_info(stock["stock_code"])
    if "Error" in stock_info:
        price = stock["selling_price"]
        change = stock["price_change"]
    else:
        price = stock_info[0]
        change = stock_info[1]

    if change == "↑":
        change_colour = "#009900"
    else:
        change_colour = "#FF0000"

    try:
        profit = str(round(((float(price) * int(stock["quantity"])) - float(stock["buying_price"])), 2))

        if "-" in profit:
            profit_colour = "#FF0000"
        else:
            profit_colour = "#00AA00"
    except:
        profit = "Error"
        profit_colour = "#000000"

    if stock["stock_name"] == "Error":
        last_updated_date = "Error"
    elif stock["last_updated"] == None:
        update_stock_update_date(stock["stock_code"])
        last_updated_date = str(datetime.now()).split(".")[0]
    elif "Error" in stock_info:
        last_updated_date = stock["last_updated"]
    else:
        update_stock_update_date(stock["stock_code"])
        last_updated_date = str(datetime.now()).split(".")[0]

    stocks.append([
        Button(text="View Info", master=stock_info_frame, padding=padding, command=lambda stock_code=stock["stock_code"]: print(f"Viewing {stock_code} stock information")),
        Label(text=stock["stock_code"], master=stock_info_frame, padding=padding, font=(font_family, body_font_size)),
        Label(text=stock["stock_name"], master=stock_info_frame, padding=padding, font=(font_family, body_font_size)),
        Label(text=stock["currency"], master=stock_info_frame, padding=padding, font=(font_family, body_font_size)),
        Label(text=price, master=stock_info_frame, padding=padding, font=(font_family, body_font_size)),
        Label(text=stock["quantity"], master=stock_info_frame, padding=padding, font=(font_family, body_font_size)),
        Label(text=stock["buying_price"], master=stock_info_frame, padding=padding, font=(font_family, body_font_size)),
        Label(text=change, master=stock_info_frame, padding=padding, foreground=change_colour, font=(font_family, body_font_size, "bold")),
        Label(text=profit, master=stock_info_frame, padding=padding, foreground=profit_colour, font=(font_family, body_font_size)),
        Label(text=last_updated_date, master=stock_info_frame, padding=padding, font=(font_family, body_font_size)),
        Button(text="Remove", master=stock_info_frame, padding=padding, command=lambda stock_code=stock["stock_code"]: remove_stock(stock_code)),
    ])

    i += 1

# Add new stocks
add_frame = Frame(master=window, padding=10)

input_code_help = Label(text="Stock Code", master=add_frame)
input_code_field = Entry(master=add_frame)
input_quantity_help = Label(text="Quantity", master=add_frame)
input_quantity_field = Entry(master=add_frame)
input_price_help = Label(text="Price Paid", master=add_frame)
input_price_field = Entry(master=add_frame)
currency_help = Label(text="Currency (e.g.: USD)", master=add_frame)
currency_field = Entry(master=add_frame)
submit_button = Button(text="Add Stock", master=add_frame, command=lambda : add_stock())

input_code_help.grid(row=0, column=0)
input_code_field.grid(row=1, column=0)
input_quantity_help.grid(row=0, column=1)
input_quantity_field.grid(row=1, column=1)
input_price_help.grid(row=0, column=2)
input_price_field.grid(row=1, column=2)
currency_help.grid(row=0, column=3)
currency_field.grid(row=1, column=3)
submit_button.grid(row=1, column=4)

# Display stored stock widgets
for i in range(len(table)+1):
    for j in range(len(stocks[0])):
        stocks[i][j].grid(row=i, column=j)

title_frame.grid(row=0, column=0)
stock_info_frame.grid(row=1, column=0)
add_frame.grid(row=3, column=0)

window.mainloop()

# Close database and exit
close_database(connection)
