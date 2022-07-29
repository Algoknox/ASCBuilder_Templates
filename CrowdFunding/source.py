from pyteal import *

def approval_program():

    txn_a_type_enum = TxnType.ApplicationCall

    txn_b_type_enum = TxnType.Payment

    zero_address = Global.zero_address()

    txn_a_type = Gtxn[0].type_enum()

    txn_b_type = Gtxn[1].type_enum()

    txn_b_amount = Gtxn[1].amount()

    min_amount_to_send = Int(100000)

    group_size = Global.group_size()

    size = Int(2)

    txn_b_rekey_to = Gtxn[1].rekey_to()

    txn_b_close_remainder_to = Gtxn[1].close_remainder_to()

    receive_funds = Seq(
        If (
            And(
                txn_a_type_enum == txn_a_type,
                txn_b_type_enum == txn_b_type,
                txn_b_rekey_to == zero_address,
                txn_b_close_remainder_to == zero_address,
                txn_b_amount >= min_amount_to_send
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
        Reject()
    )

    txn_sender = Txn.sender()

    creator_address = Global.creator_address()

    one = Int(1)

    application_address = Global.current_application_address()

    min_balance = MinBalance(application_address)

    disburse_to = Addr('HQY7QS7PICZMKJOOXCCARQ2E6W237M54T3LRLSHT6GBGHQC5GSMIQMPKHA')

    balance = Balance(application_address)

    withdrawable_balance = balance - min_balance

    disburse_funds = Seq(
        If (
            And(
                group_size == one,
                txn_sender == creator_address
            )
        ).Then(
            Seq(
                InnerTxnBuilder.Begin(),
                InnerTxnBuilder.SetFields(
                    {
                        TxnField.type_enum:TxnType.Payment,
                        TxnField.sender:Global.current_application_address(),
                        TxnField.fee:Int(0),
                        TxnField.receiver:disburse_to,
                        TxnField.amount:withdrawable_balance
                    }
                ),
                InnerTxnBuilder.Submit(),
                Approve()
            )
        ).Else(
            Seq(
                Reject()
            )
        ),
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
        [on_call_method == Bytes("receive_funds"), receive_funds],
        [on_call_method == Bytes("disburse_funds"), disburse_funds],

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