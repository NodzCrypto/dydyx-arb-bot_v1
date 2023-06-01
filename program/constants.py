from dydx3.constants import API_HOST_GOERLI, API_HOST_MAINNET
from decouple import config


#!!!!!! MODE SELECTION  !!!!!!
MODE = "DEV"

#ANNULATON DE TOUS LES ORDRES ET POSITIONS
ABORT_ALL_POSITIONS = False

#Paire cointégré trouvé 
FIND_COINTEGRATED_PAIR = True

#Place a trades
PLACE_TRADES = True

#resolution - Timeframe
RESOLUTION = "1Hours"

#Plage de jours pour le calcul des moving average
WINDOW = 21

# Thresholds - Opening
MAX_HALF_LIFE = 24
ZSCORE = 1.5
USD_PER_TRADE = 50
USD_MIN_COLLATERAL = 1880

# Thresholds - Opening
CLOSE_AT_ZSCORE_CROSS = True

# WALLET
ETHEREUM_ADDRESS = config("ETHEREUM_ADDRESS")

#---------------------- DEV  -------------------------------------
#TESTNET - PARAM  ------------------------------------
STARK_PRIVATE_KEY_TESTNET = config("STARK_PRIVATE_KEY_TESTNET")
DYDX_API_KEY_TESTNET = config("DYDX_API_KEY_TESTNET")
DYDX_API_SECRET_TESTNET = config("DYDX_API_SECRET_TESTNET")
DYDX_API_PASSPHRASE_TESTNET = config("DYDX_API_PASSPHRASE_TESTNET")
# HTTP Provider
HTTP_PROVIDER_TESTNET_ETH = config("HTTP_PROVIDER_TESTNET_ETH")

#---------------------------  PROD  ----------------------------

#STARK_PRIVATE_KEY_MAINNET - PARAM  ------------------------------------
STARK_PRIVATE_KEY_MAINNET = config("STARK_PRIVATE_KEY_MAINNET")
DYDX_API_KEY_MAINNET = config("DYDX_API_KEY_MAINNET")
DYDX_API_SECRET_MAINNET = config("DYDX_API_SECRET_MAINNET")
DYDX_API_PASSPHRASE_MAINNET = config("DYDX_API_PASSPHRASE_MAINNET")
# HTTP Provider
HTTP_PROVIDER_MAINNET_ETH = config("HTTP_PROVIDER_MAINNET_ETH")

#KEYS - EXPORT
STARK_PRIVATE_KEY = STARK_PRIVATE_KEY_MAINNET if MODE == "PROD" else STARK_PRIVATE_KEY_TESTNET
DYDX_API_KEY = DYDX_API_KEY_MAINNET if MODE == "PROD" else DYDX_API_KEY_TESTNET
DYDX_API_SECRET = DYDX_API_SECRET_MAINNET if MODE == "PROD" else DYDX_API_SECRET_TESTNET
DYDX_API_PASSPHRASE = DYDX_API_PASSPHRASE_MAINNET if MODE == "PROD" else DYDX_API_PASSPHRASE_TESTNET

# HTTP Provider - export
HTTP_PROVIDER = HTTP_PROVIDER_MAINNET_ETH if MODE == "PROD" else HTTP_PROVIDER_TESTNET_ETH

# HOST - export
HOST = API_HOST_MAINNET if MODE == "PROD" else API_HOST_GOERLI