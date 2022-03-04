import re
import base64
from algosdk.future import transaction
from algosdk import account, mnemonic
from algosdk.v2client import algod
from multiaddr.codecs import utf8


class User:

    def __init__(self):
        self.username = "Username"
        self.emailid = "email"
        self.user = "UserType"
        self.signup = "Sign Up"

# Check Username of the User.
    def check_username(self, userName):
        self.username = userName
        while True:
            is_valid = False
            if len(userName) < 6 or len(userName) > 12:
                print("Not valid ! Username total characters should be between 6 and 12")
                break
            elif not re.search("[A-Z]", userName):
                print("Not valid ! Username should contain one letter between [A-Z]")
                break
            elif not re.search("[a-z]", userName):
                print("Not valid ! Username should contain one letter between [a-z]")
                break
            elif not re.search("[1-9]", userName):
                print("Not valid ! Username should contain one letter between [1-9]")
                break
            elif re.search("[\s]", userName):
                print("Not valid ! Username should not contain any space")
                break
            else:
                is_valid = True
                break
        if is_valid:
            print("Username is valid !")

# Check the Input Email Address.
    def check_email(self, email):
        self.emailid = email
        pat = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
        if re.match(pat, email):
            print("Email id is Correct !")
            return True
        else:
            print("Email id is not valid !")

# Check if the user is investor or creator.
    def check_user(self, user_type):
        self.user = user_type
        if user_type == "Investor" or user_type == "investor":
            print("Welcome Investor.")
        elif user_type == "Creator" or user_type == "creator":
            print("Welcome Creator.")
        else:
            print("Not Valid User Type.")

# Sign Up Via option for User.
    def signUpVia(self, signup_via):
        self.signup = signup_via
        if signup_via == "Email" or signup_via == "Facebook" or signup_via == "Google":
            print("You Selected " + signup_via + ".")
        else:
            print("Wrong Sign up Input.")


# class denoted to object
user1 = User()

# Params
name = input("Enter your username: ")
email_id = input("Enter your email id: ")
userType = input("Are you an Investor or Creator? Type your Answer: ")
sign_up = input("Sign Up Via Email, Facebook or Google. Select your Method: ")

# User values are being checked
user1.check_username(name)
user1.check_email(email_id)
user1.check_user(userType)
user1.signUpVia(sign_up)


# -------------*-------------*-------------*Created Application*-------------*-------------*-------------*-------------*

# Fetching Mnemonic:
creator_mnemonic = "recipe insane demand stem tube pulp discover auction amateur dove curtain club negative boil provide help economy name congress pave nothing color feel abandon lumber"
user_mnemonic = "brass unaware company mirror rail oil step journey cargo denial inflict code ozone route recall animal ribbon comfort expect fun liquid woman stone able arrest"

# user declared algod connection parameters
algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = "K7DgVll3W19DdHA3FTduX4XZTuCvTFf32HXUP5E4"
headers = {"X-API-Key": algod_token}

# application state storage
local_ints = 5
local_bytes = 5
global_ints = 5
global_bytes = 5
global_schema = transaction.StateSchema(global_ints, global_bytes)
local_schema = transaction.StateSchema(local_ints, local_bytes)

# Approval Program
approval_program_source_initial = b"""#pragma version 5
txn ApplicationID
int 0
==
bnz main_l2
err
main_l2:
txn NumAppArgs
int 4
==
bnz main_l4
err
main_l4:
byte "name"
txna ApplicationArgs 0
app_global_put
byte "email_id"
txna ApplicationArgs 1
app_global_put
byte "userType"
txna ApplicationArgs 2
app_global_put
byte "sign_up"
txna ApplicationArgs 3
app_global_put
int 1
return
"""

# Clear Program
clear_program_source = b"""#pragma version 5
int 1
"""


# helper function to compile program source
def compile_program(client, source_code):
    compile_response = client.compile(source_code.decode('utf-8'))
    return base64.b64decode(compile_response['result'])


# converting a mnemonic into a private signing key
def get_private_key_from_mnemonic(mn):
    private_key = mnemonic.to_private_key(mn)
    return private_key


# waiting for transaction id to be confirmed by the network
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


args_list = [bytes(name, 'utf8'), bytes(email_id, 'utf8'), bytes(userType, 'utf8'), bytes(sign_up, 'utf8')]


# create new application
def create_app(client, private_key, approval_program, clear_program, global_schema, local_schema):
    sender = account.address_from_private_key(private_key)
    on_complete = transaction.OnComplete.NoOpOC.real
    params = client.suggested_params()
    txn = transaction.ApplicationCreateTxn(sender, params, on_complete, approval_program, clear_program, global_schema, local_schema, args_list)

    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()
    client.send_transactions([signed_txn])
    wait_for_confirmation(client, tx_id)
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response['application-index']
    print("Created new app-id: ", app_id)

    return app_id


def main():
    algod_client = algod.AlgodClient(algod_token, algod_address, headers)
    creator_private_key = get_private_key_from_mnemonic(creator_mnemonic)
    user_private_key = get_private_key_from_mnemonic(user_mnemonic)
    approval_program = compile_program(algod_client, approval_program_source_initial)
    clear_program = compile_program(algod_client, clear_program_source)
    app_id = create_app(algod_client, creator_private_key, approval_program, clear_program, global_schema, local_schema)


main()

