# Imports
from decouple import config
from dydx3 import Client
from web3 import Web3
from constants import (
    STARK_PRIVATE_KEY,
    DYDX_API_KEY,
    DYDX_API_SECRET,
    DYDX_API_PASSPHRASE,
    HTTP_PROVIDER, 
    HOST
)

#connexion à DYDX
def connexion_dydx():

    #create client connexion
    client = Client(
        host=HOST,
        api_key_credentials={
            "key": DYDX_API_KEY,
            "secret": DYDX_API_SECRET,
            "passphrase": DYDX_API_PASSPHRASE,
        },
        stark_private_key = STARK_PRIVATE_KEY,
        default_ethereum_address = config("ETHEREUM_ADDRESS"),
        web3 = Web3(Web3.HTTPProvider(HTTP_PROVIDER))
    )

    #confirm client
    account = client.private.get_account()
    account_id = account.data["account"]["id"]
    quote_balance = account.data["account"]["quoteBalance"]
    print("Connection successful")
    print("Account Id: ", account_id)
    print("Quote Balance: ", quote_balance)

    return client
