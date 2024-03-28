import pycrc.algorithms

def hex_to_little_endian(hex_string):
    print(hex_string.hex())
    hex_string = hex_string.to_bytes((n.bit_length() + 7) // 8, 'big') or b'\0'
    print(hex_string.hex())
    return hex_string

class CalcCRC:
    def calcCRC(file):
        # CRC Polynom: X16+X12+X5+1
        # crcval = 0
        size = len(file)
        with open(file, 'rb') as f:
            while chunk := f.read(size):
                # chunk = hex_to_little_endian(chunk)
                crc = pycrc.algorithms.Crc(width = 16, poly = 0b10001000000100001, \
                    reflect_in = True, xor_in = 0xffff, \
                    reflect_out = True, xor_out = 0x0000)
                my_crc = crc.bit_by_bit_fast(chunk)          # calculate the CRC, using the bit-by-bit-fast algorithm.
            print('{:#04x}'.format(my_crc))
                # for j in range(100000):
                    # crc=0xffff
                    # tmp_data = array1[j].tobytes()
                    # crc=binascii.crc_hqx(zb, crc)
                    # crc=binascii.crc_hqx(tmp_data, crc)

                    # tmp_data = array2[j].tobytes()
                    # crc=binascii.crc_hqx(zb, crc)
                    # crc=binascii.crc_hqx(tmp_data, crc)
        # buf = (binascii.crc32(buf))# & 0b1000100000010001)
        # print("CRC 0x" + format(crcval, 'X'))
