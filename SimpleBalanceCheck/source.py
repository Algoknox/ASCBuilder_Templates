from pyteal import *

def approval_program():

    txn_sender = Txn.sender()

    creator_address = Global.creator_address()

    minimum_amount = Int(1000000)

    algo_balance = Balance(txn_sender)

    simple_Call = Seq(
        If (
            And(
                txn_sender == creator_address,
                algo_balance >= minimum_amount
            )
        ).Then(
            Seq(
                Approve()
            )
        ).Else(
            Seq(
                Reject()
            )
        ),
    )
    OptIn = Seq(
        Approve()
    )
    OnCreate = Seq(
        Approve()
    )

    on_call_method = Txn.application_args[0]

    OnCall = Cond(
        [on_call_method == Bytes("simple_Call"), simple_Call],
    )
    program = Cond(
        [Txn.application_id() == Int(0), OnCreate],
        [
            Or(
                Txn.on_completion() == OnComplete.OptIn,
                Txn.on_completion() == OnComplete().NoOp
            ),
            OnCall
        ],
        [
            Or(
                Txn.on_completion() == OnComplete.CloseOut,
                Txn.on_completion() == OnComplete.UpdateApplication,
                Txn.on_completion() == OnComplete.DeleteApplication
            ),
            Reject()
        ]
    )
    return program

def clear_program():
    return Approve()

if __name__ == "__main__":
    with open("approval.teal", "w") as f:
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=5)
        f.write(compiled)

    with open("clear.teal", "w") as f:
        compiled = compileTeal(clear_program(), mode=Mode.Application, version=5)
        f.write(compiled)