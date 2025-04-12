from typing import Dict, List, cast

from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from react_agent.configuration import Configuration
from react_agent.prompts import *

from react_agent.state import InputState, State
from react_agent.utils import load_chat_model

# Define the function that calls the model
async def call_model(
    state: State, config: RunnableConfig
) -> Dict[str, List[AIMessage]]:
    """Call the LLM powering our "agent".

    This function prepares the prompt, initializes the model, and processes the response.

    Args:
        state (State): The current state of the conversation.
        config (RunnableConfig): Configuration for the model run.

    Returns:
        dict: A dictionary containing the model's response message.
    """
    configuration = Configuration.from_runnable_config(config)

    # Initialize the model with tool binding. Change the model or add more tools here.
    model = load_chat_model(
        configuration.model_provider, 
        configuration.model_name,
        configuration.ollama_base_url
        )

    secret_key = configuration.secret_key
    # Format the system prompt. Customize this to change the agent's behavior.
    if configuration.game_difficulty.lower() == 'hard':
        system_message = configuration.hard_system_prompt.format(secret_key=secret_key)
    elif configuration.game_difficulty.lower() == 'medium':
        system_message = configuration.medium_system_prompt.format(secret_key=secret_key)
    else:
        system_message = configuration.easy_system_prompt.format(secret_key=secret_key)

    # Get the model's response
    response = cast(
        AIMessage,
        await model.ainvoke(
            [{"role": "system", "content": system_message}, *state.messages], config
        ),
    )

    # Handle the case when it's the last step and the model still wants to use a tool
    if state.is_last_step and response.tool_calls:
        return {
            "messages": [
                AIMessage(
                    id=response.id,
                    content="Sorry, I could not find an answer to your question in the specified number of steps.",
                )
            ]
        }

    # Return the model's response as a list to be added to existing messages
    return {"messages": [response]}

async def check_incoming_message(
    state: State, config: RunnableConfig
) -> Dict[str, List[AIMessage]]:
    """Checks if the most recent message returns the secret

    Args:
        state (State): The current state of the conversation.
        config (RunnableConfig): Configuration for the model run.

    Returns:
        dict: A dictionary containing the model's response message.
    """
    configuration = Configuration.from_runnable_config(config)

    # Initialize the model with tool binding. Change the model or add more tools here.
    model = load_chat_model(
        configuration.model_provider, 
        configuration.model_name,
        configuration.ollama_base_url
        )

    # Format the system prompt. Customize this to change the agent's behavior.
    system_message = WARN_CAPTAIN_PROMPT.format(secret_key=configuration.secret_key)

    # Get the model's response
    response = cast(
        AIMessage,
        await model.ainvoke(
            [{"role": "system", "content": system_message}, state.messages[-1]], config
        ),
    )

    is_incoming_message_malicious = True if 'malicious' in response.content else False

    if is_incoming_message_malicious:
        return {
            "messages": [{"role": "system", "content": MALICIOUS_WARNING_PROMPT}],
            "is_incoming_message_malicious": is_incoming_message_malicious
            }
    
async def setup_game(
    state: State, config: RunnableConfig
) -> Dict[str, List[AIMessage]]:
    """Sets up the game with a new story and task

    Args:
        state (State): The current state of the conversation.
        config (RunnableConfig): Configuration for the model run.

    Returns:
        dict: A dictionary containing the game start messages.
    """

    first_message = SystemMessage(NEW_GAME_PROMPT)

    return {"messages": [first_message], "is_start_of_game": False}

async def check_for_weapons_key(
        state: State, config: RunnableConfig
) -> Dict[str, bool]:
    """Checks the user input for a correct weapons key guess

    Args:
        state (State): The current state of the conversation.
        config (RunnableConfig): Configuration for the model run.

    Returns:
        dict: A dictionary containing the updated value if user guessed the weapons key.
    """
    # Grab config
    configuration = Configuration.from_runnable_config(config)

    # Grab the last user message
    last_message = state.messages[-1].content

    if last_message.startswith("WEAPONS KEY GUESS: "):
        print("incoming_weapons_key_guess")
        weapons_key_guess = last_message.split(":",1)[1].strip().lower()
        return {"user_discovered_weapons_key": weapons_key_guess == configuration.secret_key.lower()} 
    else:
        return

async def incorrect_weapons_key(
        state: State, config: RunnableConfig
) -> Dict[str, List[AIMessage]]:
    """Captain is made aware that the user attempted to guess the weapons key.
    How will he respond?

    Args:
        state (State): The current state of the conversation.
        config (RunnableConfig): Configuration for the model run.

    Returns:
        dict: A dictionary containing the ai response to the incorrect
            weapons key guess
    """

    incorrect_guess_prompt = SystemMessage(INCORRECT_GUESS_PROMPT)

    configuration = Configuration.from_runnable_config(config)

    # Initialize the model with tool binding. Change the model or add more tools here.
    model = load_chat_model(
        configuration.model_provider, 
        configuration.model_name,
        configuration.ollama_base_url
        )

    secret_key = configuration.secret_key
    # Format the system prompt. Customize this to change the agent's behavior.
    if configuration.game_difficulty.lower() == 'hard':
        system_message = configuration.hard_system_prompt.format(secret_key=secret_key)
    elif configuration.game_difficulty.lower() == 'medium':
        system_message = configuration.medium_system_prompt.format(secret_key=secret_key)
    else:
        system_message = configuration.easy_system_prompt.format(secret_key=secret_key)

    user_weapons_guess = state.messages.pop()

    if not isinstance(user_weapons_guess, HumanMessage):
        print((
            "WARNING: Expected to remove weapons guess, instead removed: "
            f"{user_weapons_guess.__dict__}"
            ))

    print(state.messages[-1].__dict__)
    # Get the model's response
    response = cast(
        AIMessage,
        await model.ainvoke(
            [
                {"role": "system", "content": system_message}, 
                *state.messages, 
                incorrect_guess_prompt
            ], 
            config
        ),
    )

    return {"messages": [incorrect_guess_prompt,response], "user_discovered_weapons_key": None}

async def won_game(
        state: State, config: RunnableConfig
) -> Dict[str, List[AIMessage]]:
    """The user has won the game! Send the congrats message

    Args:
        state (State): The current state of the conversation.
        config (RunnableConfig): Configuration for the model run.

    Returns:
        dict: A dictionary containing the response to winning the same
    """

    if state.user_discovered_weapons_key:
        win_message = AIMessage(CORRECT_GUESS_PROMPT)
        return {"messages": [win_message], "is_start_of_game": True}
    
    return

