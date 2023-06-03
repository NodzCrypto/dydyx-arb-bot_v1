from datetime import datetime, timedelta
import time
from pprint import pprint
from func_utils import format_number
import json

# Get existing open positions
def is_open_positions(client, market):

    #protect API
    time.sleep(0.2)

    # get positions
    all_positions = client.private.get_positions(
        market=market,
        status="OPEN"
    )

    # determine if open
    if len(all_positions.data["positions"]) > 0:
        return True
    else:
        return False


#check orders status
def check_order_status(client, order_id):
    order = client.private.get_order_by_id(order_id)
    if order.data:
        if "order" in order.data.keys():
            return order.data["order"]["status"]
    return "FAILED"

# Place market order
def place_market_order(client, market, side, size, price, reduce_only):
    
    # Get Position Id
    account_response = client.private.get_account()
    position_id = account_response.data["account"]["positionId"]

    # Get expiration time
    server_time = client.public.get_time()
    expiration = datetime.fromisoformat(server_time.data["iso"].replace("Z", "")) + timedelta(seconds=8000)

    # Place an order
    placed_order = client.private.create_order(
        position_id = position_id, # required for creating the order signature
        market = market,
        side = side,
        order_type="MARKET",
        post_only=False,
        size = size,
        price = price,
        limit_fee = '0.015',
        expiration_epoch_seconds = expiration.timestamp(),
        time_in_force = "FOK", 
        reduce_only = reduce_only
    )

    # Return result
    return placed_order.data

# Abort all open positions
def abort_all_open_positions(client):
    
    # Cancell all orders
    cancelOrders = client.private.cancel_all_orders()
   
    # Protect API 
    time.sleep(0.5)
    # Get markers for reference of tick size
    markets = client.public.get_markets().data

   # pprint(markets)

    # Protect API 
    time.sleep(0.5)

    # get all open positions
    positions = client.private.get_positions(status="OPEN")
    all_positions = positions.data["positions"]

    # handle open positions
    close_orders = []
    if len(all_positions) > 0:

        #on boucle pour fermer les positions
        for position in all_positions:

            #on récupère le market
            market = position["market"]

            #on récupère le side
            side = "SELL" if position["side"] == "LONG" else "BUY"

            #on récupère la taille
            size = position["size"]

            #on recupère le prix
            price = float(position["entryPrice"])
            accept_price = price * 1.7 if side == "BUY" else price * 0.3
            
            tick_size = markets["markets"][market]["tickSize"]
            accept_price = format_number(accept_price, tick_size)
  
            #on récupère l'ordre à fermer
            order = place_market_order(
                client,
                market,
                side,
                position["sumOpen"],
                accept_price,
                True
                
            )

            #on ferme l'ordre
            close_orders.append(order)

            #protect API
            time.sleep(0.2)

        # update JSON with empty list
        bot_agents = []
        with open("bot_agents.json", "w") as f:
            json.dump(bot_agents, f)


        #on renvoit les ordress fermés    
        return close_orders


