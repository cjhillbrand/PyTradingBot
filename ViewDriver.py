from Model import Model
from Controller import Controller
from BuyStrategies.BuyUtil import BuyTypes, buy_type_to_string, buy_type_to_int
from SellStrategies.SellUtil import SellTypes, sell_type_to_string, sell_type_to_int


ERROR_CODE = -1
model = Model()
cont = Controller(model)


def get_symbol():
    ans = '\0'
    while ans != 'y':
        sym = input("Enter Symbol: ").upper()
        print("You have entered: ", sym)
        ans = input("Is this correct? (y)es (n)o ")
    return sym


def get_days():
    day = -1
    while day == -1:

        days_str = input("How many days back would you like to simulate?\n--> ")
        try:
            day = int(days_str)
        except ValueError:
            print('"%s" cannot be converted to an int' % days_str)
    return day


# TODO See if you can combine these two get methods for user input.
def get_buy_strategy():
    print("Please Choose a Buy Strategy:")
    ans = '\0'
    while ans == '\0':
        for bts in BuyTypes:
            print(buy_type_to_string(bts), '(', buy_type_to_int(bts), ')')
        temp = input('--> ')
        try:
            ans = int(temp)
        except ValueError:
            print('"%s" cannot be converted to an int' % temp)

    return ans


def get_sell_strategy():
    print("\nPlease Choose a Sell Strategy:")
    ans = '\0'
    while ans == '\0':
        for sts in SellTypes:
            print(sell_type_to_string(sts), '(', sell_type_to_int(sts), ')')
        temp = input('--> ')
        try:
            ans = int(temp)
        except ValueError:
            print('"%s" cannot be converted to an int' % temp)

    return ans


if __name__ == "__main__":
    print("Welcome to the Stonk Machine. Please follow the prompts...\n")
    ans = 's'
    while ans != 'o' and ans != 'r' and ans != 'c':
        ans = input('Track ( o )ne symbol or ( r )ussell 2000 or ( c )rypto?\n--> ').lower()
        if ans == 'o' or ans == 'c':
            # Grab the symbol from the user. At this location we do not care of the contents
            # of the Symbol, we only care that the user approves of their input
            symbol = get_symbol()
            code = cont.fill_data(symbol)

            # If we get an error code from Alpha Vantage we need to reprompt the user for
            # another symbol name
            while code == ERROR_CODE:
                # Keep getting new symbol and trying again.
                print("You have entered an Incorrect Symbol please try again...")
                symbol = get_symbol()
                if ans == 'c':
                    code = cont.fill_data(symbol, True)
                else:
                    code = cont.fill_data(symbol)

            print('Success loading', symbol, '\n')
        elif ans == 'r':
            print('This is where we load all the symbols of the 2000')
            symbol = 'Russel 2000'
            cont.load_russell()

    # Now we grab the buy strategy the user should only input one number.
    # At the view level we just make sure that their input can be cast to an int
    bt = get_buy_strategy()
    code = cont.set_buy_strategy(bt)

    # If we get an error from the controller we have to reprompt to the user
    # to get a valid buy strategy.
    while code == ERROR_CODE:
        print("You have entered an incorrect Buy Strategy please try again...")
        bt = get_buy_strategy()
        code = cont.set_buy_strategy(bt)

    # Now we grab the sell strategy. This is the same control flow as getting the
    # buy strategy...
    st = get_sell_strategy()
    code = cont.set_sell_strategy(st)

    # If we get an error from the controller we have to re-prompt
    while code == ERROR_CODE:
        print("You have entered an incorrect Sell strategy please try again...")
        st = get_sell_strategy()
        code = cont.set_sell_strategy(st)

    # grab the number of days the user wants to look back and go ahead and simulate
    days = get_days()
    code = cont.simulate_strategies(days)
    while code == ERROR_CODE:
        print('You have entered a zero, negative, or value greater than the number of days'
              'for stock history please enter again')
        days = get_days()
        code = cont.simulate_strategies(days)

    ans = input('Do you wish to run bot with:\nSymbol: %s\nBuy Strategy: %s\nSell Strategy: %s\n--> '
          % (symbol, buy_type_to_string(bt), sell_type_to_string(st)))
    if ans != 'y':
        print('Exiting Program')
        exit(0)

    cont.run()







