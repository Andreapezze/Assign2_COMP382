# DFA to CFG Converter

A desktop application that converts a **Deterministic Finite Automaton (DFA)** into an equivalent **Context-Free Grammar (CFG)**. Built with Python and Tkinter as a class assignment.

---

## Team

| Name | ID | Role |
|--------|------|------|
| Abdellah Lachhab | 300190682 | Frontend |
| Andrea pezzella | 300179475 | Frontend |
| Jang Toor | | Backend |
| Tanishka | | Backend |

---

## Project Structure

```
dfa-to-cfg/
│
├── main.py               
├── frontend/
│   └── app.py              ← UI code (Tkinter)
├── backend/
│   └── dfa_to_cfg.py       ← conversion algorithm
└── README.md
```

---

## How the App Works

1. User fills in DFA fields (states, alphabet, start state, accept states)
2. A transition table is auto-generated. User can modify any cell
3. User clicks "Convert"
4. Frontend builds the DFA dictionary and passes it to the backend function
5. Backend returns a CFG dictionary
6. App displays the CFG production rules

---

## The Algorithm

*(To be filled in by the backend team)*

---

## Frontend ↔ Backend Interface

This section defines the exact data formats that both teams must follow. The frontend is responsible for building the DFA dictionary from the user's input and passing it to the backend function. The backend is responsible for processing that dictionary and returning a CFG dictionary in the format below.

The function is called as follows:

```python
from backend.dfa_to_cfg import convert_dfa_to_cfg

cfg = convert_dfa_to_cfg(dfa)
```

### Input (Frontend → Backend)

The frontend will always pass a dictionary with the following structure. The backend should expect exactly this and nothing else.

```python
dfa = {
    "states": ["q0", "q1", "q2"],
    "alphabet": ["a", "b"],
    "transitions": {
        ("q0", "a"): "q1",
        ("q0", "b"): "q2",
        ("q1", "a"): "q0",
        ("q1", "b"): "q2",
        ("q2", "a"): "q2",
        ("q2", "b"): "q2"
    },
    "start_state": "q0",
    "accept_states": ["q1"]
}
```

### Output (Backend → Frontend)

The backend will always return a dictionary with the following structure. The frontend will use this to display the CFG production rules.

```python
cfg = {
    "variables": ["q0", "q1", "q2"],
    "terminals": ["a", "b"],
    "start_variable": "q0",
    "productions": {
        "q0": ["a q1", "b q2"],
        "q1": ["a q0", "b q2", "ε"],
        "q2": ["a q2", "b q2"]
    }
}
```

The CFG will be presented as follows:

```
q0 → a q1 | b q2
q1 → a q0 | b q2 | ε
q2 → a q2 | b q2

Start Variable: q0
Terminals: a, b
```

---

## Validation

- A start state must be selected
- At least one accept state must be selected
- Transition table cells are dropdowns so invalid input is not possible

---

## Git Workflow

- Don't push directly to `main`
- Each person works on their own branch
- Open a pull request to merge into `main`

---

## References

*(To be filled in)*
