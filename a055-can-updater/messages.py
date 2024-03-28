
class SetHeartbeat:
    def _init_(self, node, rate=2000):
        self.rate = rate
        self.node = node

    def setRate(self, rate):
        self.rate = rate

    def updateRate(node):
        # tested, verifyed
        # node.sdo.download(0x1017, 0, bytes.fromhex('00 00'))
        # node.sdo['Producer Heartbeat Time'].raw = self.rate

    # def updateRate(rate):
        # tested, verifyed
        # node.sdo.download(0x1017, 0, bytes.fromhex('00 00'))
        node.sdo['Producer Heartbeat Time'].raw = 2000

class PrintDeviceType:
    def PrintDeviceType(node):
        # device_type = node.sdo.upload(0x1000, 0)
        # tested, verifyed
        # device_type = node.sdo[0x1000].raw
        device_type = node.sdo['Device Type']
        print("The device type is 0x" + format(device_type.raw, 'X'))

class PrintManufacturerDeviceName:
    def PrintManufacturerDeviceName(node):
        # tested, verifyed
        device_name = node.sdo['Manufacturer device name']
        print("device_name " + format(device_name.raw))

class PrintVendorId:
    def PrintVendorId(node):
        # not working
        # vendor_id = node.sdo.upload(0x1018, 1).raw
        # vendor_id = node.sdo.upload('Identity Object', 1).raw
        # tested, verifyed
        vendor_id = node.sdo['Identity Object']['Vendor Id']
        # vendor_id = node.sdo[0x1018][1].raw
        # vendor_id = node.sdo['Identity Object']
        print("vendor_id 0x" + format(vendor_id.raw))

class PrintProductCode:
    def PrintProductCode(node):
        # tested, verifyed
        # device_name = node.sdo['Identity Object']['Vendor Id'].raw
        # device_name = node.sdo[0x1018][1].raw
        # print("device_name", device_name)
        Product_Code = node.sdo['Identity Object']['Product Code']
        print("Product Code 0x" + format(Product_Code.raw))

class PrintRevisionNumber:
    def PrintRevisionNumber(node):
        # Revision_Number = node.sdo['Identity Object']['Revision Number'].raw
        Revision_Number = node.sdo['Identity Object'][3]
        print("Revision_Number 0x" + format(Revision_Number.raw, 'X'))

class PrintSerialNumber:
    def PrintSerialNumber(node):
        # Serial_Number = node.sdo['Identity Object']['Serial Number'].raw
        Serial_Number = node.sdo['Identity Object'][4]
        print("Serial_Number 0x" + format(Serial_Number.raw, 'X'))

class Program:
    def StopProgram(node1, node2):
        print("Waiting for NMT Boot")
        try:
            node1.sdo.download(0x1F51, 1, bytes.fromhex('00'))
            node2.nmt.wait_for_bootup(5)
            print("NMT Boot received")
        except Exception as err:#canopen.SdoCommunicationError:
            print("No SDO reasponse expected")
            print(f"Unexpected {err=}, {type(err)=}\r\n")

    def StartProgram(node1, node2):
        print("Waiting for NMT Boot")
        try:
            node1.sdo.download(0x1F51, 1, bytes.fromhex('01'))
            node2.nmt.wait_for_bootup(5)
            print("NMT Boot received")
        except Exception as err:#canopen.SdoCommunicationError:
            print("No SDO reasponse expected")
            print(f"Unexpected {err=}, {type(err)=}\r\n")


