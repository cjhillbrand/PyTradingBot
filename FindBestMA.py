from Controller import Controller
from BuyStrategies.BuyUtil import new_buy_strategy, BuyTypes
from SellStrategies.SellUtil import new_sell_strategy, SellTypes
from Model import Model
import csv

MIN_SA = 2
MAX_SA = 199
MIN_LA = 3
MAX_LA = 200


def reassign_vals(la, sa, pct, sym):
    return {'Sym': sym, 'Pct': pct, 'Sa': sa, 'La': la}


if __name__ == "__main__":
    model = Model()
    cont = Controller(model)
    max_percents = list()

    cont.load_russell()

    for sa in range(MIN_SA, MAX_SA + 1):
        for la in range(MIN_LA, MAX_LA + 1):
            if sa >= la:
                continue
            print('Trying sa %d and la %d' % (sa, la))

            st = new_sell_strategy(1, sa, la)
            bt = new_buy_strategy(1, sa, la)

            cont.set_buy_strategy(bt)
            cont.set_sell_strategy(st)

            percents = cont.simulate_strategies(-1, verbosity=0)
            if sa == MIN_SA and la == MIN_LA:
                max_percents = [{'Sym': sym, 'Pct': percents[sym], 'Sa': sa, 'La': la} for sym in percents.keys()]

            else:
                max_percents = [reassign_vals(la, sa, percents[elem['Sym']], elem['Sym'])
                                if percents[elem['Sym']] > elem['Pct']
                                else elem for elem in max_percents]

    cols = ['Sym', 'Pct', 'Sa', 'La']
    csv_file = 'Best_MA.csv'
    try:
        with open(csv_file, 'w') as fid:
            writer = csv.DictWriter(fid, fieldnames=cols)
            writer.writeheader()
            for elem in max_percents:
                writer.writerow(elem)
    except IOError:
        print('I/O error')
