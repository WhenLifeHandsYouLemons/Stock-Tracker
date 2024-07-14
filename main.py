# If debug is enabled, the program will not search for stock information online
offline_mode = False

from datetime import datetime           # For getting the current date and time
import sqlite3                          # For database management
from requests_html import HTMLSession   # https://github.com/psf/requests-html  # For web scraping
from tkinter import *                   # For GUI
from tkinter.ttk import *               # For GUI
from matplotlib.figure import Figure    # For plotting stock charts
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # For plotting stock charts

# API keys (stored in secrets.txt)
try:
    with open("secrets.txt", "r") as file:
        exchange_rate_api_key = file.readline()
except:
    exchange_rate_api_key = "Error"


class StockInfoWindow():
    def __init__(self, master, stock_code: str) -> None:
        self.stock_code = stock_code

        self.master = Toplevel(master)
        self.master.configure()
        self.master.title(f"{fetchStockName(stock_code)} Stock Information")

        self.font_family = "Arial"
        self.body_font_size = 12
        self.title_font_size = 18

        self.pageItems()

        # Put everything above this
        self.master.mainloop()

    def pageItems(self) -> None:
        title_frame = Frame(master=self.master, padding=15)
        txt_title = Label(text=f"{fetchStockName(self.stock_code)} ({self.stock_code}) Stock Information", master=title_frame, font=(self.font_family, self.title_font_size))
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
            Button(text=chart_range_types[i][1], master=chart_options_frame, command=lambda range_option=chart_range_types[i]: self.changeChartRange(range_option)).grid(row=i+1, column=0)

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
            Checkbutton(text=self.chart_data_types[i][1], master=chart_options_frame, variable=self.chart_data_visibility[i], command=lambda: self.toggleChartPriceTypes()).grid(row=i+len(chart_range_types)+3, column=0)

        chart_options_frame.grid(row=0, column=0)

        # Stock chart
        self.fig = Figure(figsize = (10, 5), dpi = 75)
        self.plot1 = self.fig.subplots(1, 1)
        self.plot1.set_autoscaley_on(False)
        self.chart_canvas = FigureCanvasTkAgg(self.fig, master=stock_info_frame)

        self.toggleChartPriceTypes()

        # https://stackoverflow.com/a/47166787
        self.fig.canvas.mpl_connect("motion_notify_event", self.hover)

        self.chart_canvas.get_tk_widget().grid(row=0, column=1)

        # Show the current, opening, closing, high, and low prices
        self.fetchStockData()

        # Get live stock data
        self.master.after(2000, self.fetchLiveStockData)
        self.current_stock_price_var = StringVar(value="Current Price: Loading...")

        current_stock_price = Label(textvariable=self.current_stock_price_var, justify="left", master=stock_info_frame, font=(self.font_family, self.body_font_size))
        current_stock_price.grid(row=1, column=1, sticky="W")

        opening_stock_price = Label(text=f"Opening Price: {self.fetchStockData()[1]}", justify="left", master=stock_info_frame, font=(self.font_family, self.body_font_size))
        opening_stock_price.grid(row=2, column=1, sticky="W")

        closing_stock_price = Label(text=f"Previous Closing Price: {self.fetchStockData()[2]}", justify="left", master=stock_info_frame, font=(self.font_family, self.body_font_size))
        closing_stock_price.grid(row=3, column=1, sticky="W")

        high_stock_price = Label(text=f"High Price: {self.fetchStockData()[3]}", justify="left", master=stock_info_frame, font=(self.font_family, self.body_font_size))
        high_stock_price.grid(row=4, column=1, sticky="W")

        # Add the frames to the screen
        title_frame.grid(row=0, column=0)
        stock_info_frame.grid(row=1, column=0)

    def fetchStockData(self) -> list:
        URL = f"https://query2.finance.yahoo.com/v6/finance/options/{self.stock_code}"

        try:
            result = search(URL)
            info = result["optionChain"]["result"][0]["quote"]
        except:
            return ["Error" for i in range(5)]

        # Returns, current price, opening price, closing price, high price, low price
        return [info["regularMarketPrice"], info["regularMarketOpen"], info["regularMarketPreviousClose"], info["regularMarketDayHigh"], info["regularMarketDayLow"]]

    def fetchLiveStockData(self) -> None:
        URL = f"https://query2.finance.yahoo.com/v6/finance/options/{self.stock_code}"

        try:
            result = search(URL)
            info = str(result["optionChain"]["result"][0]["quote"]["regularMarketPrice"])

            self.current_stock_price_var.set(f"Current Price: {info}")

            # Rerun the function every minute
            self.master.after(60000, self.fetchLiveStockData)
        except:
            info = "Error! Please try again later."

            self.current_stock_price_var.set(f"Current Price: {info}")

            # Rerun the function every 2 minutes in case of an error
            self.master.after(120000, self.fetchLiveStockData)

    def fetchStockChartData(self, duration: str, metric_type: str) -> list:
        if duration == "1d":
            interval = "1m"
        elif duration == "5d" or duration == "1mo" or duration == "3mo" or duration == "6mo" or duration == "1y" or duration == "ytd":
            interval = "1d"
        elif duration == "2y" or duration == "5y":
            interval = "1wk"
        elif duration == "max":
            interval = "1mo"
        else:
            interval = ""

        URL = f"https://query2.finance.yahoo.com/v8/finance/chart/{self.stock_code}?metrics={metric_type}?&range={duration}&interval={interval}"
        result = search(URL)

        try:
            time = [datetime.fromtimestamp(x) for x in result["chart"]["result"][0]["timestamp"]]
            prices = result["chart"]["result"][0]["indicators"]["quote"][0][metric_type]
        except:
            time, prices = [], []

        return time, prices

    def changeChartRange(self, chart_range: str) -> None:
        self.plot1.clear()
        self.lines = []

        for i in self.chart_data_visibility:
            if bool(int(i.get())):
                chart_data = self.chart_data_types[self.chart_data_visibility.index(i)]
                time, data = self.fetchStockChartData(chart_range[0], chart_data[0])
                self.line = self.plot1.plot(time, data, "-", color=self.changeGraphColor(chart_data[0]), label=chart_data[1])

                # Fill in missing data
                for i, val in enumerate(data):
                    if val == None:
                        data[i] = data[i-1]
                    elif i == 0 and val == None:
                        data[i] = 0

                xmin, xmax, ymin, ymax = self.plot1.axis()
                if min(data) < ymin:
                    ymin = min(data)
                if max(data) > ymax:
                    ymax = max(data)

                self.plot1.axes.set_ylim([ymin, ymax])

                self.plot1.fill_between(time, data, color=self.changeGraphColor(chart_data[0]), alpha=0.1)

        self.plot1.set_title(f"{fetchStockName(self.stock_code)} ({self.stock_code}) Stock Chart ({chart_range[1]})")
        self.showMainChartInfo()

        self.selected_chart_range.set(chart_range)

        self.chart_canvas.draw()

    def toggleChartPriceTypes(self) -> None:
        # Change the chart data to the selected data
        self.plot1.clear()
        self.lines = []

        for i in self.chart_data_visibility:
            if bool(int(i.get())):
                chart_data = self.chart_data_types[self.chart_data_visibility.index(i)]
                time, data = self.fetchStockChartData(str(self.selected_chart_range.get().split(", ")[0][2:-1]), chart_data[0])
                self.line = self.plot1.plot(time, data, "-", color=self.changeGraphColor(chart_data[0]), label=chart_data[1])

                # Fill in missing data
                for i, val in enumerate(data):
                    if val == None:
                        data[i] = data[i-1]
                    elif i == 0 and val == None:
                        data[i] = 0

                xmin, xmax, ymin, ymax = self.plot1.axis()
                if min(data) < ymin:
                    ymin = min(data)
                if max(data) > ymax:
                    ymax = max(data)

                self.plot1.axes.set_ylim([ymin, ymax])

                self.plot1.fill_between(time, data, color=self.changeGraphColor(chart_data[0]), alpha=0.1)

        self.plot1.set_title(f"{fetchStockName(self.stock_code)} ({self.stock_code}) Stock Chart ({str(self.selected_chart_range.get().split(', ')[1][1:-2])})")
        self.showMainChartInfo()

        self.chart_canvas.draw()

    def showMainChartInfo(self) -> None:
        self.plot1.set_ylabel("Price")
        self.plot1.set_xlabel("Time")
        self.plot1.grid(True, which="both", linestyle="--", linewidth=0.5)

        for i in self.chart_data_visibility:
            if bool(int(i.get())):
                self.plot1.legend()

        self.annot = self.plot1.axes.annotate("", xy=(0,0), xytext=(-20,20),textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)

    def changeGraphColor(self, data: str) -> str:
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

    # https://stackoverflow.com/a/47166787
    def updateAnnotation(self, ind):
        x,y = self.line[0].get_data()
        self.annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
        text = f"{str(x[ind['ind'][0]])}: {str(round(float(y[ind['ind'][0]]), 2))}"
        self.annot.set_text(text)
        self.annot.get_bbox_patch().set_alpha(0.75)

    def hover(self, event):
        vis = self.annot.get_visible()
        if event.inaxes == self.plot1:
            cont, ind = self.line[0].contains(event)
            if cont:
                self.updateAnnotation(ind)
                self.annot.set_visible(True)
                self.fig.canvas.draw_idle()
            else:
                if vis:
                    self.annot.set_visible(False)
                    self.fig.canvas.draw_idle()

