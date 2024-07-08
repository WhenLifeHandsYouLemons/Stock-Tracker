# If debug is enabled, the program will not search for stock information online
debug = False

from datetime import datetime   # For getting the current date and time
import sqlite3  # For database management
from requests_html import HTMLSession   # https://github.com/psf/requests-html  # For web scraping
from tkinter import *       # For GUI
from tkinter.ttk import *   # For GUI
from matplotlib.figure import Figure    # For plotting stock charts
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg   # For plotting stock charts
import matplotlib.dates as mdates   # For plotting stock charts

# API keys (stored in secrets.txt)
try:
    with open("secrets.txt", "r") as file:
        exchange_rate_api_key = file.readline()
except:
    exchange_rate_api_key = "Error"


class StockInfoWindow():
    def __init__(self, master, stock_code) -> None:
        self.stock_code = stock_code

        self.master = Toplevel(master)
        self.master.configure()
        self.master.title(f"{stock_code} Stock Information")

        self.font_family = "Arial"
        self.body_font_size = 12
        self.title_font_size = 18

        self.page_items()

        # Put everything above this
        self.master.mainloop()

    def page_items(self) -> None:
        title_frame = Frame(master=self.master, padding=15)
        txt_title = Label(text=f"{self.stock_code} Stock Information", master=title_frame, font=(self.font_family, self.title_font_size))
        txt_title.pack()

        stock_info_frame = Frame(master=self.master, padding=5)

        # Buttons to change chart type
        chart_options_frame = Frame(master=stock_info_frame, padding=5)
        chart_range_label = Label(text="Chart Type:", master=chart_options_frame, font=(self.font_family, self.body_font_size))
        chart_range_label.grid(row=0, column=0)

        chart_range_types = [["1d", "1 Day"],
                             ["5d", "5 Days"],
                             ["1mo", "1 Month"],
                             ["3mo", "3 Months"],
                             ["6mo", "6 Months"],
                             ["1y", "1 Year"],
                             ["2y", "2 Years"],
                             ["5y", "5 Years"],
                             ["ytd", "Year to Date"],
                             ["max", "Max"]]

        self.selected_chart_range = StringVar()
        self.selected_chart_range.set(chart_range_types[0])

        for i in range(len(chart_range_types)):
            Button(text=chart_range_types[i][1], master=chart_options_frame, command=lambda range_option=chart_range_types[i]: self.change_chart_range(range_option)).grid(row=i+1, column=0)

        # Small spacer between options
        chart_option_spacer = Label(text="", master=chart_options_frame)
        chart_option_spacer.grid(row=len(chart_range_types)+1, column=0)

        # Low, high, opening, closing options
        chart_data_label = Label(text="Data:", master=chart_options_frame, font=(self.font_family, self.body_font_size))
        chart_data_label.grid(row=len(chart_range_types)+2, column=0)

        self.chart_data_types = [["low", "Low Price"],
                            ["high", "High Price"],
                            ["open", "Opening Price"],
                            ["close", "Closing Price"]]
        self.chart_data_visibility = [StringVar(value=False) for i in range(len(self.chart_data_types))]
        self.chart_data_visibility[-1].set(True)

        for i in range(len(self.chart_data_types)):
            Checkbutton(text=self.chart_data_types[i][1], master=chart_options_frame, variable=self.chart_data_visibility[i], command=lambda: self.toggle_chart_data()).grid(row=i+len(chart_range_types)+3, column=0)

        chart_options_frame.grid(row=0, column=0)

        # Stock chart
        self.chart = Figure(figsize = (10, 5), dpi = 75)
        self.plot1 = self.chart.add_subplot()
        self.chart_canvas = FigureCanvasTkAgg(self.chart, master=stock_info_frame)

        self.toggle_chart_data()

        self.chart_canvas.get_tk_widget().grid(row=0, column=1)

        #! Add live ticker value for current stock price here
        #! Add opening, closing, high, and low prices here

        title_frame.grid(row=0, column=0)
        stock_info_frame.grid(row=1, column=0)

    def get_stock_chart_data(self, duration, metric_type) -> list:
        if duration == "1d" or duration == "5d":
            interval = "1m"
        elif duration == "1mo" or duration == "3mo" or duration == "6mo" or duration == "1y" or duration == "ytd":
            interval = "1d"
        elif duration == "2y" or duration == "5y":
            interval = "1wk"
        elif duration == "max":
            interval = "1mo"

        URL = f"https://query2.finance.yahoo.com/v8/finance/chart/{self.stock_code}?metrics={metric_type}?&range={duration}&interval={interval}"
        result = search(URL)

        time = [datetime.fromtimestamp(x) for x in result["chart"]["result"][0]["timestamp"]]
        prices = result["chart"]["result"][0]["indicators"]["quote"][0][metric_type]

        return time, prices

    def change_chart_range(self, chart_range) -> None:
        self.plot1.clear()

        for i in self.chart_data_visibility:
            if bool(int(i.get())):
                chart_data = self.chart_data_types[self.chart_data_visibility.index(i)]
                time, data = self.get_stock_chart_data(chart_range[0], chart_data[0])
                self.plot1.plot(time, data, "-", color=self.change_chart_color(chart_data[0]), label=chart_data[1])

        self.plot1.set_ylabel("Price")
        self.plot1.set_xlabel("Time")
        self.plot1.grid(True, which="both", linestyle="--", linewidth=0.5)

        self.selected_chart_range.set(chart_range)

        self.chart_canvas.draw()

    def toggle_chart_data(self) -> None:
        # Change the chart data to the selected data
        self.plot1.clear()

        for i in self.chart_data_visibility:
            if bool(int(i.get())):
                chart_data = self.chart_data_types[self.chart_data_visibility.index(i)]
                time, data = self.get_stock_chart_data(str(self.selected_chart_range.get().split(", ")[0][2:-1]), chart_data[0])
                self.plot1.plot(time, data, "-", color=self.change_chart_color(chart_data[0]), label=chart_data[1])

        self.plot1.set_ylabel("Price")
        self.plot1.set_xlabel("Time")
        self.plot1.grid(True, which="both", linestyle="--", linewidth=0.5)

        self.chart_canvas.draw()

    def change_chart_color(self, data) -> str:
        if data == "close":
            return "black"
        elif data == "open":
            return "grey"
        elif data == "high":
            return "green"
        elif data == "low":
            return "red"
        else:
            return "black"

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
    add_successful_text = Label(text=f"{quantity} {code} stocks added successfully! Please restart the application to update your portfolio.", master=add_frame, font=(font_family, body_font_size))
    add_successful_text.grid(row=2, columnspan=4)

def remove_stock(stock_code):
    # Remove from database
    write_database(connection, f"DELETE FROM stocks WHERE stock_code='{stock_code}';")
    remove_successful_text = Label(text=f"{stock_code} stocks removed successfully! Please restart the program to remove it from your portfolio.", master=window, font=(font_family, body_font_size))
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
body_font_size = 12
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
        Button(text="View Info", master=stock_info_frame, padding=padding, command=lambda stock_code=stock["stock_code"]: StockInfoWindow(window, stock_code)),
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
