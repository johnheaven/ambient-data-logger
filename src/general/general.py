def get_env_vars(env_vars, return_type='dict'):
    """Returns a dictionary or tuple of the specified environment variables
    Args:
        env_vars (list or tuple, optional): The names of env vars to return.
    Returns:
        dict or tuple: The env vars
    """
    from dotenv import load_dotenv
    import os

    load_dotenv()
    
    if return_type == 'dict':
        return {env_var: os.environ[env_var] for env_var in env_vars}
    else:
        return (os.environ[env_var] for env_var in env_vars)
