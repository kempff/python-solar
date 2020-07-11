'''
Commands to send from front-end to backend.
'''
SET_MAX_CURRENT = 1
SET_AC_CURRENT = 2
SET_BATTERY_REDISCHARGE_VOLTAGE = 3
SET_BATTERY_RECHARGE_VOLTAGE = 4
SET_BATTERY_CUTOFF_VOLTAGE = 5

'''
Dictionary to lookup text string to send from command
'''
command_dictionary = {
    SET_MAX_CURRENT: "MCHGC",
    SET_AC_CURRENT: "MUCHGC",
    SET_BATTERY_REDISCHARGE_VOLTAGE: "PBDV",
    SET_BATTERY_RECHARGE_VOLTAGE: "PBCV",
    SET_BATTERY_CUTOFF_VOLTAGE: "PSDV",
}