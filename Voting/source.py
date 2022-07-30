from pyteal import *

def approval_program():

    start_date = Bytes('start_date')

    end_date = Bytes('end_date')

    positive = Bytes('positive')

    negative = Bytes('negative')

    start_date_state = App.globalGet(start_date)

    end_date_state = App.globalGet(end_date)

    positive_state = App.globalGet(positive)

    txn_sender = Txn.sender()

    choice = Bytes('choice')

    increment = Int(1)

    negative_state = App.globalGet(negative)

    user_choice = App.localGet(txn_sender, choice)

    timestamp = Global.latest_timestamp()

    zero = Int(0)

    decision = Txn.application_args[1]

    increment_user_choice = App.globalGet(decision)

    incrementation = increment_user_choice + increment

    cast_vote = Seq(
        If (
            And(
                timestamp >= start_date_state,
                timestamp <= end_date_state,
                user_choice != zero
            )
        ).Then(
            Seq(
                App.globalPut(increment_user_choice, incrementation),
        App.localPut(txn_sender, choice, decision),
                Approve()
            )
        ),
        Reject()
    )
    OptIn = Seq(
        Approve()
    )
    OnCreate = Seq(
        App.globalPut(Bytes("start_date"), Int(1659173464)),
        App.globalPut(Bytes("end_date"), Int(1659174464)),
        App.globalPut(Bytes("positive"), Int(0)),
        App.globalPut(Bytes("negative"), Int(0)),
        Approve()
    )

    on_call_method = Txn.application_args[0]

    OnCall = Cond(
        [on_call_method == Bytes("cast_vote"), cast_vote],

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

    user_state_key = Bytes('choice')

    sender = Txn.sender()

    choice_of_user = App.localGet(sender, user_state_key)

    zero_value = Int(0)

    one = Int(1)

    decrement_from = App.globalGet(choice_of_user)

    deduct = decrement_from - one

    clearProgram = Seq(
        If (
            choice_of_user != zero_value
        ).Then(
            Seq(
                App.localDel(sender, user_state_key),
        App.globalPut(decrement_from, deduct),
                Approve()
            )
        ).Else(
            Seq(
        Approve()
            )
        ),
        Reject()
    )
    return clearProgram

if __name__ == "__main__":
    with open("approval.teal", "w") as f:
        compiled = compileTeal(approval_program(), mode=Mode.Application, version=5)
        f.write(compiled)

    with open("clear.teal", "w") as f:
        compiled = compileTeal(clear_program(), mode=Mode.Application, version=5)
        f.write(compiled)