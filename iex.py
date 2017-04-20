import io
import os
import requests
import pandas as pd
from bokeh.models import ColumnDataSource, HoverTool, ResizeTool, SaveTool, CustomJS
from bokeh.models.widgets import Paragraph, Panel, Tabs, TextInput, Button, DataTable, TableColumn, DateFormatter
from bokeh.plotting import figure, curdoc
from bokeh.layouts import row, column, widgetbox, layout



def get_last_price(symbol):
    payload = {
        "format": "csv",
        "symbols": symbol
    }
    endpoint = "tops/last"

    if symbol == "TEST":
        prices_df = get_test_data()
        return prices_df

    raw = requests.get(base + endpoint, params=payload)
    raw = io.BytesIO(raw.content)
    prices_df = pd.read_csv(raw, sep=",")
    prices_df["time"] = pd.to_datetime(prices_df["time"], unit="ms")
    prices_df["display_time"] = prices_df["time"].dt.strftime("%m-%d-%Y %H:%M:%S.%f")

    return prices_df


def get_test_data():
    choices = [-.5, -.25, 0, .25, .5]
    delta = np.random.choice(choices)
    
    return prices_df

def initialize_data(ticker):
    prices_df = get_last_price(ticker)
    data = ColumnDataSource(dict(index=[0], 
                                 time=prices_df["time"], 
                                 display_time=prices_df["display_time"],
                                 price=prices_df['price']))
    return data


def update_ticker():
    global TICKER
    global i

    TICKER = ticker_textbox.value
    i = 0

    price_plot.title.text = "IEX Real-Time Price: " + ticker_textbox.value
    new_data = initialize_data(TICKER)
    data.data = new_data.data
    return


i = 0
def update_price():
    global i
    i += 1
    new_price = get_last_price(symbol=TICKER)
    
    if (new_price['display_time'].values[0] == data.data['display_time'][-1]):
        return

    data_dict = dict(index=[i],
                     time=new_price["time"],
                     display_time=new_price["display_time"],
                     price=new_price["price"])
    data.stream(data_dict, 10000)

    return


TICKER = "SPY"
base = "https://api.iextrading.com/1.0/"
data = initialize_data(TICKER)

columns = [
    TableColumn(field="time",
                title="Time",
                formatter=DateFormatter(format="@")),
    TableColumn(field="display_time", title="Display Time"),
    TableColumn(field="price", title="Trade Price")
]

data_table = DataTable(source=data, columns=columns, width=800)


hover = HoverTool(tooltips=[
    ("Time", "@display_time"),
    ("IEX Real-Time Price", "@price")])

price_plot = figure(plot_width=800,
                    plot_height=200,
                    x_axis_type='datetime',
                    tools=[hover, ResizeTool(), SaveTool()],
                    title="Real-Time Price Plot")

price_plot.line(source=data, x='time', y='price')
price_plot.xaxis.axis_label = "Time"
price_plot.yaxis.axis_label = "IEX Real-Time Price"
price_plot.title.text = "IEX Real Time Price: " + TICKER

ticker_textbox = TextInput(placeholder="Ticker")

update = Button(label="Update")
update.on_click(update_ticker)

download = Button(label="Download", button_type="success")
download.callback = CustomJS(args=dict(source=data),
                             code=open(os.path.join(os.path.dirname(__file__), "export.js")).read())

inputs = widgetbox([ticker_textbox, update, download], width=200)
table = widgetbox(data_table)
view = column(price_plot, table)
dashboard = row(inputs, view)

curdoc().add_root(dashboard)
curdoc().title = "Real-Time Price Plot from IEX"
curdoc().add_periodic_callback(update_price, 1000)