class StockNotFoundError(Exception):
    pass


def openDatabase(filename: str) -> sqlite3.Connection:
    connection = sqlite3.connect(filename)
    connection.row_factory = sqlite3.Row
    return connection

def readDatabase(connection: sqlite3.Connection, sql: str) -> 'list[dict]':
    cursor = connection.cursor()
    cursor.execute(sql)
    result = [ dict(row) for row in cursor.fetchall() ]
    return result

def writeDatabase(connection: sqlite3.Connection, sql: str) -> int:
    cursor = connection.cursor()
    rows_affected = cursor.execute(sql).rowcount
    connection.commit()
    return rows_affected

def closeDatabase(connection: sqlite3.Connection) -> None:
    connection.close()

def search(URL: str) -> dict:
    # If debug is enabled, don't search (as if it's offline)
    if offline_mode:
        return ""

    # Search the given link and return the data in a dictionary
    session = HTMLSession()
    result = session.get(URL)
    result = result.json()
    return result

def fetchStockName(stock_code: str) -> str:
    URL = f"https://query2.finance.yahoo.com/v6/finance/options/{stock_code}"
    result = search(URL)

    # Get the stock's name
    try:
        name = result["optionChain"]["result"][0]["quote"]["shortName"]
    except:
        name = "Error"

    return name

