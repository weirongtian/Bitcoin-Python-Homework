# Import dependencies
import subprocess
import json
#rom dotenv import load_dotenv
import os

# Load and set environment variables
load_dotenv("API.env")
mnemonic=os.getenv("mnemonic")

# Import constants.py and necessary functions from bit and web3
# YOUR CODE HERE
from constants import *
from web3 import Web3
from decimal import Decimal
from eth_account import Account
from bit import wif_to_key, PrivateKeyTestnet, network
from web3.middleware import geth_poa_middleware
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# Create a function called `derive_wallets`
def derive_wallets(coin):
    command = './derive -g --mnemonic="'+ mnemonic+'" --cols=path,address,privkey,pubkey --format=json --coin=' + coin
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait()
    return json.loads(output)
    

# Create a dictionary object called coins to store the output from `derive_wallets`.
coins = {"btc-test" : derive_wallets(BTCTEST),
         "eth"      : derive_wallets(ETH) }

# Create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_to_account(coin,priv_key):
    if coin == ETH:
         return Account.privateKeyToAccount(priv_key)
    elif coin ==BTCTEST:
         return PrivateKeyTestnet(priv_key)

# Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
def create_tx(coin,account,to,amount ):
    if coin == ETH:
        amount = w3.toWei(Decimal(amount), 'ether')
        gasEstimate = w3.eth.estimateGas(
            {"from": account.address, "to": to, "value": amount}
        )
        return {
            "from": account.address,
            "to": to,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gasEstimate,
            "nonce": w3.eth.getTransactionCount(account.address),
            "chainId": 1000
    }
    elif coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])

# Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
def send_tx(coin,account,to,amount):
    raw_tx = create_tx(coin, account, to, amount)
    signed_tx = account.sign_transaction(raw_tx)
    if coin == BTCTEST:
        result = network.NetworkAPI.broadcast_tx_testnet(signed_tx)
    else:
        result = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        result = result.hex()
    return (result)

