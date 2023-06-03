from constants import CLOSE_AT_ZSCORE_CROSS
from func_utils import format_number
from func_public import get_candles_recent
from func_cointegration import calculate_zscore
from func_private import place_market_order
import json
import time

from pprint import pprint

# managing trade exits
def manage_trade_exits(client):

    """
        Manage exiting open positions
        based upon criteria set in constants
    """

    # Initialize saving output
    save_output = []

    # Opening JSON file
    try:
        open_positions_file = open("bot_agents.json")
        open_positions_dict = json.load(open_positions_file)
    except:
        return "complete"
    
    # Guard: Exit if no open positions in file
    if len(open_positions_dict) < 1:
        return "complete"
    
    # Get all open positions on exchange
    exchange_pos = client.private.get_positions(status="OPEN")
    all_exc_pos = exchange_pos.data["positions"]
    markets_live = []

    for p in all_exc_pos:
        markets_live.append(p["market"])

    # protect API
    time.sleep(0.5)

    # Check all saved positions match order record
    # Exit trade according to any exit trade rules
    for position in open_positions_dict:

        # Initialize is_close trigger
        is_close = False

        # Extract position matching information from file - market 1
        position_market_m1 = position["market_1"]
        position_size_m1 = position["order_m1_size"]
        position_side_m1 = position["order_m1_side"]

        # Extract position matching information from file - market 2
        position_market_m2 = position["market_2"]
        position_size_m2 = position["order_m2_size"]
        position_side_m2 = position["order_m2_side"]

        # Protect API
        time.sleep(0.5)

        # Get Order info m1 per exchange
        order_m1 = client.private.get_order_by_id(position["order_id_m1"])
        order_market_m1 = order_m1.data["order"]["market"]
        order_size_m1 = order_m1.data["order"]["size"]
        order_side_m1 = order_m1.data["order"]["side"]

        # Protect API
        time.sleep(0.5)

        # Get Order info m2 per exchange
        order_m2 = client.private.get_order_by_id(position["order_id_m2"])
        order_market_m2 = order_m2.data["order"]["market"]
        order_size_m2 = order_m2.data["order"]["size"]
        order_side_m2 = order_m2.data["order"]["side"]

        # Perform matching check between JSON file and Exchange
        check_m1 = position_market_m1 == order_market_m1 and position_size_m1 == order_size_m1 and position_side_m1 == order_side_m1
        check_m2 = position_market_m2 == order_market_m2 and position_size_m2 == order_size_m2 and position_side_m2 == order_side_m2
        check_live = position_market_m1 in markets_live and position_market_m2 in markets_live

        # Guard: if not all match exit with error
        if not check_m1 or not check_m2 or not check_live:
            print(f"Warning: not all open positions match exchange recoards for {position_market_m1} and {position_market_m2}")
            continue

        # Get prices
        series_1 = get_candles_recent(client, position_market_m1)
        time.sleep(0.2)
        series_2 = get_candles_recent(client, position_market_m2)
        time.sleep(0.2)

        # Get markets for referece of tick size
        markets = client.public.get_markets().data

        # Protect API
        time.sleep(0.5)

        # Trigger close based on ZScore 
        if CLOSE_AT_ZSCORE_CROSS:
            
            # Initialize ZScore
            hedge_ratio = position["hedge_ratio"]
            zscore_traded = position["zscore"]

            if len(series_1) > 0 and len(series_1) == len(series_2):
                spread = series_1 - (hedge_ratio * series_2)
                zscore_current = calculate_zscore(spread).values.tolist()[-1]

            # Determine trigger 
            zscore_level_check = abs(zscore_current) >= abs(zscore_traded)
            zscore_cross_check = (zscore_current < 0 and zscore_traded > 0) or (zscore_current > 0 and zscore_traded < 0)

            # Close trade
            if zscore_level_check and zscore_cross_check:

                # Initiate close trigger
                is_close = True

            ###
            # possibilité d'ajouter ici d'autres critères de close
            ###
        
        # Close positions if triggered
        if is_close:
            # Determine side - m1
            side_m1 = "SELL" if position_side_m1 == "BUY" else "BUY"

            # Determine side - m2
            side_m2 = "SELL" if position_side_m2 == "BUY" else "BUY"

            # Get format price
            price_m1 = float(series_1[-1])
            price_m2 = float(series_2[-1])

            accept_price_m1 = price_m1 * 1.05 if side_m1 == "BUY" else price_m1 * 0.95
            accept_price_m2 = price_m2 * 1.05 if side_m2 == "BUY" else price_m2 * 0.95
            tick_size_m1 = markets["markets"][position_market_m1]["tickSize"]
            tick_size_m2 = markets["markets"][position_market_m2]["tickSize"]
            accept_price_m1 = format_number(accept_price_m1, tick_size_m1)
            accept_price_m2 = format_number(accept_price_m2, tick_size_m2)

            # Close positions
            try:
                # Close positions for market 1
                print(">>> Closing Market 1 <<<")
                print(f"Closing position for {position_market_m1}")

                close_order_m1 = place_market_order(
                    client, 
                    market=position_market_m1,
                    side=side_m1,
                    size=position_size_m1,
                    price=accept_price_m1,
                    reduce_only=True
                )

                print("id : ", close_order_m1["order"]["id"])
                print(">>> Closed <<<")

                # Protect API
                time.sleep(1)
                
                # Close positions for market 2
                print(">>> Closing Market 2 <<<")
                print(f"Closing position for {position_market_m2}")

                close_order_m2 = place_market_order(
                    client, 
                    market=position_market_m2,
                    side=side_m2,
                    size=position_size_m2,
                    price=accept_price_m2,
                    reduce_only=True
                )

                print("id : ", close_order_m2["order"]["id"])
                print(">>> Closed <<<")

                # Protect API
                time.sleep(1)
            except Exception as e:
                print(f"Exit failed for {position_market_m1} with {position_market_m2}")
                save_output.append(position)

        # Keep record of items and save
        else:
            save_output.append(position)

    # Save remaining items
    print(f"{len(save_output)} Items remaining. Saving file....")
    with open("bot_agents.json", "w") as f:
        json.dump(save_output, f)