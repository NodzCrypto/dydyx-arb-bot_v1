from constants import ABORT_ALL_POSITIONS, FIND_COINTEGRATED_PAIR, PLACE_TRADES, MANAGE_EXITS
from func_connections import connexion_dydx
from func_private import abort_all_open_positions
from func_public import construct_market_prices
from dydx3.constants import MARKET_BTC_USD
from func_cointegration import store_cointegration_results
from func_entry_pairs import open_positions
from func_exit_pair import manage_trade_exits
from func_messaging import send_message

# MAIN FUNCTION
if __name__ == "__main__":

    # Message on start 
    send_message("Bot launched successfully !") 

    #connect to client 
    try:
        print("Connexion au client...")
        client = connexion_dydx()
    except Exception as e:   
        print(e)
        print("Erreur de connexion client : ", e)
        send_message(f"ERR03 - Failed to connect to client : {e}") 
        exit(1)

    # Abort all open positions
    if ABORT_ALL_POSITIONS == True:
        try: 
            print("Closing all positions...")
            close_orders = abort_all_open_positions(client)
        except Exception as e:
            print(e)
            print("Error closing positions : ", e)
            send_message(f"ERR04 - Failed closing all positions : {e}") 
            exit(1)

    #Find cointegrated pairs
    if FIND_COINTEGRATED_PAIR:
        try: 
            print("Fetching market prices, it could take 3-5 mins, please wait...")
            df_market_prices = construct_market_prices(client)
        except Exception as e:
            print(e)
            print("Error constructing market prices ", e)
            send_message(f"ERR05 - Failed constructing market prices : {e}") 
            exit(1)

    #Store cointegrated pairs
    if FIND_COINTEGRATED_PAIR:
        try: 
            print("Storing cointegrated pairs, please wait...")
            store_result = store_cointegration_results(df_market_prices)
            if store_result != "saved":
                print("Error saving cointegrated pairs")
                exit(1)

        except Exception as e:
            print("Error saving cointegrated pairs: ", e)
            send_message(f"ERR06 - Failed saving cointegrated pairs : {e}") 
            exit(1)

    # Run as always on
    while True:

        # manage exits on open trade
        if MANAGE_EXITS:
            try: 
                print("Managing exits...")
                manage_trade_exits(client)

            except Exception as e:
                print("Error managing exiting positions: ", e)
                send_message(f"ERR06 - Failed managing exiting positions : {e}") 
                exit(1) 

        # Place trades for opening positions
        if PLACE_TRADES:
            try: 
                print("Searching trading opportunities...")
                open_positions(client)

            except Exception as e:
                print("Error opening position: ", e)
                send_message(f"ERR06 - Failed opening position : {e}") 
                exit(1)        

   