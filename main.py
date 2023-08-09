debug = False

import sqlite3
from requests_html import HTMLSession   # https://github.com/psf/requests-html
import tkinter as tk

# Testing
import cpi

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
    # Search the given link and return the data in a dictionary
    session = HTMLSession()
    result = session.get(URL)
    result = result.json()
    return result

def get_stock_name(stock_code):
    URL = f"https://query2.finance.yahoo.com/v7/finance/options/{stock_code}"
    result = search(URL)

    # Get the stock's name
    try:
        name = result["optionChain"]["result"][0]["quote"]["shortName"]
    except:
        name = "Error"

    return name

def get_stock_info(stock_code):
    URL = f"https://query2.finance.yahoo.com/v7/finance/options/{stock_code}"

    return_info = []

    try:
        result = search(URL)
        return_info.append(result["optionChain"]["result"][0]["quote"]["regularMarketPrice"])
    except:
        return_info.append("Error")

    try:
        stock_price_change = result["optionChain"]["result"][0]["quote"]["regularMarketChangePercent"]

        if stock_price_change > 0:
            return_info.append("↑")
        else:
            return_info.append("↓")
    except:
        return_info.append("Error")

    return return_info

def add_stock():
    code = input_code_field.get()
    price = input_price_field.get()
    quantity = input_quantity_field.get()
    # Add to the database
    write_database(connection, f"INSERT INTO stocks (stock_code, stock_name, quantity, buying_price) VALUES ('{code}', '{get_stock_name(code)}', {quantity}, {price});")
    add_successful_text.grid(row=2, columnspan=4)

def remove_stock(stock_code):
    # Remove from database
    write_database(connection, f"DELETE FROM stocks WHERE stock_code='{stock_code}';")
    remove_successful_text = tk.Label(text="Stock removed successfully! Please restart the application to fully remove the stock.", master=window)
    remove_successful_text.grid(row=2, column=0)


# Open database
file_name = "stocks.db"
connection = open_database(file_name)
table = read_database(connection, "SELECT * FROM stocks;")

# Show app
window = tk.Tk()
window.configure()  # Can change bg colour here
window.title("Stock Tracker")

font_family = "Arial"
body_font_size = 14
title_font_size = 24

# Title frame
title_frame = tk.Frame(master=window, padx=25, pady=25)
txt_title = tk.Label(text="Stock Information", master=title_frame, font=(font_family, title_font_size))
txt_title.pack()

# Stock information frame
padding = 5
stock_info_frame = tk.Frame(master=window, padx=10, pady=10)
stocks = []

# Column information
stocks.append([
    tk.Label(text="Stock Code", master=stock_info_frame, padx=padding, font=(font_family, body_font_size)),
    tk.Label(text="Stock Name", master=stock_info_frame, padx=padding, font=(font_family, body_font_size)),
    tk.Label(text="Stock Price", master=stock_info_frame, padx=padding, font=(font_family, body_font_size)),
    tk.Label(text="Quantity", master=stock_info_frame, padx=padding, font=(font_family, body_font_size)),
    tk.Label(text="Price Paid", master=stock_info_frame, padx=padding, font=(font_family, body_font_size)),
    tk.Label(text="Price Change", master=stock_info_frame, padx=padding, font=(font_family, body_font_size)),
    tk.Label(text="Profit/Loss", master=stock_info_frame, padx=padding, font=(font_family, body_font_size)),
    tk.Label(text="", master=stock_info_frame, padx=padding, font=(font_family, body_font_size)),
])

# Get all the stock information and save it
print("\nGetting latest stock information, please wait...")
i = 0
while i != len(table)-1:
    stock = table[i]

    if debug == True:
        price = "NaN"
        change = "NaN"
    else:
        stock_info = get_stock_info(stock["stock_code"])
        price = stock_info[0]
        change = stock_info[1]


    if change == "↑":
        change_colour = "#009900"
    else:
        change_colour = "#FF0000"

    try:
        profit = str(round((float(price) - float(stock["buying_price"])) * int(stock["quantity"]), 2))

        if "-" in profit:
            profit_colour = "#FF0000"
        else:
            profit_colour = "#00AA00"
    except:
        profit = "NaN"
        profit_colour = "#000000"

    stocks.append([
        tk.Label(text=stock["stock_code"], master=stock_info_frame, padx=padding, font=(font_family, body_font_size)),
        tk.Label(text=stock["stock_name"], master=stock_info_frame, padx=padding, font=(font_family, body_font_size)),
        tk.Label(text=price, master=stock_info_frame, padx=padding, font=(font_family, body_font_size)),
        tk.Label(text=stock["quantity"], master=stock_info_frame, padx=padding, font=(font_family, body_font_size)),
        tk.Label(text=stock["buying_price"], master=stock_info_frame, padx=padding, font=(font_family, body_font_size)),
        tk.Label(text=change, master=stock_info_frame, padx=padding, font=(font_family, body_font_size, "bold"), fg=change_colour),
        tk.Label(text=profit, master=stock_info_frame, padx=padding, font=(font_family, body_font_size), fg=profit_colour),
        tk.Button(text="Remove", master=stock_info_frame, padx=padding, command=lambda : remove_stock(stock["stock_code"])),
    ])

    i += 1

# Add new stocks
add_frame = tk.Frame(master=window, padx=10, pady=10)

input_code_help = tk.Label(text="Stock Code", master=add_frame)
input_code_field = tk.Entry(master=add_frame)
input_quantity_help = tk.Label(text="Quantity", master=add_frame)
input_quantity_field = tk.Entry(master=add_frame)
input_price_help = tk.Label(text="Price Paid", master=add_frame)
input_price_field = tk.Entry(master=add_frame)
submit_button = tk.Button(text="Add Stock", master=add_frame, command=lambda : add_stock())
add_successful_text = tk.Label(text="Stock added successfully! Please restart the application to see the new stock.", master=add_frame)

input_code_help.grid(row=0, column=0)
input_code_field.grid(row=1, column=0)
input_quantity_help.grid(row=0, column=1)
input_quantity_field.grid(row=1, column=1)
input_price_help.grid(row=0, column=2)
input_price_field.grid(row=1, column=2)
submit_button.grid(row=1, column=3)

# Display stored stock widgets
for i in range(len(table)):
    for j in range(len(stocks[0])):
        stocks[i][j].grid(row=i, column=j)

title_frame.grid(row=0, column=0)
stock_info_frame.grid(row=1, column=0)
add_frame.grid(row=3, column=0)

window.mainloop()

# Close database and exit
close_database(connection)
