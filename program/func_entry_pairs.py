from constants import ZSCORE_TRESHOLD, USD_PER_TRADE, USD_MIN_COLLATERAL
from func_utils import format_number
from func_public import get_candles_recent
from func_cointegration import calculate_zscore
from func_private import is_open_positions
from func_bot_agent import botAgent
import pandas as pd
import json
from func_messaging import send_message

from pprint import pprint

# open positions
def open_positions(client):
    """
        Manage finding triggers for trade entry
        store trades for managing later on exit function
    """

    # Load cointegrated pairs
    df = pd.read_csv("cointegrated_pairs.csv")

    # get markets from referencing of min order size, tick size etc...
    markets = client.public.get_markets().data

    #Initialize container for botAgent results
    bot_agents = []
    # Opening JSON file
    try:
        open_positions_file = open("bot_agents.json")
        open_positions_dict = json.load(open_positions_file)

        for p in open_positions_dict:
            bot_agents.append(p)

    except:
        bot_agents = []

    # Find ZScore triggers
    for index, row in df.iterrows():

        #extract varaibles
        base_market = row["base_market"]
        quote_market = row["quote_market"]
        hedge_ratio = row["hedge_ratio"]
        half_life = row["half_life"]

        # get prices
        series_1 = get_candles_recent(client, base_market)
        series_2 = get_candles_recent(client, quote_market)
        
        #get ZScore
        if len(series_1) > 0 and len(series_1) == len(series_2):
            spread = series_1 - (hedge_ratio * series_2)
            zscore = calculate_zscore(spread).values.tolist()[-1]
            
            # Establish if potential trade
            if abs(zscore) >= ZSCORE_TRESHOLD:

                # ensure like-for-like not already open (diversify trading)
                is_base_open = is_open_positions(client, base_market) 
                is_quote_open = is_open_positions(client, quote_market)

                # place trade
                if not is_base_open and not is_quote_open:

                    # determine the side of the trade
                    base_side = "BUY" if zscore < 0 else "SELL"
                    quote_side = "BUY" if zscore > 0 else "SELL"

                    # get acceptable price in string format with correct number of decimals
                    base_price = series_1[-1]
                    quote_price = series_2[-1]

                    accept_base_price = float(base_price) * 1.01 if zscore < 0 else float(base_price) * 0.99
                    accept_quote_price = float(quote_price) * 1.01 if zscore > 0 else float(quote_price) * 0.99
                    accept_failsafe_base_price = float(base_price) * 0.05 if zscore < 0 else float(base_price) * 1.7
                    base_tick_size = markets["markets"][base_market]["tickSize"]
                    quote_tick_size = markets["markets"][quote_market]["tickSize"]

                    # Format prices
                    accept_base_price = format_number(accept_base_price, base_tick_size)
                    accept_quote_price = format_number(accept_quote_price, quote_tick_size)
                    accept_failsafe_base_price = format_number(accept_failsafe_base_price, base_tick_size)

                    """
                        partie à customiser pour trade un % de BK au lieu d'un monatant fixe et tester les différentes tailles de trade etc...
                    """

                    # Get size
                    base_quantity = 1 / base_price * USD_PER_TRADE
                    quote_quantity = 1 / quote_price * USD_PER_TRADE
                    base_step_size = markets["markets"][base_market]["stepSize"]
                    quote_step_size = markets["markets"][quote_market]["stepSize"]

                    # Format sizes
                    base_size = format_number(base_quantity, base_step_size)
                    quote_size = format_number(quote_quantity, quote_step_size)

                    # Ensure size
                    base_min_order_size = markets["markets"][base_market]["minOrderSize"]
                    quote_min_order_size = markets["markets"][quote_market]["minOrderSize"]
                    check_base = float(base_quantity) > float(base_min_order_size)
                    check_quote = float(quote_quantity) > float(quote_min_order_size)

                    # if checks pass, place trade
                    if check_base and check_quote:

                        #check account balance
                        account = client.private.get_account()
                        free_collateral = float(account.data["account"]["freeCollateral"])
                        print(f"Balance: {free_collateral} and minimum at {USD_MIN_COLLATERAL}")
                        send_message(f"Balance: {free_collateral} and minimum at {USD_MIN_COLLATERAL}")

                        # Guard: Ensure collateral
                        if free_collateral < USD_MIN_COLLATERAL:
                            send_message(f"Trade aborted, not enough collateral")
                            break

                        # create botAgent
                        bot_agent = botAgent(
                            client,
                            market_1=base_market,
                            market_2=quote_market,
                            base_side=base_side,
                            base_size=base_size,
                            base_price=accept_base_price,
                            quote_side=quote_side,
                            quote_size=quote_size,
                            quote_price=accept_quote_price,
                            accept_failsafe_base_price=accept_failsafe_base_price,
                            zscore=zscore,
                            half_life=half_life,
                            hedge_ratio=hedge_ratio,

                        )

                        # open trade
                        bot_open_dict = bot_agent.open_trades()

                        # handles success in opening trades
                        if bot_open_dict["pair_status"] == "LIVE":

                            # append to list of bot agents
                            bot_agents.append(bot_open_dict)
                            del (bot_open_dict)

                            #confirm live status in print
                            print("Trades status : live")
                            print("---")
    # save agents
    print(f"Success: Manage open trades checked")
    
    if len(bot_agents) > 0:
        with open("bot_agents.json", "w") as f:
            json.dump(bot_agents, f)

