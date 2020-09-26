import pandas as pd
from functools import reduce

def get_country_ts(country, dataframes, columns):
    """
    
    Extract data for specific country.
    
    Notes
    -----
    Apply backfill to NaN's.
    
    """
    
    cols = ['Date'] + columns
    ctry = list()
    for df in dataframes:
        tmp = df.loc[:, ['Date', country]]
        ctry.append(tmp)        
    ctry = reduce(lambda x, y: pd.merge(x, y, on='Date', how='outer'), ctry)    
    ctry.columns = cols
    ctry = ctry.fillna(method='bfill')
    
    return ctry


def get_high_mort(df):
    """

    Extract mortality rate

    """

    high_mort = df[['Country', 'Mortality', 'Confirmed']]
    high_mort = high_mort.loc[high_mort['Confirmed'] > 1000, :]
    high_mort = high_mort.drop('Confirmed', axis=1)
    high_mort = high_mort.sort_values('Mortality', ascending=False)
    high_mort = high_mort.reset_index(drop=True)
    high_mort.columns = ['Country', 'Mortality Rate']
    high_mort = high_mort.head(10)    
    
    return high_mort