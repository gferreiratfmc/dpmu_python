import sys, os
from os import path

# update mypath - 'canlib32.dll' must recide here
my_path = 'C:\Program Files\Kvaser\Drivers'
bundle_dir = getattr(sys, '_MEIPASS', path.abspath(path.dirname(__file__)))
path_to_dat = path.abspath(path.join(bundle_dir, my_path))
os.environ['KVDLLPATH'] = path_to_dat
print(os.environ['KVDLLPATH'])

import threading
from canlib import canlib
from canlib.canlib import ChannelData

def setUpChannel(channel=0,
                 openFlags=canlib.canOPEN_ACCEPT_VIRTUAL,
                 bitrate=canlib.canBITRATE_125K,
                 bitrateFlags=canlib.canDRIVER_NORMAL):
    ch = canlib.openChannel(channel, openFlags)
    print("Using channel: %s, EAN: %s" % (ChannelData.channel_name,
                                          ChannelData(channel).card_upc_no)
                                              )
    ch.setBusOutputControl(bitrateFlags)
    ch.setBusParams(bitrate)
    ch.busOn()
    return ch

def tearDownChannel(ch):
    print("Bus " + format(ch) + "closing")
    ch.busOff()
    ch.close()

class canOD:
    sdoBlock=0
    sdoBlockTransferOngoing=0
    ackSeq=0

def high_byte(x):
    return (x>>8)&0xff

def low_byte(x):
    return (x)&0xff

def msg_as_string(msg):
    # 'id', 'data', 'dlc', 'flags', 'timestamp'
    # Frame(id=1537, data=bytearray(b'/\x10@\x01\x00\x00\x00\x00'), dlc=8, flags=<MessageFlag.STD: 2>, timestamp=5314)
    msg_string= "Frame(id=" + format(msg.id, '03x') + \
                ", data=" + format(msg.data[0], '02x') + \
                " "       + format(msg.data[1], '02x') + \
                " "       + format(msg.data[2], '02x') + \
                " "       + format(msg.data[3], '02x') + \
                " "       + format(msg.data[4], '02x') + \
                " "       + format(msg.data[5], '02x') + \
                " "       + format(msg.data[6], '02x') + \
                " "       + format(msg.data[7], '02x') + \
                "), dlc=" + str(msg.dlc) + \
                 ", flags=" + str(msg.flags) + \
                ", timestamp=" + str(msg.timestamp)  + \
                ")"
    return msg_string

import time
def print_can_message(msg):
    try:
        # print("msg.dlc: {:03x}".format(msg.dlc))
        i=msg.dlc
        string = "ID {:03x}".format(msg.id)
        if i > 0:
            string += " CCS {:02x}".format(msg.data[0])
        if i > 2:
            string += " I {:04x}".format((msg.data[2] << 8) | msg.data[1])
        else:
            if i > 1:
                string += " {:04x}".format(msg.data[1])
        if i > 3:
            string += " S {:02x}".format(msg.data[3])
        if i > 4:
            string += " : {:02x}".format(msg.data[4])
        if i > 5:
            string += " {:02x}".format(msg.data[5])
        if i > 6:
            string += " {:02x}".format(msg.data[6])
        if i > 7:
            string += " {:02x}".format(msg.data[7])

        # print on terminal
        # print(string)

        # add for new line in textbox
        string += "\r\n"

        return string[:-2]
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        return "\r\n"

def print_can_message_raw(msg):
    try:
        # print("msg.dlc: {:03x}".format(msg.dlc))
        i=msg.dlc
        string = "ID {:03x}".format(msg.id)
        if i > 0:
            string += " {:02x}".format(msg.data[0])
        if i > 1:
            string += " {:02x}".format(msg.data[1])
        if i > 2:
            string += " {:02x}".format(msg.data[2])
        if i > 3:
            string += " {:02x}".format(msg.data[3])
        if i > 4:
            string += " : {:02x}".format(msg.data[4])
        if i > 5:
            string += " {:02x}".format(msg.data[5])
        if i > 6:
            string += " {:02x}".format(msg.data[6])
        if i > 7:
            string += " {:02x}".format(msg.data[7])

        # print on terminal
        # print(string)

        # add for new line in textbox
        string += "\r\n"

        return string[:-2]
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        return "\r\n"

class CanReceive():
    def __init__(self):
        # super().__init__()
        pass

    def events():
        # wait for next hb  CAN message
        while True:
            try:
                msg = canopen_DPMU_A_2.read(timeout=1000)
                if msg.flags == canlib.MessageFlag.ERROR_FRAME :
                    pass
                else :
                    # print_can_message(msg)
                    match msg.id & 0x780 :
                        case 0x700:
                            match msg.data[0]:
                                case 0:
                                    print("Heartbeat BOOT_UP " + print_can_message(msg))
                                case 4:
                                    print("Heartbeat STOPPED " + print_can_message(msg))
                                case 5:
                                    print("Heartbeat OPERATIONAL ")
                                case 127:
                                    print("Heartbeat PRE_OPERATIONAL ")
                                case _:
                                    print("Heartbeat ERROR - UNKNOWN STATE ")
                        case 0x080:
                            print("PDO 080 " + print_can_message_raw(msg))#format(msg))
                        case 0x180:
                            print("PDO 180 " + print_can_message(msg))#format(msg))
                        case 0x280:
                            print("PDO 280 " + print_can_message(msg))#format(msg))
                        case 0x380:
                            print("PDO 380 " + print_can_message(msg))#format(msg))
                        case 0x480:
                            print("PDO 480 " + print_can_message(msg))#format(msg))
                        case 0x330:
                            print("NMT answer " + print_can_message(msg))#format(msg))
                        case 0x600:
                            print("SDO 600 " + print_can_message(msg))#msg_as_string(msg))
                        case 0x580:
                            if 1 == canOD.sdoBlockTransferOngoing:
                                print("SDO 580 " + print_can_message_raw(msg))
                            else:
                                print("SDO 580 " + print_can_message(msg))#msg_as_string(msg))
                            can_input_event(msg)
                        # case 0x000:
                            # print("SDO 000 " + msg_as_string(msg))
                        case _:
                            #print(msg)
                            print(print_can_message(msg))
            except canlib.canNoMsg:
                pass
            except canlib.canError as ex:
                print(ex)
                print("Terminating")
                exit()