def fetchStockCurrency(stock_code: str) -> str:
    URL = f"https://query2.finance.yahoo.com/v6/finance/options/{stock_code}"
    result = search(URL)

    # Get the stock's trading currency
    try:
        currency = result["optionChain"]["result"][0]["quote"]["currency"]
    except:
        currency = "Error"

    return currency

def fetchExchangeRate(currency1: str, currency2: str) -> 'float | str':
    URL = f"https://v6.exchangerate-api.com/v6/{exchange_rate_api_key}/latest/{currency1}"
    result = search(URL)

    # Get the exchange rate between two currencies
    try:
        rate = float(result["conversion_rates"][currency2])
    except:
        rate = "Error"

    return rate

def addStockToPortfolio() -> None:
    code = input_code_field.get()
    price = float(input_price_field.get())
    quantity = int(input_quantity_field.get())
    true_currency = fetchStockCurrency(code)
    currency = currency_field.get()

    if "" in [code, currency] or price <= 0 or quantity <= 0:
        return

    if true_currency != "Error":
        exchange_rate = fetchExchangeRate(currency, true_currency)
        if exchange_rate != "Error":
            price *= exchange_rate
            currency = true_currency

    # Add to the database
    writeDatabase(connection, f"INSERT INTO stocks (stock_code, stock_name, quantity, buying_price, currency) VALUES ('{code}', '{fetchStockName(code)}', {quantity}, {price}, '{currency}');")
    add_successful_text = Label(text=f"{quantity} {code} stocks added successfully! Please restart the application to update your portfolio.", master=add_frame, font=(font_family, body_font_size))
    add_successful_text.grid(row=2, columnspan=4)

def removeStockFromPortfolio(stock_code: str) -> None:
    # Remove from database
    writeDatabase(connection, f"DELETE FROM stocks WHERE stock_code='{stock_code}';")
    remove_successful_text = Label(text=f"{stock_code} stocks removed successfully! Please restart the program to remove it from your portfolio.", master=window, font=(font_family, body_font_size))
    remove_successful_text.grid(row=2, column=0)

def updateStockLastUpdated(stock_code: str) -> None:
    writeDatabase(connection, f"UPDATE stocks SET last_updated=datetime('now', 'localtime') WHERE stock_code='{stock_code}';")

def updateStockPrice(stock_code: str, current_price: float) -> None:
    writeDatabase(connection, f"UPDATE stocks SET selling_price={current_price} WHERE stock_code='{stock_code}';")

def updateStockPriceChange(stock_code: str, price_change: str) -> None:
    writeDatabase(connection, f"UPDATE stocks SET price_change='{price_change}' WHERE stock_code='{stock_code}';")

