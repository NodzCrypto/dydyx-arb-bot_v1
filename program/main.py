from constants import ABORT_ALL_POSITIONS, FIND_COINTEGRATED_PAIR
from func_connections import connexion_dydx
from func_private import abort_all_open_positions
from func_public import construct_market_prices

if __name__ == "__main__":

    #connect to client 
    try:
        print("Connexion au client...")
        client = connexion_dydx()
    except Exception as e:   
        print(e)
        print("Erreur de connexion client : ", e)
        exit(1)

    # Abort all open positions
    if ABORT_ALL_POSITIONS == True:
        try: 
            print("Closing all positions...")
            close_orders = abort_all_open_positions(client)
        except Exception as e:
            print(e)
            print("Error closing positions : ", e)
            exit(1)

    #Find cointegrated pairs
    if FIND_COINTEGRATED_PAIR:
        try: 
            print("Fetching market prices, please wait...")
            df_market_prices = construct_market_prices(client)
        except Exception as e:
            print(e)
            print("Error constructing market prices ", e)
            exit(1)