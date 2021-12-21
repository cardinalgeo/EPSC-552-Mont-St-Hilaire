from mendeleev.fetch import fetch_table

def get_elements(candidate_list): 
    # elements in periodic table
    ptable = fetch_table('elements').symbol.to_list()

    elements = set(ptable) & set(candidate_list)
    elements = list(elements)
    elements.sort()

    return elements # sorted list of elements in candidate_list