# Open database
file_name = "stocks.db"
connection = openDatabase(file_name)
table = readDatabase(connection, "SELECT * FROM stocks;")

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
stocks = [[
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
]]
stocks_vars = []


def getLiveStockData(i) -> None:
    stock = table[i]
    stock_code = stock["stock_code"]

    URL = f"https://query2.finance.yahoo.com/v6/finance/options/{stock_code}"

    try:
        if stock["stock_name"] == "Error":
            raise StockNotFoundError

        result = search(URL)

        # For stock price
        stock_price = str(result["optionChain"]["result"][0]["quote"]["regularMarketPrice"])

        stocks_vars[i][0].set(stock_price)

        updateStockPrice(stock_code, float(stocks_vars[i][0].get()))

        # For stock price change
        stock_price_change = result["optionChain"]["result"][0]["quote"]["regularMarketChangePercent"]

        if stock_price_change > 0:
            stocks_vars[i][1][0].set("Increase")
            stocks_vars[i][1][1].set("#060")
        elif stock_price_change < 0:
            stocks_vars[i][1][0].set("Decrease")
            stocks_vars[i][1][1].set("#F11")
        else:
            stocks_vars[i][1][0].set("No change")
            stocks_vars[i][1][1].set("#000")

        updateStockPriceChange(stock_code, stocks_vars[i][1][0].get())

        # For profit/loss calculation
        try:
            stocks_vars[i][2][0].set(str(round(((float(stocks_vars[i][0].get()) * int(stock["quantity"])) - float(stock["buying_price"])), 2)))

            if "-" in stocks_vars[i][2][0].get():
                stocks_vars[i][2][1].set("#F11")
            else:
                stocks_vars[i][2][1].set("#060")
        except:
            stocks_vars[i][2][0].set("Error")
            stocks_vars[i][2][1].set("#000")

        # For last updated time
        updateStockLastUpdated(stock_code)
        stocks_vars[i][3].set(str(datetime.now()).split(".")[0])

        # Rerun the function every minute
        window.after(60000, lambda i=i: getLiveStockData(i))
    except StockNotFoundError:
        stocks_vars[i][0].set("Error")
        stocks_vars[i][1][0].set("Error")
        stocks_vars[i][1][1].set("#222")
        stocks_vars[i][2][0].set("Error")
        stocks_vars[i][2][1].set("#000")
        stocks_vars[i][3].set("Error")
    except:
        stocks_vars[i][3].set(stock["last_updated"])

        # Rerun the function every 2 minutes in case of an error
        window.after(120000, lambda i=i: getLiveStockData(i))

# Get all the stock information and save it
print("\nGetting latest stock information, please wait...")
i = 0
while i < len(table):
    stock = table[i]

    stocks_vars.append([
        StringVar(),                # stock price
        [StringVar(), StringVar()], # [price change, text colour]
        [StringVar(), StringVar()], # [profit/loss, text colour]
        StringVar(),                # last updated
    ])

    getLiveStockData(i)

    stocks.append([
        Button(text="View Info", master=stock_info_frame, padding=padding, command=lambda code=stock["stock_code"]: StockInfoWindow(window, code)),
        Label(text=stock["stock_code"], master=stock_info_frame, padding=padding, font=(font_family, body_font_size)),
        Label(text=stock["stock_name"], master=stock_info_frame, padding=padding, font=(font_family, body_font_size)),
        Label(text=stock["currency"], master=stock_info_frame, padding=padding, font=(font_family, body_font_size)),
        Label(textvariable=stocks_vars[i][0], master=stock_info_frame, padding=padding, font=(font_family, body_font_size)),
        Label(text=stock["quantity"], master=stock_info_frame, padding=padding, font=(font_family, body_font_size)),
        Label(text=stock["buying_price"], master=stock_info_frame, padding=padding, font=(font_family, body_font_size)),
        Label(textvariable=stocks_vars[i][1][0], master=stock_info_frame, padding=padding, foreground=stocks_vars[i][1][1].get(), font=(font_family, body_font_size, "bold")),
        Label(textvariable=stocks_vars[i][2][0], master=stock_info_frame, padding=padding, foreground=stocks_vars[i][2][1].get(), font=(font_family, body_font_size)),
        Label(textvariable=stocks_vars[i][3], master=stock_info_frame, padding=padding, font=(font_family, body_font_size)),
        Button(text="Remove", master=stock_info_frame, padding=padding, command=lambda code=stock["stock_code"]: removeStockFromPortfolio(code)),
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
submit_button = Button(text="Add Stock", master=add_frame, command=lambda : addStockToPortfolio())

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
closeDatabase(connection)
