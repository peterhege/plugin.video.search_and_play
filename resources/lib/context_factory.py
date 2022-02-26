from resources.lib.control import dialog, call_user_func

previous_functions = []


def show(menu, this=None, main=False):
    global previous_functions
    if main:
        previous_functions = []
    selected_menu = dialog.contextmenu(menu.values())
    if selected_menu > -1:
        if this:
            previous_functions.append(this)
        else:
            previous_functions = []
        callable_name = menu.keys()[selected_menu]
        return call_user_func(callable_name)
    if len(previous_functions):
        return call_user_func(previous_functions.pop())
    return None
