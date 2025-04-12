from typing import Literal

from react_agent.state import State

def is_start_of_game(state: State) -> Literal["setup_game", "check_for_weapons_key"]:
    """Determine if a new game is being started.

    This function checks if there is an inprogess game. If not
    it runs a new game setup

    Args:
        state (State): The current state of the conversation.

    Returns:
        str: The name of the next node to call ("setup_game" or "check_for_weapons_key").
    """
    print(state.is_start_of_game)
    return "setup_game" if state.is_start_of_game else "check_for_weapons_key"

def is_weapons_key_guessed(state: State) -> Literal["call_model", "won_game", "incorrect_weapons_key"]:
     """Determine if a weapons key guess has been attempted and if the 
     guess was correct or incorrect

    Args:
        state (State): The current state of the conversation.

    Returns:
        str: The name of the next node to call ("call_model", "won_game", "incorrect_weapons_key").
    """
     
     if state.user_discovered_weapons_key is None:
          return "call_model"
     
     if state.user_discovered_weapons_key:
          return "won_game"
     else:
          return "incorrect_weapons_key"
          