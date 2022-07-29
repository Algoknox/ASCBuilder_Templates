from pyteal import *

def approval_program():

    counter_key = Bytes('counter')

    counter_value = App.globalGet(counter_key)

    increment_by = Int(1)

    incremented = counter_value + increment_by

    increment_call = Seq(
        App.globalPut(counter_key, incremented),
            Approve(),
        Reject()
    )
    OptIn = Seq(
        Approve()
    )
    OnCreate = Seq(
        Approve()
    )

    on_call_method = Txn.application_args[0]

    OnCall = Cond(
        [on_call_method == Bytes("increment_call"), increment_call],

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