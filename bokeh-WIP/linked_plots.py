from functools import lru_cache

import os

import pandas as pd

from bokeh.resources import INLINE
from bokeh.io import output_notebook
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import PreText, Select
from bokeh.plotting import figure

output_notebook(INLINE, hide_banner=True)

DATA_DIR = os.path.join(os.environ['HOME'], 'DATA', 'quantquote_daily_sp500_83986', 'daily')

DEFAULT_TICKERS = ['AAPL', 'GOOG', 'INTC', 'BRCM', 'YHOO']

def nix(val, lst):
    return [x for x in lst if x != val]

@lru_cache()
def load_ticker(ticker):
    fname = os.path.join(DATA_DIR, 'table_%s.csv' % ticker.lower())
    data = pd.read_csv(fname, header=None, parse_dates=['date'],
                       names=['date', 'foo', 'o', 'h', 'l', 'c', 'v'])
    data = data.set_index('date')
    return pd.DataFrame({ticker: data.c, ticker+'_returns': data.c.diff()})

@lru_cache()
def get_data(t1, t2):
    df1 = load_ticker(t1)
    df2 = load_ticker(t2)
    data = pd.concat([df1, df2], axis=1)
    data = data.dropna()
    data['t1'] = data[t1]
    data['t2'] = data[t2]
    data['t1_returns'] = data[t1+'_returns']
    data['t2_returns'] = data[t2+'_returns']
    return data

class linked_plots(object):
    def setup_widgets(self):
        self.stats = PreText(text='', width=500)
        self.ticker1 = Select(value='AAPL', options=nix('GOOG', DEFAULT_TICKERS))
        self.ticker2 = Select(value='GOOG', options=nix('AAPL', DEFAULT_TICKERS))

    def setup_plots(self):
        self.source = ColumnDataSource(data=dict(date=[], t1=[], t2=[], t1_returns=[], t2_returns=[]))
        self.source_static = ColumnDataSource(data=dict(date=[], t1=[], t2=[], t1_returns=[], t2_returns=[]))

        self.corr = figure(plot_width=350, plot_height=350,
                      tools='pan,wheel_zoom,box_select,reset')
        self.corr.circle('t1_returns', 't2_returns', size=2, source=self.source,
                    selection_color="orange", alpha=0.6, nonselection_alpha=0.1, selection_alpha=0.4)
 
        tools = 'pan,wheel_zoom,xbox_select,reset'
        self.ts1 = figure(plot_width=900, plot_height=200, tools=tools, x_axis_type='datetime', active_drag="xbox_select")
        self.ts1.line('date', 't1', source=self.source_static)
        self.ts1.circle('date', 't1', size=1, source=self.source, color=None, selection_color="orange")

        self.ts2 = figure(plot_width=900, plot_height=200, tools=tools, x_axis_type='datetime', active_drag="xbox_select")
        self.ts2.x_range = self.ts1.x_range
        self.ts2.line('date', 't2', source=self.source_static)
        self.ts2.circle('date', 't2', size=1, source=self.source, color=None, selection_color="orange")

    # set up callbacks
    def ticker1_change(self, attrname, old, new):
        self.ticker2.options = nix(new, DEFAULT_TICKERS)
        self.update()

    def ticker2_change(self, attrname, old, new):
        self.ticker1.options = nix(new, DEFAULT_TICKERS)
        self.update()

    def update(self, selected=None):
        t1, t2 = self.ticker1.value, self.ticker2.value

        data = get_data(t1, t2)
        self.source.data = self.source.from_df(data[['t1', 't2', 't1_returns', 't2_returns']])
        self.source_static.data = self.source.data

        self.update_stats(data, t1, t2)

        self.corr.title.text = '%s returns vs. %s returns' % (t1, t2)
        self.ts1.title.text, self.ts2.title.text = t1, t2

    def update_stats(self, data, t1, t2):
        self.stats.text = str(data[[t1, t2, t1+'_returns', t2+'_returns']].describe())



    def selection_change(self, attrname, old, new):
        t1, t2 = self.ticker1.value, self.ticker2.value
        data = get_data(t1, t2)
        selected = self.source.selected.indices
        if selected:
            data = data.iloc[selected, :]
        self.update_stats(data, t1, t2)
        
    def make_ticker_plot(self, doc):
        # set up layout
        widgets = column(self.ticker1, self.ticker2, self.stats)
        main_row = row(self.corr, widgets)
        series = column(self.ts1, self.ts2)
        layout = column(main_row, series)
        doc.add_root(layout)

    def __init__(self):
        self.setup_widgets()
        self.setup_plots()
        self.ticker1.on_change('value', self.ticker1_change)
        self.ticker2.on_change('value', self.ticker2_change)
        self.source.on_change('selected', self.selection_change)

        # initialize
        self.update()