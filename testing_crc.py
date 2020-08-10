import crc16

POLYNOMIAL = 0x1021
PRESET = 0

def _initial(c):
    crc = 0
    c = c << 8
    for j in range(8):
        if (crc ^ c) & 0x8000:
            crc = (crc << 1) ^ POLYNOMIAL
        else:
            crc = crc << 1
        c = c << 1
    return crc

_tab = [ _initial(i) for i in range(256) ]

def _update_crc(crc, c):
    cc = 0xff & c

    tmp = (crc >> 8) ^ cc
    crc = (crc << 8) ^ _tab[tmp & 0xff]
    crc = crc & 0xffff

    return crc

def crc(str):
    crc = PRESET
    for c in str:
        crc = _update_crc(crc, ord(c))
    return crc

def checkCRC(message):
    #CRC-16-CITT poly, the CRC sheme used by ymodem protocol
    poly = 0x11021
    #16bit operation register, initialized to zeros
    reg = 0xFFFF
    #pad the end of the message with the size of the poly
    message += '\x00\x00' 
    #for each bit in the message
    for byte in message:
        mask = 0x80
        while(mask > 0):
            #left shift by one
            reg<<=1
            #input the next bit from the message into the right hand side of the op reg
            if ord(byte) & mask:   
                reg += 1
            mask>>=1
            #if a one popped out the left of the reg, xor reg w/poly
            if reg > 0xffff:            
                #eliminate any one that popped out the left
                reg &= 0xffff           
                #xor with the poly, this is the remainder
                reg ^= poly
    return reg


#hex_data = "283233322e302035302e30203232392e392035302e302030333637203032383920303037203335322035302e3530203030302030383320303033342030303030203030302e302030302e303020303030303620303030313030303020303020303020303030303020303130b80e0d"
#hex_data = "283232392e312034392e39203233302e302034392e392030363434203035383720303132203334362034392e3730203030302030373520303033342030303030203030302e302030302e3030203030303132203030303130303030203030203030203030303030203031300bd60d"
#hex_data = "283233352e332034392e38203232392e392034392e382030333930203033323320303037203335372035312e3130203030302030383920303033362030303032203037302e302035312e313320303030303420303031313031313020303020303020303031333820303130b9290d"
hex_data = "283233382e302034392e39203232392e392034392e392030333930203033323920303037203337372035332e3930203030322031303020303033352030303039203038322e352035332e393320303030303020303031313031313020303020303020303034393620313130350e0d"

bytes_data = bytearray.fromhex(hex_data)
check_data = bytes(bytes_data[:-3])
crc1 = crc16.crc16xmodem(check_data)

check_data2 = ''.join(chr(x) for x in check_data) 
crc2 = crc(check_data2)

print(bytes_data)
print(f"RX: {hex_data[-6:-2]} Calc: {hex(crc1)}")

print(check_data2)
print(f"RX: {hex_data[-6:-2]} Calc: {hex(crc2)}")

