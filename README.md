# DFA to CFG Converter

A desktop application that converts a **Deterministic Finite Automaton (DFA)** into an equivalent **Context-Free Grammar (CFG)**. Built with Python and Tkinter as a class assignment.

---

## Team

| Name | ID | Role |
|--------|------|------|
| Abdellah Lachhab | 300190682 | Frontend |
| Andrea pezzella | 300179475 | Frontend |
| Jang Toor |300211868 | Backend |
| Tanishka | 300200109 | Backend |

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

This application creates a similar right-linear grammar (a Context-Free Grammar that produces a regular language) from a Deterministic Finite Automaton (DFA).

Main concept:
Every DFA state turns into a non-terminal CFG variable.
Every DFA transition turns into a rule for production.
In order for the string to terminate, each accept (final) state also receives an epsilon production.

Formal conversion rules: 
We construct a CFG G = (V, Σ, R, S) given a DFA with states Q, alphabet Σ, transition function δ, start state q0, and accept states F.The DFA states Q are variables V.
The DFA alphabet Σ is used for terminals.
The DFA start state q0 is represented by the start variable S.

1) For every transition δ(q, a) = p, add the production:
q → a p

2) For every accept state f in F, add the production:
f → ε

Example:
If the DFA contains δ(q0, a) = q1 and δ(q0, b) = q2, and q1 is an accept state, then the CFG includes:
q0 → a q1 | b q2
q1 → ε

The frontend receives the output format back from the backend as a dictionary containing:- variables: the DFA states list
The list of DFA alphabet symbols is the terminals.
The DFA start state is the start_variable.
A dictionary that associates each variable with its set of production strings is called "productions."

For instance, productions for q0 might include: a q1 and b q2.
Validation notes: To avoid problems and offer unambiguous error messages, the backend validates the received DFA dictionary even though the user interface uses dropdowns to limit inputs. It verifies:- there are needed fields (start_state, accept_states, transitions, states, and alphabet).
The start_state is a legitimate state.
All accept states are legitimate, and there is at least one accept state.
Transitions employ (state, symbol) keys, and the symbols are alphabetic. The DFA is finished.

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

- JFLAP Workshop 2014, Arvind B. [Converting a DFA to a CFG](https://www.jflap.org/modules/JFLAPWorkshop2014/Upload%20Exercises%20and%20Modules%20here/ArvindB/Exercises/RegularGrammar/Regular2CFG.pdf)
- Converting a DFA to a context free grammar (CFG) [Video]. (n.d.). YouTube. https://www.youtube.com/watch?v=NrRZi89TiYM
- Ekeeda. (n.d.). DFA to right linear grammar (RLG) [Video]. YouTube. https://www.youtube.com/watch?v=xmknBzUHLIc
- Gordon College. (n.d.). CPS 220 – Theory of computation: CFL [PDF]. https://www.cs.gordon.edu/courses/cps220/Notes/CFL.pdf
- WhiteMech. (n.d.). pythomata. GitHub. https://github.com/whitemech/pythomata

## Libraries Used

- `tkinter` — Desktop GUI
- `unittest` — Backend testing
