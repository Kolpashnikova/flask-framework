from flask import Flask, render_template, request, redirect
import os
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, SelectField
from wtforms.validators import DataRequired
import simplejson as json
import datetime
import bokeh
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.resources import CDN
import requests

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
Bootstrap(app)

def stock_graph(ticker, price_type, month, year):
    url = ("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY"
    + "&symbol="
    + ticker
    + "&outputsize=full&apikey="
    + os.getenv('ALPHA_KEY'))
    full_data = json.loads(requests.get(url).text)
    if "Error Message" in full_data:
        return 1

    all_dates = map(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'),
                    full_data['Time Series (Daily)'].keys())
    month_year = datetime.datetime.strptime(month + ' ' + year, '%B %Y')

    dates = []
    for date in all_dates:
        if date.month == month_year.month and date.year == month_year.year:
            dates.append(date)
    dates = sorted(dates)

    prices = []
    for date in dates:
        date_string = date.strftime('%Y-%m-%d')
        if price_type=="open":
        	price = full_data['Time Series (Daily)'][date_string]['1. open']
        elif price_type=="high":
        	price = full_data['Time Series (Daily)'][date_string]['2. high']
        elif price_type=="low":
        	price = full_data['Time Series (Daily)'][date_string]['3. low']
        elif price_type=="close":
        	price = full_data['Time Series (Daily)'][date_string]['4. close']
        price = float(price)
        prices.append(price)

    tools = 'pan,wheel_zoom,xbox_select,reset'

    t = (price_type.capitalize() + " Prices of " + ticker + " for the month of " + month + " "
         + year)
    curdoc().theme = 'dark_minimal'
    p = figure(x_axis_type="datetime", title=t, width=600, height=600, tools=tools)
    p.grid.grid_line_alpha=0.3
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Price'

    p.line(dates, prices, legend_label=ticker, color="black")
    p.legend.location = "top_right"

    return(p)

class StockForm(FlaskForm):
    ticker = StringField('Enter stock ticker code (e.g., AAPL, C, HPQ, INTC):', validators=[DataRequired()])
    month = DateField('Enter month (MM/YYYY):', format='%m/%Y', validators=[DataRequired()])
    price_type = SelectField('Price Type', choices=[('open', 'Open'), ('high', 'High'), ('low', 'Low'), ('close', 'Close')])
    submit = SubmitField('Graph Price')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = StockForm()
    output = ""
    if form.validate_on_submit():
        ticker = form.ticker.data
        date = form.month.data
        price_data = form.price_type.data
        month = date.strftime('%B')
        year = date.strftime('%Y')
        p = stock_graph(ticker, price_data, month, year)
        if p == 1:
            output = "Wrong input. Try to check your stock ticker name."
        else:
            script, div = components(p)
            output = script + div

    return render_template('index.html', form=form, output=output)

if __name__ == '__main__':
  app.run(port=33507)
