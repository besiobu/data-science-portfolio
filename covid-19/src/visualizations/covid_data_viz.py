from functools import reduce

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import display
from matplotlib.dates import DateFormatter
from scipy.stats import linregress

from utils import get_vlines

class CovidDataViz(object):
    """

    A class to make plots from processed COVID-19 and World Bank data.

    """

    def __init__(self, path='../data/processed'):

        self.path = path
        self.data = dict()

        self.data['Confirmed'] = pd.read_csv(f'{path}/confirmed_cases.csv')
        self.data['Confirmed chg'] = pd.read_csv(f'{path}/confirmed_cases_daily_change.csv')        
        self.data['Confirmed t0'] = pd.read_csv(f'{path}/confirmed_cases_since_t0.csv')
        self.data['Recovered'] = pd.read_csv(f'{path}/recovered_cases.csv')
        self.data['Dead'] = pd.read_csv(f'{path}/dead_cases.csv')
        self.data['Active'] = pd.read_csv(f'{path}/active_cases.csv')
        self.data['Mortality'] = pd.read_csv(f'{path}/mortality_rate.csv')
        self.data['Coordinates'] = pd.read_csv(f'{path}/coordinates.csv')
        self.data['Continents'] = pd.read_csv(f'{path}/continents.csv')            
        self.data['Ctry to cont'] = pd.read_csv(f'{path}/country_to_continent.csv')
        self.data['Country stats'] = pd.read_csv(f'{path}/country_stats.csv')        
        self.data['World bank'] = pd.read_csv(f'{path}/world_bank.csv')

        for _, df in self.data.items():
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])

        self.all_countries = sorted(set(self.data['Coordinates']['Country']))
        self.all_continents = sorted(set(self.data['Continents']['Continent']))

    def list_highest_mortality(self, n=10):
        """

        Generate a list of countries with the highest moratlity rate.

        Notes
        -----
        mortality = dead / confirmed.

        """

        df = self._sort_ctry_stats(stat_name='Mortality', n=n)
        
        return df

    def get_country_ts(self, country):
        """

        Extract country level cases time series.

        """

        dfs = [self.data['Confirmed'][['Date', country]],
               self.data['Recovered'][['Date', country]],
               self.data['Dead'][['Date', country]],
               self.data['Active'][['Date', country]]]

        df = reduce(lambda x, y: pd.merge(x, y, on='Date', how='outer'), dfs)                   

        df.columns = ['Date', 'Confirmed', 'Recovered', 'Dead', 'Active']

        return df

    def get_continent_ts(self, continent):
        """

        Get continent level cases time series.

        """

        cont = self.data['Continents'].copy()
        cont = cont[cont['Continent'] == continent]

        cont = pd.merge(self.data['Coordinates'], cont, on='Country')

        countries = sorted(list(cont['Country']))

        cases = ['Confirmed', 'Recovered', 'Dead', 'Active']

        dfs = []
        for c in cases:
            tmp = self.data[c][countries].sum(axis=1)
            tmp.name = c
            tmp = tmp.to_frame()
            tmp['Date'] = self.data[c]['Date']
            dfs.append(tmp)

        df = reduce(lambda x, y: pd.merge(x, y, on='Date', how='outer'), dfs)                   

        df = df[['Date'] + cases]

        return df

    def get_world_ts(self):
        """

        Get world level cases time series.

        """

        cases = ['Confirmed', 'Recovered', 'Dead', 'Active']

        dfs = []

        for case in cases:
            tmp = self.data[case].drop('Date', axis=1).sum(axis=1)
            tmp.name = case
            tmp = tmp.to_frame()
            tmp['Date'] = self.data[case]['Date']
            dfs.append(tmp)

        df = reduce(lambda x, y: pd.merge(x, y, on='Date', how='outer'), dfs)                   

        return df
    
    def get_highest_mortality(self, n_countries, min_cases=10 ** 4):
        """
        
        List countries with highest moratlity rate.

        """

        df = self.data['Country stats']
        df = df[df['Confirmed'] > min_cases]
        df = df.sort_values('Mortality', ascending=False).copy()
        df = df.reset_index(drop=True)
        df = df.head(n_countries)
        df = df[['Country', 'Mortality']]
            
        return df

    def get_most_cases(self, case_type, n=10):
        """

        Get n countries with most cases.

        """

        df = self._sort_ctry_stats(stat_name=case_type, n=n)
        return df        
      
    def plot_world_cases(self):
        """

        Create world cases line plot.

        """

        df = self.get_world_ts()
        self.plot_ts(df=df, title='World', suffix='cases')

    def plot_country_cases(self, country):
        """

        Create individual country cases line plot.

        """        

        df = self.get_country_ts(country=country)
        self.plot_ts(df, country, 'cases')

    def plot_continent_cases(self, continent):
        """

        Create continent cases line plot.

        """

        df = self.get_continent_ts(continent=continent)
        self.plot_ts(df, continent, 'cases')
      
    def plot_ts(self, df, title, suffix):
        """

        Draw individual time series as a line plot.

        Inputs
        ------
        df : pd.DataFrame
            A dataframe with a `Date` column and cases data.
        title : str
            The title of the plot

        Notes
        -----
        This will create a time series plot of cases. It
        will also save the plot to ../img/{title}.png

        """

        # Set proper aspect ratio and dpi
        width = 1650
        height = width / 2.33
        dpi = 300
        fontsize = 8
        fontfamily = 'serif'

        plt.figure(figsize=(width/dpi, height/dpi), dpi=dpi)
        ax = plt.subplot(111)

        # Extend x axis so that labels fit inside the plot
        extend_x_axis = pd.Timedelta('7 days')

        # Extend plot by 5% to make space between
        # plot and title
        extend_y_axis = 0.04

        # Disable axis
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Force ticks to bottom left
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()

        # Get min and max values to set limits
        # points fit inside the plot.
        xmin = df['Date'].min()
        xmax = df['Date'].max() + extend_x_axis
        ymin = df.drop(['Date'], axis=1).min().min() 
        ymax = df.drop(['Date'], axis=1).max().max() 

        yticks, ylabels = get_vlines(ymin, ymax, k=3)

        plt.yticks(ticks=yticks, labels=ylabels, 
                   fontsize=fontsize, family=fontfamily)

        plt.xticks(fontsize=fontsize, family=fontfamily)

        # Display label of every other month
        ax.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))

        # Plot horizontal greyed out lines so that people can
        # actually see the data without squinting
        for y_val in yticks:
            ax.plot(df['Date'], np.full((len(df), 1), y_val), c='black', 
                    linestyle='dashed', linewidth=1/2, alpha=3/10)

        # User colors from color brewer.
        colours = ['#d7191c', '#fdae61', '#a6d96a', '#1a9641']

        # Extract list of columns in alphabeticall order
        cols = sorted(df.drop('Date', axis=1).columns)

        # Plot the actual data
        for col,c in zip(cols, colours):
            # Line plot
            ax.plot(df['Date'], df[col], linewidth=3/2, alpha=9/10, c=c)

            # Plot marker at end of x axis
            x = df['Date'].tail(1)
            y = df[col].tail(1)
            ax.scatter(x=x, y=y, linewidth=3, c=c, marker='.', alpha=9/10)

            # Plot label outside plot
            ax.text(x=df['Date'].tail(1) + pd.Timedelta('7 days'), 
                    y=df[col].tail(1), s=col, fontsize=fontsize, c=c,
                    family=fontfamily, horizontalalignment='left',
                    verticalalignment='center')

        # Display title left aligned to y axis
        plt.title(label=title, fontsize=fontsize + 1, family=fontfamily,
                   weight='bold', loc='left')

        # Set plot limits and extend y by 5%
        plt.xlim(xmin, xmax)

        # Set minimum y value to -2% of ymax so that 
        plt.ylim(-extend_y_axis * ymax, (1 + extend_y_axis) * ymax)
    
        plt.tick_params(axis='both', which='both', 
                        bottom=False, top=False,    
                        labelbottom='on', left=False, 
                        right=False, labelleft='on')            

        plt.tight_layout()            

        plt.savefig(f'../img/{title.lower()}_{suffix}.png', bbox_inches='tight')

    def plot_highest_country_stats(self, statistic, n=10):
        """

        Bar plot of countries with the most cases of a certain type.    

        """
            
        df = self.get_most_cases(case_type=statistic)

        plt.figure()
        plt.bar(df['Country'], df[statistic])
        plt.xticks(rotation=90)
        plt.title(f'{statistic}')

        if statistic == 'Mortality':
            plt.ylabel('Moratlity Rate (%)')
        else:
            plt.ylabel('Cases')

        plt.tight_layout()

        plt.savefig(f'../img/{statistic.lower()}_cases_most.png')

        plt.show()                

    def plot_growth(self, countries, periods, steps=50, save=False):
        """
        
        Plot growth curves, log scale.
        
        Inputs
        ------
        countries : list
            List of countries
        periods : list of ints
            Doubling periods for growth curves.
        steps : int
            Number of data points to use.
        
        """
        
        countries = sorted(countries)
        
        # Extract mean and use as starting point for 
        # exponential growth curves.
        a = self.data['Confirmed t0'].mean(axis=1)[0]
        b = 2

        # List of growth curves
        growth = list()
        for period in periods:
            g = exp_growth(a=a, 
                        b=b, 
                        t=np.arange(steps), 
                        tau=period)
            g = np.log(g)
            growth.append(list(g))

        for g,p in zip(growth, periods):

            # Draw growth curves
            plt.plot(range(steps), g, 
                    c='black', 
                    linestyle='dashed', 
                    alpha=1/2)

            if p == 1:
                s = f'Double every day'
            else:
                s = f'Double every {str(p)} days'       

            # Draw text outside
            plt.text(x=steps,
                    y=g[steps - 1],
                    s=s, 
                    alpha=3/4, 
                    horizontalalignment='left',
                    verticalalignment='center',
                    rotation_mode='anchor')

        # Draw country level data
        plot_df = self.data['Confirmed t0'][countries].head(steps)
        for c in countries:
            plt.plot(range(len(plot_df)), np.log(plot_df[c]), label=c)

        plt.xlim(0, steps-1)
        plt.legend(loc='best')
        plt.ylabel('Confirmed cases, log scale')
        plt.xlabel('Days since 100 cases')
        plt.tight_layout()

        if save:
            plt.savefig('../img/growth_plot.png')
            
        plt.show()    

    def plot_country_cases_chg(self, country, n=7):
        """

        Plot country level change in cases with n day moving average.        

        """

        df = self.data['Confirmed chg'][['Date', country]].copy()
        df[f'{n} day average \n of new cases'] = df[country].rolling(n).mean()
        df = df.drop(country, axis=1)

        self.plot_ts(df=df, title=country, suffix='chg')

    def plot_with_slope(self, x, y):
        """

        Create scatter plot with regression line and 
        greyed out R squared.

        """

        X = self.data['World bank'][x]
        Y = self.data['World bank'][y]

        X_reg = np.linspace(np.min(X), np.max(X), 1000)

        # Estimate Y = aX +b
        a, b, c, p, _ = linregress(X, Y)

        # Get r squared
        r = c * c

        Y_reg = a * X_reg + b
        label_reg = f'y = {round(a, 4)}x + {round(b, 4)}'
        text_reg = r'$R^{2}$' + f'={round(r, 2)}'# + '\n' + r'$p$-value' + f'={round(p, 2)}'

        plt.figure(figsize=(5,5))

        plt.scatter(x=X, y=Y, s=4, alpha=2/3)

        plt.plot(X_reg, Y_reg, 
                 linewidth=1, 
                 color='black', 
                 label=label_reg)
        
        plt.text(x=(np.min(X) + np.max(X))/2, 
                 y=(np.min(Y) + np.max(Y))/2, 
                 s=text_reg,
                 alpha=1/4,
                 fontsize=30,
                 verticalalignment='center',
                 horizontalalignment='center')

        plt.xlabel(f'{x}')
        plt.ylabel(f'{y}')
        # plt.legend(loc='upper left')

        plt.tight_layout()
        plt.show()        
 
    def _sort_ctry_stats(self, stat_name, min_cases=5000, n=10):
        """

        Sort the dataframe of country statistics using a cutoff
        of `min_cases` and return top `n` countries.

        """

        df = self.data['Country stats'].copy()
        df['Has min cases'] = df['Confirmed'] > min_cases
        df = df[df['Has min cases'] == True]
        df = df.sort_values(stat_name, ascending=False)
        df = df.reset_index(drop=True)
        df = df[['Country', stat_name]]    
        df = df.head(n)

        return df

    def show_corr_mat(self):
        """

        Display colourfull correlation matrix of cases with socioeconomic factors.        

        """

        C = self.data['World bank'].corr()
        C = C.style.background_gradient(cmap='coolwarm')
        C = C.set_precision(2)
        C = C.set_table_attributes('style="font-size: 13px"')
        
        display(C)

def exp_growth(a, b, t, tau):
    """
    
    Calculate exponential growth.
    
    Parameters
    ----------
    a : int
        Initial value.
    b : int
        Growth factor.
    t : int 
        Time.
    tau : int
        Time required for increase by factor of b.
        
    Notes
    -----
    See https://en.wikipedia.org/wiki/Exponential_growth 
    for details.
    
    """
    
    return a * np.power(b, t / tau)         
