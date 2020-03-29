import pandas as pd
import numpy as np

CEIL_PRICE = 40
FLOOR_PRICE = 5
SAMPLES = 500
RANDOM_STATE = 42
EPOCHS = 10

df = pd.read_csv('./data/russell_2000.csv')
of_interest = df[(df['Price'] <= CEIL_PRICE) & (df['Price'] > FLOOR_PRICE)]
of_interest = of_interest.sample(n=SAMPLES, random_state=RANDOM_STATE)

df = pd.read_csv('Best_MA.csv')
result = pd.merge(df, of_interest[['Ticker', 'Beta']],
                  left_on='Sym', right_on='Ticker',
                  how='left')
result.drop(columns=['Ticker'], inplace=True)

weights = pd.DataFrame(np.random.random((2, 2)))
p = pd.DataFrame([np.ones((len(result))), result['Beta']])
# FIXME need a better fill strat
p.fillna(0, inplace=True)
a = pd.DataFrame([result['Sa'], result['La']], index=[0, 1])
m = len(p)
alpha = 0.1
for i in range(0, EPOCHS):
    t = weights.dot(p)
    err = (t - a).transpose()
    err.fillna(0, inplace=True)
    adjustment = alpha / m * p.dot(err)
    weights -= adjustment

    cost = ((t - a) ** 2)
    cost = cost.sum(1) / (m * 2)
    print(cost)


