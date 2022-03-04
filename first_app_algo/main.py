import base64

from algosdk.future import transaction
from algosdk import account, mnemonic
from algosdk.v2client import algod

# user declared account mnemonics
creator_mnemonic = "recipe insane demand stem tube pulp discover auction amateur dove curtain club negative boil provide help economy name congress pave nothing color feel abandon lumber"
user_mnemonic = "brass unaware company mirror rail oil step journey cargo denial inflict code ozone route recall animal ribbon comfort expect fun liquid woman stone able arrest"

# user declared algod connection parameters
algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = "K7DgVll3W19DdHA3FTduX4XZTuCvTFf32HXUP5E4"
headers = {"X-API-Key": algod_token}

# declare application state storage (immutable)
local_ints = 1
local_bytes = 1
global_ints = 1
global_bytes = 0
global_schema = transaction.StateSchema(global_ints, global_bytes)
local_schema = transaction.StateSchema(local_ints, local_bytes)

approval_program_source_initial = b"""#pragma version 2
int 1
"""

# declare clear state program source
clear_program_source = b"""#pragma version 2
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


def main():
    # initialize an algodClient
    algod_client = algod.AlgodClient(algod_token, algod_address, headers)

    # define private keys
    creator_private_key = get_private_key_from_mnemonic(creator_mnemonic)
    user_private_key = get_private_key_from_mnemonic(user_mnemonic)

    approval_program = compile_program(algod_client, approval_program_source_initial)
    clear_program = compile_program(algod_client, clear_program_source)

    # create new application
    app_id = create_app(algod_client, creator_private_key, approval_program, clear_program, global_schema, local_schema)


main()
