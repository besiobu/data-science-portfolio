# trading results

## Project goal
The objective is to analyze trades placed by my trading algorithm.

### Methods
* Data visualization
* Data wrangling

### Technologies
* Python
* Pandas
* Matplotlib

## Project description
First some background information: I wrote a trading algorithm, hosted it on a VPS and it traded there for a month. I extracted information about trades placed by my trading algorithm from my trading platform in the form of a `.csv` file. Next I analyse the profitability of trades. Lastly I simulate future performance and calculate upper and lower bounds on expected performance.

## Summary
* Between `2020-05-19` and `2020-06-16` the algorithm executed `92` trades and achieved a profit of `118.02 PLN`.

* The market with the highest total profit was the `USD/CHF` currency pair. The profit was `180.18 PLN`.

* The market with the biggest total loss was the `US500` stock index. The loss amounted to `-76.74 PLN`.

* The best and worst trades respectively were both on the `US500` index and amounted to `140.30 PLN` and `-41.10 PLN`.

* The per contract distribution of profit has a mean of `0.49 PLN` and standard deviation of `22.8 PLN`. The distribution exhibits `positive skew` and `leptokurtosis`.

* Around the `50`-th trade the strategy entered a period of drawdown that lasted `4 days 03:48:00`. During that time the algorithm lost `243.01 PLN`.

* Under the assumption that market behaviour does not change the probability of the algorithm making money over the next `100` trades is `56.63%`.

* Under the same assumption as above, a cumulative loss of more than `306.93 PLN` should force a re-evaluation of the algorithm.