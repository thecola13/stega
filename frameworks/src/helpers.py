from termcolor import colored

def vprint(msg, type = "info", level = 1, verbose = 1):
    ''' 
    Helper function to print messages. Different colors for different types.

    Args:
        msg (str): Message to print
        type (str): Type of message (info, success, warning, error)
        level (int): Level of message 
        verbose (int): Verbose level
    
    '''
    colors = {
        "info": "blue",
        "success": "green",
        "warning": "yellow",
        "error": "red"
    }
    if verbose >= level:
        print(colored(f"[{type}] {msg}", colors[type]))