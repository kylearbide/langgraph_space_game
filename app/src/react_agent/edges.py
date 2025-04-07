from typing import Literal

from react_agent.state import State

def is_start_of_game(state: State) -> Literal["setup_game", "call_model"]:
    """Determine if a new game is being started.

    This function checks if there is an inprogess game. If not
    it runs a new game setup

    Args:
        state (State): The current state of the conversation.

    Returns:
        str: The name of the next node to call ("setup_game" or "call_model").
    """
    print(state.is_start_of_game)
    return "setup_game" if state.is_start_of_game else "call_model"