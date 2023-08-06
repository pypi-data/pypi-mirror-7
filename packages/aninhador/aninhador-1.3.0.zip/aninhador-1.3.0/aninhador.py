"""This is the "aninhador.py" module, and it provides one function called
print_lol() which prints lists that may or may not include nested lists"""
def print_lol(the_list, indent=False, level=0):
    """This function takes a positional argument called "the_list", which is
    any Python list (of, possibly, nested lists). Each data item in the
    provided list is (recursively) printed to the screen on its own line.
    A second argument called "indent" determines if the list in printed with
    identation on each of its nested lists. A third argument called "level"
    is used to insert tab-stops when a nested list is encountered."""
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, indent, level+1)
        else:
            if indent:
                print('\t' * level, end='')
            print(each_item)
