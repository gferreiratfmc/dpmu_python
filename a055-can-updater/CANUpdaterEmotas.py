import sys
import os
import canopen
import time
import logging
from messages import *
from dataclasses import dataclass
from CalcCRC import CalcCRC

@dataclass
class FirmWare:
    domain: int
    filename: bytearray

    def __init__(self, domain=1, filename='1hz/dpmu_cpu1.crc'):
        self.domain = domain
        self.filename = filename


def download_firmware(firmware_file):
    print("Erase Program")
    # node.sdo.download(0x1F51, 1, 3)
    nodebl.sdo.download(0x1F51, fw.domain, bytes.fromhex('03'))
    #0x67E:8: 0x2F 0x51 0x1F 0x01 0x03 0x00 0x00 0x00

    time.sleep(0.250)

    print("Waiting for erase done")
    # Check, that the erase is ready – read from 0x1F57:1 Bit 0 – busy flag
    while True:
        busyFlag = nodebl.sdo.upload(0x1F57, fw.domain)
        print("busyFlag", format(busyFlag))
        # 0x67e:8: 0x40  0x57  0x1f  0x01  0x00  0x00  0x00  0x00
        # 0x5fe:8: 0x43  0x57  0x1f  0x01  0x02  0x00  0x00  0x00
        busyFlag = int.from_bytes(busyFlag, "little", signed=False)
        if not busyFlag & 1: # Check bit zero
            break;
        else:
            time.sleep(1)

    time.sleep(0.01)
    # Open the firmware file and read its content
    with open(firmware_file, 'rb') as file:
        firmware_data = file.read()

    # Get the size of the firmware data
    firmware_size = len(firmware_data)
    print("firmware_size 0x%08X" % firmware_size)

    # Divide the firmware into chunks to fit SDO segments
    chunk_size = 7  # Adjust based on your requirements
    chunks = [firmware_data[i:i + chunk_size] for i in range(0, firmware_size, chunk_size)]

    print("SDO Domain Transfer")
    nodebl.sdo.download(0x1F50, fw.domain, firmware_data, force_segment=True)

    time.sleep(2)

    # node.sdo.download(0x1F50, 0x01, chunks[0], force_segment=True)
    # Send the rest of the chunks
    # i = 0
    # for chunk in chunks[1:]:
        # print("%i %s", i, chunk)
        # if i > 10:
            # break
        # i += 1
        # nodebl.sdo.download(0x1F50, 0x01, chunk, force_segment=True)

    # Finish the firmware download
    # nodebl.sdo.download(0x1F50, 0x01, b'', end_download=True)

def InBootloader():
    nodebl.nmt.wait_for_heartbeat()
    PrintDeviceType.PrintDeviceType(nodebl)
    # PrintManufacturerDeviceNameBL.PrintManufacturerDeviceName()
    PrintVendorId.PrintVendorId(nodebl)
    PrintProductCode.PrintProductCode(nodebl)
    PrintRevisionNumber.PrintRevisionNumber(nodebl)
    PrintSerialNumber.PrintSerialNumber(nodebl)

    download_firmware(fw.filename)
    # download_firmware('1hz/dpmu_cpu1.crc')
    # download_firmware('C:/Users/hb/Documents/Project/CCS/workspace_v12/a055-dpmu-fw/dpmu_cpu1/CPU1_FLASH/dpmu_cpu1.crc')

    # CalcCRC.calcCRC('4hz/dpmu_cpu1.crc')

    # Check CRC by reading from 0x1F56:1
    print("Check CRC")
    # node.sdo.download(0x1F51, 1, 3)
    # Check by reading from 0x1F56:1
    # 1.0 .. error
    # 2.CRC Sum .. CRC sum is correct, transfer was OK
    # 3.Note: CRC sum can be used to identify the application.

    # Calculate checksum
    check_sum_calc = 0

    # Check, that the erase is ready – read from 0x1F57:1 Bit 0 – busy flag
    while True:
        busyFlag = nodebl.sdo.upload(0x1F57, fw.domain)
        print("busyFlag", format(busyFlag))
        # 0x67e:8: 0x40  0x57  0x1f  0x01  0x00  0x00  0x00  0x00
        # 0x5fe:8: 0x43  0x57  0x1f  0x01  0x02  0x00  0x00  0x00
        busyFlag = int.from_bytes(busyFlag, "little", signed=False)
        if not busyFlag & 1: # Check bit zero
            break;
        else:
            time.sleep(0.1)

    # Read checksum
    check_sum_read = nodebl.sdo.upload(0x1f56, fw.domain)
    check_sum_read = int.from_bytes(check_sum_read, "little", signed=False)
    print("Checksum 0x%04X" % check_sum_read)

    # Compare checksums
    if check_sum_read == check_sum_calc:
        print("FW UPDATE - SUCCESS")
    else:
        print("FW UPDATE - ERROR")

    Program.StartProgram(nodebl, node)

    sys.exit()

    time.sleep(5)

    print("Reading DeviceType")
    try:
        PrintDeviceType.PrintDeviceType(nodebl)
    except Exception as err:#canopen.SdoCommunicationError:
        print("No SDO reasponse expected")
        print(f"Unexpected {err=}, {type(err)=}\r\n")

    print("Waiting for Heartbeat")
    try:
        nodebl.nmt.wait_for_heartbeat(5)
    except:
        print("No Heartbeat received")

    time.sleep(1)

    # program start
    print("Waiting for NMT Boot")
    try:
        nodebl.sdo.download(0x1F51, 1, bytes.fromhex('01'))
        node.nmt.wait_for_bootup(5)
        print("NMT Boot received")
    except Exception as err:#canopen.SdoCommunicationError:
        print("No SDO reasponse expected")
        print(f"Unexpected {err=}, {type(err)=}\r\n")

    time.sleep(5)

    try:
        PrintDeviceType.PrintDeviceType(node)
    except Exception as err:#canopen.SdoCommunicationError:
        print("No SDO reasponse expected")
        print(f"Unexpected {err=}, {type(err)=}\r\n")

    ### UPDATE END ###

    network.sync.stop()
    network.disconnect()



