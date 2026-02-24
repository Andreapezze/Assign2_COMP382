# this is a mock so the frontend can be tested independently
def convert_dfa_to_cfg(dfa):

    productions = {}
    for state in dfa["states"]:
        rules = []
        for (st, sym), ns in dfa["transitions"].items():
            if st == state:
                rules.append(f"{sym} {ns}")
        if state in dfa["accept_states"]:
            rules.append("ε")
        productions[state] = rules
    return {
        "variables": dfa["states"],
        "terminals": dfa["alphabet"],
        "start_variable": dfa["start_state"],
        "productions": productions
    }