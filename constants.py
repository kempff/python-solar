'''
Commands to send from front-end to backend.
'''
SET_MAX_CURRENT = 1
SET_AC_CURRENT = 2

'''
Dictionary to lookup text string to send from command
'''
command_dictionary = {
    SET_MAX_CURRENT: "MCHGC",
    SET_AC_CURRENT: "MUCHGC",
}