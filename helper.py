# give 2 string choices and a state; outputs opposite state like, [in]on -> [out]off.
# state = off
# choices = ['on', 'off']
# returns on
def flip(state, choices):
    if len(choices) < 1:
        return 
    state = str(state).strip()
    if state in choices:
        choices.remove(state)
    return choices[0]