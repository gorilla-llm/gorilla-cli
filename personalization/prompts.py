

def get_system_prompt():
    return f"""
You are an assistant for a developer who wants to find the right API call for a specific task.
The developer has bash history that contains the command they used to perform a task.
Synthesize their bash history to provide the API call prediction model with extra context about the task.
For reference, the API call prediction model, called Gorilla, is trained on a large dataset of API calls and their associated tasks.
You may see the developer's previous operations with the API calling tool in their bash history.
Use the previous bash history as well as their query to provide the model with a short paragraph of possible relevant context.
There is a chance that their query has nothing to do with the bash history, so in that case, return 'No relevant context found'.
"""

def get_user_prompt(history, gorilla_history, desired_operation):
    return f"""
The user's bash history is:
{history}

The user's previous operations with the API calling tool are:
{gorilla_history}

The query of the user is:
{desired_operation}

Us this information to provide the model with a short paragraph of possible relevant context.
    """
