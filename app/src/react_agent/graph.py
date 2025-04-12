"""Define a custom Reasoning and Action agent.

Works with a chat model with tool calling support.
"""
from langgraph.graph import StateGraph

from react_agent.configuration import Configuration
from react_agent.edges import is_start_of_game, is_weapons_key_guessed
from react_agent.nodes import (
    call_model, 
    check_incoming_message, 
    setup_game,
    check_for_weapons_key,
    incorrect_weapons_key,
    won_game
)
from react_agent.prompts import WARN_CAPTAIN_PROMPT, MALICIOUS_WARNING_PROMPT
from react_agent.state import InputState, State
from react_agent.tools import TOOLS
from react_agent.utils import load_chat_model

# Define a new graph
builder = StateGraph(State, input=InputState, config_schema=Configuration)

# Define the main node
builder.add_node(call_model)
builder.add_node(setup_game)
builder.add_node(check_for_weapons_key)
builder.add_node(incorrect_weapons_key)
builder.add_node(won_game)

# Add a conditional edge to determine the next step after `call_model`
builder.add_conditional_edges(
    "__start__",
    # After call_model finishes running, the next node(s) are scheduled
    # based on the output from route_model_output
    is_start_of_game,
)

builder.add_edge("setup_game", "check_for_weapons_key")

# Checks if the weapons key was guesses
builder.add_conditional_edges(
    "check_for_weapons_key",
    is_weapons_key_guessed
)

# Add a normal edge from `tools` to `call_model`
# This creates a cycle: after using tools, we always return to the model
# builder.add_edge("tools", "call_model")
builder.add_edge("call_model", "__end__")
builder.add_edge("incorrect_weapons_key", "__end__")
builder.add_edge("won_game", "__end__")

# Compile the builder into an executable graph
# You can customize this by adding interrupt points for state updates
graph = builder.compile(
    interrupt_before=[],  # Add node names here to update state before they're called
    interrupt_after=[],  # Add node names here to update state after they're called
)
graph.name = "Game Agent"  # This customizes the name in LangSmith

"""
Below is the implementation of the Extra Hard version of the game.
At this time it is not completed. The concept is all messages from the user
are vetted, and malicious ones are tagged with a warning message.
"""

extra_hard_builder = StateGraph(State, input=InputState, config_schema=Configuration)

# Define the main node
extra_hard_builder.add_node(call_model)
extra_hard_builder.add_node(check_incoming_message)

# Set the entrypoint as `call_model`
# This means that this node is the first one called
extra_hard_builder.add_edge("__start__", "check_incoming_message")
extra_hard_builder.add_edge("check_incoming_message", "call_model")

extra_hard_builder.add_edge("call_model", "__end__")

# Compile the extra_hard_builder into an executable graph
# You can customize this by adding interrupt points for state updates
extra_hard_graph = extra_hard_builder.compile(
    interrupt_before=[],  # Add node names here to update state before they're called
    interrupt_after=[],  # Add node names here to update state after they're called
)
extra_hard_graph.name = "Extra Hard Game Agent"  # This customizes the name in LangSmith