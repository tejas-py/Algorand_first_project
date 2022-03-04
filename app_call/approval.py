from pyteal import *


def approval_program():
    on_creation = Seq(
        [
            App.globalPut(Bytes("name"), Bytes("Chahat")),
            App.globalPut(Bytes("age"), Int(26)),
            Return(Int(1))
        ]
    )

    check_age = If(Int(25) <= App.globalGet(Bytes("age")), Return(Int(1)), Return(Int(0)))

    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnComplete.UpdateApplication, check_age],
        [Txn.on_completion() == OnComplete.NoOp, Approve()]
    )

    return program


if __name__ == "__main__":
    with open("approvalProgram.teal", "w") as f:
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=5)
        f.write(compiled)