# Save the arguments passed from command line
arg_list = sys.argv[1:]
arg_len  = len(arg_list)
print(arg_list)
print("len 0x%X" % arg_len)
fw = FirmWare()

if arg_len == 2:
    # Domain = 1 -> CPU1
    # Domain = 2 -> CPU2
    domain = int(arg_list[0])

    # Name of the file with the new FW
    filename = arg_list[1]
    fw.domain = domain
    fw.filename = filename
else:
    print("Usage: .\CANUpdaterEmotas_BAD.py <domain> <filename>")
    print("       <domain> [1..2], 1 = CPU1, 2 = CPU2")
    print("       <filename> name of the file with the new FW, full/relative path")

print(fw.domain)
print(fw.filename)
# sys.exit()

# For extra debug log printing
# logging.basicConfig(level=logging.DEBUG)

# Start with creating a network representing one CAN bus
network = canopen.Network()


# try:
# Connect to the CAN bus
# Arguments are passed to python-can's can.Bus() constructor
# (see https://python-can.readthedocs.io/en/latest/bus.html).
# network.connect()
# network.connect(bustype='socketcan', channel='can0')
network.connect(bustype='kvaser', channel=0, bitrate=125000)
# network.connect(bustype='pcan', channel='PCAN_USBBUS1', bitrate=250000)
# network.connect(bustype='ixxat', channel=0, bitrate=250000)
# network.connect(bustype='vector', app_name='CANalyzer', channel=0, bitrate=250000)
# network.connect(bustype='nican', channel='CAN0', bitrate=250000)

# Check network for serious problems
network.check()

# This will attempt to read an SDO from nodes 1 - 127
network.scanner.search()
node_id = 126
# We may need to wait a short while here to allow all nodes to respond
time.sleep(3)
#for node_id in network.scanner.nodes:
if node_id  in network.scanner.nodes:
    print("Found node %d!" % node_id)
else:
    node_id = 125
# I need this for my GUI interface to finnish printing all messages on the bus
# time.sleep(3)

# Add some nodes with corresponding Object Dictionaries

# node for device running in application mode
# address CAN ID 0x125
node = canopen.RemoteNode(node_id, './DPMU_001.eds')
node.sdo.RESPONSE_TIMEOUT = 2
node.PAUSE_BEFORE_SEND  = 0.01
# node.MAX_RETRIES = 2
# node.sdo.MAX_RETRIES = 2
network.add_node(node)

# node for device running in bootloader mode
# address CAN ID 0x7E
nodebl = canopen.RemoteNode(0x7e, './DPMU_001.eds')
nodebl.RESPONSE_TIMEOUT = 2
nodebl.PAUSE_BEFORE_SEND  = 0.01
network.add_node(nodebl)

# sys.exit()
# node.nmt.wait_for_heartbeat()

# node.add_sdo(0x600 + node_id, 0x580 + node_id)
# node_id = 1
# client = canopen.sdo.SdoClient(0x600 + node_id, 0x580 + node_id, './DPMU_001.eds')
# client.RESPONSE_TIMEOUT = 1;
if node_id == 0x7e:
    print("In Bootloader")
    InBootloader()
    sys.exit()

#node.nmt.wait_for_heartbeat()

# Set the rate of the heartbeats
#SetHeartbeat.updateRate(node)

# Read device information
try:
    PrintDeviceType.PrintDeviceType(node)
    PrintManufacturerDeviceName.PrintManufacturerDeviceName(node)
    PrintVendorId.PrintVendorId(node)
    PrintProductCode.PrintProductCode(node)
    PrintRevisionNumber.PrintRevisionNumber(node)
    PrintSerialNumber.PrintSerialNumber(node)
except:
    print('No answer from dpmu1')

# time.sleep(0.3)

### UPDATE START ###
print("UPDATE START")

print("Stop Program")
Program.StopProgram(node, nodebl)

InBootloader()
