import os
import xml.etree.ElementTree as ET


def load_jflap_dfa(filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(base_dir, filename)

    tree = ET.parse(filepath)

    transition_table = {}
    accept_states = set()
    start_state = None
    state_names = {}

    # 1. Parse all states using .iter() to bypass strict tag hierarchy
    for state in tree.iter('state'):
        state_id = state.get('id')
        state_name = state.get('name')
        state_names[state_id] = state_name
        transition_table[state_name] = {}

        if state.find('initial') is not None:
            start_state = state_name
        if state.find('final') is not None:
            accept_states.add(state_name)

    # 2. Parse all transitions using .iter()
    for transition in tree.iter('transition'):
        from_id = transition.find('from').text
        to_id = transition.find('to').text
        read_symbol = transition.find('read').text

        from_name = state_names[from_id]
        to_name = state_names[to_id]

        transition_table[from_name][read_symbol] = to_name

    return transition_table, start_state, accept_states


# Load the JFLAP file
transition_table, current_state, accept_states = load_jflap_dfa("States.jff")


def process_turn(state, action_input):
    """
    Evaluates the transition and returns the new state and whether the turn is valid.
    """
    new_state = transition_table[state][action_input]
    can_attack = new_state in accept_states
    return new_state, can_attack