def sdo_block_transfer(data):
    # print("canOD.sdoBlockTransferOngoing {:01x}".format(canOD.sdoBlockTransferOngoing))
    index = (data[2] << 8) | data[1]

    if 1 == canOD.sdoBlockTransferOngoing:
        messageSent = 0
        canOD.ackSeq += 1
        # print("canOD.ackSeq {:04x}".format(canOD.ackSeq))

        if 0 == canOD.ackSeq%4: # block size = 4
            print("SDO BLOCK TRANSFER DONE")
            canOD.ackSeq = data[0] & 0x7f
            # print("canOD.ackSeq: {:02x}".format(canOD.ackSeq))")
            # if OD.I_DEBUG_LOG == index:
            debuglog.ccs = 0xA2
            debuglog.set_data_byte1(canOD.ackSeq)
            debuglog.set_data_byte2(4)
            debuglog.set_data_byte3(0)
            debuglog.set_data_byte4(0)
            debuglog.set_data_byte5(0)
            debuglog.set_data_byte6(0)
            debuglog.set_data_byte7(0)
            debuglog.sendCanMessage()
            # else:
                # debuglog.ccs = 0xA2
                # debuglog.set_data_byte1(canOD.ackSeq)
                # debuglog.set_data_byte2(4)
                # debuglog.set_data_byte3(0)
                # debuglog.set_data_byte4(0)
                # debuglog.set_data_byte5(0)
                # debuglog.set_data_byte6(0)
                # debuglog.set_data_byte7(0)
                # debuglog.sendCanMessage()
            messageSent = 1

        if 0x80 == data[0] & 0x80: # SDO Block transfer last segment
            canOD.sdoBlockTransferOngoing = 0
            if 0 == messageSent:
                print("SDO BLOCK LAST TRANSFER DONE")
                canOD.ackSeq = data[0] & 0x7f
                # print("canOD.ackSeq: {:02x}".format(canOD.ackSeq))
                debuglog.ccs = 0xA2
                debuglog.set_data_byte1(canOD.ackSeq)
                debuglog.set_data_byte2(4)
                debuglog.set_data_byte3(0)
                debuglog.set_data_byte4(0)
                debuglog.set_data_byte5(0)
                debuglog.set_data_byte6(0)
                debuglog.set_data_byte7(0)
                debuglog.sendCanMessage()
                canOD.sdoBlockTransferOngoing = 0
    else:
        if 0xc1 == data[0] & 0xe1: # SDO Block transfer initate transfer block end
            print("SDO BLOCK END")
            debuglog.ccs = 0xA1
            debuglog.set_data_byte1(0)
            debuglog.set_data_byte2(0)
            debuglog.set_data_byte3(0)
            debuglog.set_data_byte4(0)
            debuglog.set_data_byte5(0)
            debuglog.set_data_byte6(0)
            debuglog.set_data_byte7(0)
            debuglog.sendCanMessage()
            canOD.ackSeq = 0
            canOD.sdoBlock = 0

def can_input_event(msg):
    data = msg.data
    # print_can_message(msg)
    # print(data)
    # print("sdoBlock ", canOD.sdoBlock)

    index = (data[2] << 8) | data[1]
    # print("index {:04x}".format(index))
    subIndex = data[3]
    # print("subIndex {:02x}".format(subIndex))
    value = data[4] +1
    value16 = (data[4]<<8) + data[5] +1
    # print("value   ", value)
    # print("value16 ", value16)
    # print("data[0] ", hex(data[0]))

    if 0 != canOD.sdoBlock :
        sdo_block_transfer(data)
    else:
        pass

    if 0x80 == data[0]: # SDO Abort
        print(  "SDO ABORT  " +
                " index {:04x}".format(index) +
                " subindex {:02x}".format(subIndex) +
                " Error Code: {:02x}".format(data[7]) +
                " {:02x}".format(data[6]) +
                " {:02x}".format(data[5]) +
                " {:02x}".format(data[4]))
        canOD.sdoBlock = 0
        canOD.sdoBlockTransferOngoing = 0

if __name__ == "__main__":
    print("CAN DUMP\r\n")

    # canopen_DPMU_A = setUpChannel(channel=0)
    # canopen_DPMU_A.iocontrol.local_txecho = False
    canopen_DPMU_A_2 = setUpChannel(channel=0)

    t2 = threading.Thread(target=CanReceive.events)
    t2.start()

    while(True):
        if input():
            break

    tearDownChannel(canopen_DPMU_A_2)
