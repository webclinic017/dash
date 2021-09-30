###########
# Imports #
###########
import os, pickle
os.chdir('C:/')

from MINIONS.dwx_graphics_helpers import DWX_Graphics_Helpers
from plotly.offline import init_notebook_mode
from scipy.stats import zscore
import pickle, warnings
import pandas as pd
import numpy as np

################################
# Some configuration for later #
################################
warnings.simplefilter("ignore") # Suppress warnings
init_notebook_mode(connected=True)
################################

# Create DWX Graphics Helpers object for later
_graphics = DWX_Graphics_Helpers()

# Load DataFrame of DARWIN quotes (Daily precision) from pickle archive.
quotes = pickle.load(open('../DATA/jn_all_quotes_active_deleted_12062019.pkl', 'rb'))

# Remove non-business days (consider Monday to Friday only)
quotes = quotes[quotes.index.dayofweek < 5]

# Load FX Market Volatility data upto 2019-06-17 (for evaluation later)
voldf = pd.read_csv('../DATA/volatility.beginning.to.2019-06-17.csv',
                    index_col=0,
                    parse_dates=True,
                    infer_datetime_format=True)

# Print DARWINs in dataset
print(f'DARWIN assets in dataset: {quotes.shape[1]}') # 5331 DARWINs

# Print list of DARWINs in DataFrame
print(f'\nDARWIN Symbols: \n{quotes.columns}')

# Select an example DARWIN and plot its Quotes
test_darwin = 'LVS.4.20'

# Plot test DARWIN Quotes
_graphics._plotly_dataframe_scatter_(
                            _df=pd.DataFrame(quotes[test_darwin].dropna()),
                            _x_title = "Date / Time",
                            _y_title = "Quote",
                            _main_title = f'${test_darwin} Quotes',
                            _plot_only = True)

print(quotes[test_darwin].tail())
pass; # Suppress object output