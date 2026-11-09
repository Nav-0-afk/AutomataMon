import xml.etree.ElementTree as ET
import os


class JFLAPAutomaton:
    def __init__(self, jff_filename="States.jff"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        jff_path = os.path.join(base_dir, jff_filename)

        self.id_to_name = {}
        self.accepting_states = set()
        self.transitions = {}

        tree = ET.parse(jff_path)
        root = tree.getroot()
        automaton = root.find("automaton")

        # 1. Parse all states and identify Accepting (<final/>) states
        for state in automaton.findall("state"):
            s_id = state.attrib["id"]
            s_name = state.attrib["name"]
            self.id_to_name[s_id] = s_name
            self.transitions[s_name] = {}

            if state.find("final") is not None:
                self.accepting_states.add(s_name)

        # 2. Parse all delta transitions
        for trans in automaton.findall("transition"):
            from_name = self.id_to_name[trans.find("from").text]
            to_name = self.id_to_name[trans.find("to").text]
            symbol = trans.find("read").text
            if symbol:
                self.transitions[from_name][symbol] = to_name

    def step(self, current_state, action_input):
        new_state = self.transitions.get(current_state, {}).get(action_input, current_state)
        can_attack = new_state in self.accepting_states
        return new_state, can_attack


# Instantiate once and expose process_turn for pokemon.py
_dfa = JFLAPAutomaton("States.jff")  # Change filename if your .jff is named differently


def process_turn(current_state, action_input):
    return _dfa.step(current_state, action_input)

ACCEPTING_STATES = _dfa.accepting_states
accept_states = _dfa.accepting_states
current_state = "q0"