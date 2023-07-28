import data_getter as dg

def go_bundle(curr_input, curr_out, curr_fiat, bank_insert, bank_withdraw, amount)-> dict:
    try:
        result = dg.Bundle.get_diff()
        return (result)

    except Exception as exc:
        return exc