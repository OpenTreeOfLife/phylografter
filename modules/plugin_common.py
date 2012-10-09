def evaluate( string ):
    return eval( string, {"__builtins__":None} ,{} )
