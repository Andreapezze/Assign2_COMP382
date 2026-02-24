from typing import Dict, List, Tuple, Any


def convert_dfa_to_cfg(dfa: Dict[str, Any]) -> Dict[str, Any]:

    _validate_dfa(dfa)

    states: List[str] = dfa["states"]
    alphabet: List[str] = dfa["alphabet"]
    transitions: Dict[Tuple[str, str], str] = dfa["transitions"]
    start_state: str = dfa["start_state"]
    accept_states: List[str] = dfa["accept_states"]

    # Initialize productions for every state
    productions: Dict[str, List[str]] = {state: [] for state in states}

    # Add production from transitions: q -> a p
    for (from_state, symbol), to_state in transitions.items():
        productions[from_state].append(f"{symbol} {to_state}")

    # Add epsilon productions for accept states: f -> ε
    for f in accept_states:
        productions[f].append("ε")

    # remove duplicates plus the keep stable order
    for state in productions:
        seen = set()
        cleaned = []
        for rule in productions[state]:
            if rule not in seen:
                seen.add(rule)
                cleaned.append(rule)
        productions[state] = cleaned

    cfg = {
        "variables": states[:],
        "terminals": alphabet[:],
        "start_variable": start_state,
        "productions": productions
    }
    return cfg


def _validate_dfa(dfa: Dict[str, Any]) -> None:
    required_keys = {"states", "alphabet", "transitions", "start_state", "accept_states"}
    missing = required_keys - set(dfa.keys())
    if missing:
        raise ValueError(f"DFA is missing required keys: {sorted(missing)}")

    states = dfa["states"]
    alphabet = dfa["alphabet"]
    transitions = dfa["transitions"]
    start_state = dfa["start_state"]
    accept_states = dfa["accept_states"]

    if not isinstance(states, list) or not all(isinstance(s, str) for s in states) or len(states) == 0:
        raise ValueError("dfa['states'] must be a non-empty list of strings.")

    if not isinstance(alphabet, list) or not all(isinstance(a, str) for a in alphabet) or len(alphabet) == 0:
        raise ValueError("dfa['alphabet'] must be a non-empty list of strings.")

    if start_state not in states:
        raise ValueError("Start state must be selected and must be one of the DFA states.")

    if not isinstance(accept_states, list) or len(accept_states) == 0:
        raise ValueError("At least one accept state must be selected.")

    bad_accept = [s for s in accept_states if s not in states]
    if bad_accept:
        raise ValueError(f"Accept states must be in states. Invalid: {bad_accept}")

    if not isinstance(transitions, dict):
        raise ValueError("dfa['transitions'] must be a dictionary mapping (state, symbol) -> state.")

    # Validate each transition entry
    for k, v in transitions.items():
        if (
            not isinstance(k, tuple)
            or len(k) != 2
            or not isinstance(k[0], str)
            or not isinstance(k[1], str)
        ):
            raise ValueError("Transition keys must be tuples like ('q0', 'a').")

        from_state, symbol = k
        to_state = v

        if from_state not in states:
            raise ValueError(f"Transition has invalid from_state '{from_state}' not in states.")
        if symbol not in alphabet:
            raise ValueError(f"Transition has invalid symbol '{symbol}' not in alphabet.")
        if to_state not in states:
            raise ValueError(f"Transition goes to invalid to_state '{to_state}' not in states.")

    # Every (state, symbol) pair should exist
    for s in states:
        for a in alphabet:
            if (s, a) not in transitions:
                raise ValueError(f"Missing transition for ({s}, {a}). DFA must be complete.")
