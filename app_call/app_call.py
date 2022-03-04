import base64
import datetime

from algosdk.future import transaction
from algosdk import account, mnemonic
from algosdk.v2client import algod

# user declared account mnemonics
creator_mnemonic = "arena cloth spot illness message upset fitness chief fossil share brave arm green either pond gasp weird glare ribbon topple various major phone abandon lobster"
user_mnemonic = "craft modify cost fiber myth style hat camp time arm patrol home idle kitten assault frown inherit oak lens sight radio ignore trip abandon shift"

# user declared algod connection parameters
algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = "K7DgVll3W19DdHA3FTduX4XZTuCvTFf32HXUP5E4"
headers = {"X-API-Key": algod_token}

# declare application state storage (immutable)
local_ints = 4
local_bytes = 4
global_ints = 4
global_bytes = 4
global_schema = transaction.StateSchema(global_ints, global_bytes)
local_schema = transaction.StateSchema(local_ints, local_bytes)

# user declared approval program (initial)
approval_program_source_initial = b"""#pragma version 5
txn ApplicationID
int 0
==
bnz main_l8
txn OnCompletion
int UpdateApplication
==
bnz main_l5
txn OnCompletion
int NoOp
==
bnz main_l4
err
main_l4:
int 1
return
main_l5:
int 25
byte "age"
app_global_get
<=
bnz main_l7
int 0
return
main_l7:
int 1
return
main_l8:
byte "name"
byte "Chahat"
app_global_put
byte "age"
int 26
app_global_put
int 1
return
"""

# declare clear state program source
clear_program_source = b"""#pragma version 5
int 1
"""


# helper function to compile program source
def compile_program(client, source_code):
    compile_response = client.compile(source_code.decode('utf-8'))
    return base64.b64decode(compile_response['result'])


# helper function that converts a mnemonic passphrase into a private signing key
def get_private_key_from_mnemonic(mn):
    private_key = mnemonic.to_private_key(mn)
    return private_key


# helper function that waits for a given txid to be confirmed by the network
def wait_for_confirmation(client, txid):
    last_round = client.status().get('last-round')
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
        print("Waiting for confirmation...")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print("Transaction {} confirmed in round {}.".format(txid, txinfo.get('confirmed-round')))
    return txinfo


# create new application
def create_app(client, private_key, approval_program, clear_program, global_schema, local_schema):
    # define sender as creator
    sender = account.address_from_private_key(private_key)

    # declare on_complete as NoOp
    on_complete = transaction.OnComplete.NoOpOC.real

    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = 1000

    # create unsigned transaction
    txn = transaction.ApplicationCreateTxn(sender, params, on_complete,
                                           approval_program, clear_program,
                                           global_schema, local_schema)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response['application-index']
    print("Created new app-id: ", app_id)

    return app_id


def call_app(client, private_key, index, app_args):
    # declare sender
    sender = account.address_from_private_key(private_key)
    print("Call from account: ", sender)

    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = 1000

    # create unsigned transaction
    txn = transaction.ApplicationNoOpTxn(sender, params, index, app_args)

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    print("Called app-id: ",transaction_response['txn']['txn']['apid'])
    if "global-state-delta" in transaction_response :
        print("Global State updated :\n",transaction_response['global-state-delta'])
    if "local-state-delta" in transaction_response :
        print("Local State updated :\n",transaction_response['local-state-delta'])


def main():
    # initialize an algodClient
    algod_client = algod.AlgodClient(algod_token, algod_address, headers)

    # define private keys
    creator_private_key = get_private_key_from_mnemonic(creator_mnemonic)
    user_private_key = get_private_key_from_mnemonic(user_mnemonic)

    # compile programs
    approval_program = compile_program(algod_client, approval_program_source_initial)
    clear_program = compile_program(algod_client, clear_program_source)

    # create new application
    app_id = create_app(algod_client, creator_private_key, approval_program, clear_program, global_schema, local_schema)

    # call application without arguments
    call_app(algod_client, user_private_key, app_id, None)


main()
