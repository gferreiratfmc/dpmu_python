import sys, os, datetime, math
from os import path
from tkinter.constants import DISABLED
from test.test_typechecks import SubInt
from enum import Enum


# update mypath - 'canlib32.dll' must recide here
my_path = 'C:\Program Files\Kvaser\Drivers'
bundle_dir = getattr(sys, '_MEIPASS', path.abspath(path.dirname(__file__)))
path_to_dat = path.abspath(path.join(bundle_dir, my_path))
os.environ['KVDLLPATH'] = path_to_dat
print(os.environ['KVDLLPATH'])

import time as timer
import threading
import tkinter
import tkinter.messagebox
import customtkinter

from canlib import canlib, Frame
from canlib.canlib import ChannelData
from gen_indices import OD
#from canopen omport *

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class DPMUState(Enum):
    Idle = 0
    Initialize = 1
    SoftstartInitDefault = 2
    SoftstartInitRedundant = 201
    Softstart = 3
    TrickleChargeInit = 4
    TrickleChargeDelay = 5
    TrickleCharge = 6
    ChargeInit = 7
    Charge = 8
    ChargeStop = 9
    ChargeConstantVoltageInit = 10
    ChargeConstantVoltage = 11
    RegulateInit = 12
    Regulate = 13
    RegulateStop = 14
    RegulateVoltageInit = 140
    RegulateVoltage = 141
    Fault = 15
    FaultDelay = 16
    Keep = 17
    BalancingInit = 18
    Balancing = 19
    CC_Charge = 20
    StopEPWMs = 21
    ChargeRamp = 22

class canOD:
    sdoBlock=0
    sdoBlockTransferOngoing=0
    ackSeq=0
    
    numberOfBlocks=0
    
    id: int

    # class data:
    ccs: int
    indexHigh: int
    indexLow: int
    subIndex: int
    data_byte4: int
    data_byte5: int
    data_byte6: int
    data_byte7: int
#data Frame(id=1537, data=bytearray(b'/\x00@\x02\x00efg'), dlc=8, flags=<MessageFlag.STD: 2>, timestamp=None)
    # def __str__(self) -> str:
        # return "b'/\x'" + f'{selfdata.ccs:x}' + ", indexHigh=" + hex(self.data.indexHigh) + ", indexLow=" + hex(self.data.indexLow) + ", subIndex=" + hex(self.data.subIndex) + ", state=" + hex(self.data.state) + ""

    def __init__(self, id, ccs, indexHigh, indexLow, subIndex, data_byte4=0, data_byte5=0, data_byte6=0, data_byte7=0):
        self.id = id
        self.ccs = ccs
        self.indexHigh = indexHigh
        self.indexLow = indexLow
        self.subIndex = subIndex
        self.data_byte4 = data_byte4
        self.data_byte5 = data_byte5
        self.data_byte6 = data_byte6
        self.data_byte7 = data_byte7

    def setID(self, nodeid):
        self.id = 0x600 + nodeid

    def setSubIndex(self, subIndex):
        self.subIndex = subIndex

    def set_data_byte1(self, data_byte1):
        self.indexLow = data_byte1

    def set_data_byte2(self, data_byte2):
        self.indexHigh = data_byte2

    def set_data_byte3(self, data_byte3):
        self.subIndex = data_byte3

    def set_data_byte4(self, data_byte4):
        self.data_byte4 = data_byte4

    def set_data_byte5(self, data_byte5):
        self.data_byte5 = data_byte5

    def set_data_byte6(self, data_byte6):
        self.data_byte6 = data_byte6

    def set_data_byte7(self, data_byte7):
        self.data_byte7 = data_byte7

    def sendCanMessage(self):
        frame = Frame(id_=self.id, data=[self.ccs,
                                         self.indexLow,
                                         self.indexHigh,
                                         self.subIndex,
                                         self.data_byte4, self.data_byte5, self.data_byte6, self.data_byte7],
                                         flags=canlib.MessageFlag.STD)
        canopen_DPMU_A.write(frame)

        index = ((self.indexHigh<<8) + self.indexLow)
        if(  (self.ccs == 0x2f) and ( ( index == OD.I_ENERGY_BANK_SUMMARY ) or ( index == OD.I_DC_BUS_VOLTAGE ) or ( index == OD.I_DPMU_STATE ) ) ):
            print("OD ccs {:02x}".format(self.ccs) +
                  " index {:04x}".format((self.indexHigh<<8) + self.indexLow) +
                  " subindex {:02x}".format(self.subIndex) +
                  " data: {:02x}".format(self.data_byte4) +
                  " {:02x}".format(self.data_byte5) +
                  " {:02x}".format(self.data_byte6) +
                  " {:02x}".format(self.data_byte7))

    def createDPMULogFile(self, typeOfLog):
        fileCreated = False
        while (fileCreated == False):
            currentTimeStamp = timer.time()
            dateTimeStr =  datetime.datetime.fromtimestamp(currentTimeStamp).strftime("%Y%m%d_%H%M%S")               
            if( typeOfLog == OD.I_DEBUG_LOG):
                self.dpmuDebugFileName = "c:\\DPMU_LOG\\DPMU_LOG_" + dateTimeStr + ".hex"
            else:
                self.dpmuDebugFileName = "c:\\DPMU_LOG\\DPMU_CAN_LOG_" + dateTimeStr + ".hex"
                
            try:
                self.dpmuDebugFile = open(self.dpmuDebugFileName, "wb")  
                fileCreated = True
                self.numberOfBlocks = 0
            except FileExistsError as error:
                fileCreated = False
                time.sleep(1)
                print("File already exists. " + error)
                
    def writeDataToLogFile(self, data):
        # for i in data:
        #     print("Data[%04x]" % i )
        buffer = bytearray(0)
        buffer.append( data[1])
        buffer.append( data[2])
        buffer.append( data[3])
        buffer.append( data[4])
        buffer.append( data[5])
        buffer.append( data[6])
        buffer.append( data[7])
        
        self.dpmuDebugFile.write(buffer)   
        self.numberOfBlocks = self.numberOfBlocks + 1
        
    def closeDPMULogFile(self):
        self.dpmuDebugFile.flush()
        self.dpmuDebugFile.close()
        print("Number of blocks read:" + str( self.numberOfBlocks) )
        print("DPMU Log file created:" + self.dpmuDebugFileName)
# switch_inrush = canOD()
# switch_inrush.id = 0x601
# switch_inrush.ccs = 0x2F # Download, n = 3 bumber of bytes without data ((Bytes 4..7), e = 1 expediated transfer, s = 1 Byte in 'n'
# switch_inrush.indexHigh = 0x40
# switch_inrush.indexLow = 0x00
# #Switch_State.subIndex = 0x01 # SW_Qsb_State     - GLOAD_3 - J7.16
# #Switch_State.subIndex = 0x02 # SW_Qlb_State     - GLOAD_2 - J9.5
# switch_inrush.subIndex = 0x03 # SW_Qinb_State    - GLOAD_4 - J7.18
# #Switch_State.subIndex = 0x04 # SW_Qinrush_State - GLOAD_1 - J9.3

# global switch_input_state
# switch_input_state = False
# global switch_load_state
# switch_load_state = False
# global switch_share_state
# switch_share_state = False
# global switches_inrush_state
# switches_inrush_state = False
global nmtNodeId
nmtNodeId = 125

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

class App(customtkinter.CTk):
    cellVoltage = {}
    
    dpmuCurrentState = 0
    stateReadUpdateTime = 1000
    
    switch_input_state = False
    switch_load_state = False
    switch_share_state = False
    switches_inrush_state = False

    def __init__(self):
        super().__init__()

        # configure window
        self.title("CustomTkinter complex_example.py")
        self.geometry(f"{1920}x{980}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure((0, 2, 3, 4), weight=0)
        self.grid_rowconfigure((0, 1), weight=0)
        # self.grid_rowconfigure((2), weight=0)


        # create state frame with widgets
        rownr = 0
        self.state_frame = customtkinter.CTkFrame(self, width=140, corner_radius=10)
        self.state_frame.grid(row=rownr, column=0, rowspan=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.state_frame.grid_rowconfigure(5, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.state_frame, text="DPMU STATE", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=rownr, column=0, padx=20, pady=(20, 10))
        rownr += 1
        self.state_off_button = customtkinter.CTkButton(self.state_frame, command=self.state_off_event, text = "FAULT")
        self.state_off_button.grid(row=rownr, column=0, padx=20, pady=10)
        rownr += 1
        self.state_idle_button = customtkinter.CTkButton(self.state_frame, command=self.state_idle_event, text = "IDLE")
        self.state_idle_button.grid(row=rownr, column=0, padx=20, pady=10)
        rownr += 1
        self.state_initialize_button = customtkinter.CTkButton(self.state_frame, command=self.state_initialize_event, text = "INITIALIZE")
        self.state_initialize_button.grid(row=rownr, column=0, padx=20, pady=10)
        rownr += 1
        self.state_charge_button = customtkinter.CTkButton(self.state_frame, command=self.state_charge_event, text = "CHARGE")
        self.state_charge_button.grid(row=rownr, column=0, padx=20, pady=10)
        rownr += 1
        self.state_regulate_button = customtkinter.CTkButton(self.state_frame, command=self.state_regulate_event, text = "REGULATE")
        self.state_regulate_button.grid(row=rownr, column=0, padx=20, pady=10)
        rownr += 1
        self.state_read_button = customtkinter.CTkButton(self.state_frame, command=self.state_read_state_event, text = "READ STATE")
        self.state_read_button.grid(row=rownr, column=0, padx=20, pady=10)
        self.state_read_button.after(500, self.state_read_state_event)
        rownr += 1
        self.state_reboot_button = customtkinter.CTkButton(self.state_frame, command=self.state_reboot_event, text = "REBOOT")
        self.state_reboot_button.grid(row=rownr, column=0, padx=20, pady=10)


        ### create nmt frame
        rownr += 1
        self.logo_label = customtkinter.CTkLabel(self.state_frame, text="NMT", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=rownr, column=0, padx=20, pady=(20, 0))
        rownr += 1
        self.nmt_reset_application_button = customtkinter.CTkButton(self.state_frame, command=self.nmt_reset_application_event, text = "RESET APPLICATION")
        self.nmt_reset_application_button.grid(row=rownr, column=0, padx=20, pady=10)
        rownr += 1
        self.nmt_reset_communication_button = customtkinter.CTkButton(self.state_frame, command=self.nmt_reset_communication_event, text = "RESET COMMUNICATION")
        self.nmt_reset_communication_button.grid(row=rownr, column=0, padx=20, pady=10)
        rownr += 1
        self.nmt_pre_operational_button = customtkinter.CTkButton(self.state_frame, command=self.nmt_pre_operational_event, text = "PRE OPERATIONAL")
        self.nmt_pre_operational_button.grid(row=rownr, column=0, padx=20, pady=10)
        rownr += 1
        self.nmt_operational_button = customtkinter.CTkButton(self.state_frame, command=self.nmt_operational_event, text = "OPERATIONAL")
        self.nmt_operational_button.grid(row=rownr, column=0, padx=20, pady=10)
        rownr += 1
        self.nmt_stop_button = customtkinter.CTkButton(self.state_frame, command=self.nmt_stop_event, text = "STOP")
        self.nmt_stop_button.grid(row=rownr, column=0, padx=20, pady=10)


        # create main entry and button
        # self.entry = customtkinter.CTkEntry(self, placeholder_text="CTkEntry")
        # self.entry.grid(row=2, column=1, columnspan=2, padx=(20, 0), pady=(20, 20), sticky="sew")

        # self.main_button_1 = customtkinter.CTkButton(master=self, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        # self.main_button_1.grid(row=2, column=3, padx=(20, 20), pady=(20, 20), sticky="sew")


        #create new frame
        # self.log_frame = customtkinter.CTkFrame(self, width=140, corner_radius=10)
        # self.log_frame.grid(row=rownr, column=1, rowspan=3, padx=(20, 0), pady=(20, 0), sticky="nsew")
        # create textbox
        self.textbox = customtkinter.CTkTextbox(self, width=260)
        #self.textbox.configure(state="disabled", text_color="black") # read only
        self.textbox.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")


        # create dc bus frame
        rownr = 0
        self.voltages_frame = customtkinter.CTkFrame(self, width=140, corner_radius=10)
        self.voltages_frame.grid(row=rownr, column=2, rowspan=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.voltages_frame_label = customtkinter.CTkLabel(self.voltages_frame, text="DC BUS", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.voltages_frame_label.grid(row=rownr, column=0, columnspan=3, padx=20, pady=(20, 10))

        rownr += 1
        self.voltages_max_allowed_dc_bus_voltage_entry = customtkinter.CTkEntry(self.voltages_frame, width=50, justify="right", placeholder_text=193)
        self.voltages_max_allowed_dc_bus_voltage_entry.grid(row=rownr, column=0, padx=(20, 0), pady=(5), sticky="nsew")
        self.voltages_max_allowed_dc_bus_voltage_label = customtkinter.CTkLabel(self.voltages_frame, text="V")
        self.voltages_max_allowed_dc_bus_voltage_label.grid(row=rownr, column=1, padx=(5), sticky="nsew")
        self.voltages_max_allowed_dc_bus_voltage_button = customtkinter.CTkButton(self.voltages_frame, command=self.voltages_max_allowed_dc_bus_voltage_event, text = "MAX VOLTAGE")
        self.voltages_max_allowed_dc_bus_voltage_button.grid(row=rownr, column=2, padx=(20,0), pady=5)
        self.voltages_max_allowed_dc_bus_voltage_button = customtkinter.CTkButton(self.voltages_frame, command=self.voltages_max_allowed_dc_bus_voltage_read_event, width=20, text = "R")
        self.voltages_max_allowed_dc_bus_voltage_button.grid(row=rownr, column=3, padx=(0,20), pady=5, sticky="w")
        self.voltages_max_allowed_dc_bus_voltage_entry.insert(0,"193")

        rownr += 1
        self.voltages_target_voltage_entry = customtkinter.CTkEntry(self.voltages_frame, width=50, justify="right", placeholder_text="180 V")
        self.voltages_target_voltage_entry.grid(row=rownr, column=0, padx=(20, 0), pady=(5), sticky="nsew")
        self.voltages_target_voltage_label = customtkinter.CTkLabel(self.voltages_frame, text="V")
        self.voltages_target_voltage_label.grid(row=rownr, column=1, padx=(5), sticky="nsew")
        self.voltages_target_voltage_button = customtkinter.CTkButton(self.voltages_frame, command=self.voltages_target_voltage_event, text = "TARGET")
        self.voltages_target_voltage_button.grid(row=rownr, column=2, padx=(20,0), pady=5)
        self.voltages_target_voltage_button = customtkinter.CTkButton(self.voltages_frame, command=self.voltages_target_voltage_read_event, width=20, text = "R")
        self.voltages_target_voltage_button.grid(row=rownr, column=3, padx=(0,20), pady=5, sticky="w")
        self.voltages_target_voltage_entry.insert(0,"180")

        rownr += 1
        self.voltages_min_allowed_dc_bus_voltage_entry = customtkinter.CTkEntry(self.voltages_frame, width=50, justify="right", placeholder_text="167 V")
        self.voltages_min_allowed_dc_bus_voltage_entry.grid(row=rownr, column=0, padx=(20, 0), pady=(5), sticky="nsew")
        self.voltages_min_allowed_dc_bus_voltage_label = customtkinter.CTkLabel(self.voltages_frame, text="V")
        self.voltages_min_allowed_dc_bus_voltage_label.grid(row=rownr, column=1, padx=(5), sticky="nsew")
        self.voltages_min_allowed_dc_bus_voltage_button = customtkinter.CTkButton(self.voltages_frame, command=self.voltages_min_allowed_dc_bus_voltage_event, text = "MIN VOLTAGE")
        self.voltages_min_allowed_dc_bus_voltage_button.grid(row=rownr, column=2, padx=(20,0), pady=5)
        self.voltages_min_allowed_dc_bus_voltage_button = customtkinter.CTkButton(self.voltages_frame, command=self.voltages_min_allowed_dc_bus_voltage_read_event, width=20, text = "R")
        self.voltages_min_allowed_dc_bus_voltage_button.grid(row=rownr, column=3, padx=(0,20), pady=5, sticky="w")
        self.voltages_min_allowed_dc_bus_voltage_entry.insert(0,"167")

        rownr += 1
        self.voltages_dc_bus_short_circuit_limit_entry = customtkinter.CTkEntry(self.voltages_frame, width=50, justify="right", placeholder_text="60 V")
        self.voltages_dc_bus_short_circuit_limit_entry.grid(row=rownr, column=0, padx=(20, 0), pady=(5), sticky="nsew")
        self.voltages_dc_bus_short_circuit_limit_label = customtkinter.CTkLabel(self.voltages_frame, text="V")
        self.voltages_dc_bus_short_circuit_limit_label.grid(row=rownr, column=1, padx=(5), sticky="nsew")
        self.voltages_dc_bus_short_circuit_voltage_button = customtkinter.CTkButton(self.voltages_frame, command=self.voltages_short_circuit_voltage_event, text = "SHORT CIRCUIT")
        self.voltages_dc_bus_short_circuit_voltage_button.grid(row=rownr, column=2, padx=(20,0), pady=5)
        self.voltages_dc_bus_short_circuit_voltage_button = customtkinter.CTkButton(self.voltages_frame, command=self.voltages_short_circuit_voltage_read_event, width=20, text = "R")
        self.voltages_dc_bus_short_circuit_voltage_button.grid(row=rownr, column=3, padx=(0,20), pady=5, sticky="w")
        self.voltages_dc_bus_short_circuit_limit_entry.insert(0,"30")

        rownr += 1
        self.energy_bank_safey_threshold_entry = customtkinter.CTkEntry(self.voltages_frame, width=50, justify="right", placeholder_text="45 V")
        self.energy_bank_safey_threshold_entry.grid(row=rownr, column=0, padx=(20, 0), pady=(5), sticky="nsew")
        self.energy_bank_safey_threshold_label = customtkinter.CTkLabel(self.voltages_frame, text="V")
        self.energy_bank_safey_threshold_label.grid(row=rownr, column=1, padx=(5), sticky="nsew")
        self.energy_bank_safey_threshold_button = customtkinter.CTkButton(self.voltages_frame, command=self.bank_safey_threshold_event, text = "SAFETY THRESHOLD")
        self.energy_bank_safey_threshold_button.grid(row=rownr, column=2, padx=(20,0), pady=5)
        self.energy_bank_safey_threshold_button = customtkinter.CTkButton(self.voltages_frame, command=self.bank_safey_threshold_read_event, width=20, text = "R")
        self.energy_bank_safey_threshold_button.grid(row=rownr, column=3, padx=(0,20), pady=5, sticky="w")
        self.energy_bank_safey_threshold_entry.insert(0,"30")

        rownr += 1
        self.power_pudget_dc_input_available_power_budget_input_event_entry = customtkinter.CTkEntry(self.voltages_frame, width=50, justify="right", placeholder_text="360")
        self.power_pudget_dc_input_available_power_budget_input_event_entry.grid(row=rownr, column=0, padx=(20, 0), pady=(5), sticky="nsew")
        self.power_pudget_dc_input_available_power_budget_input_event_label = customtkinter.CTkLabel(self.voltages_frame, text="W")
        self.power_pudget_dc_input_available_power_budget_input_event_label.grid(row=rownr, column=1, padx=(5), sticky="nsew")
        self.power_pudget_dc_input_available_power_budget_input_event_button = customtkinter.CTkButton(self.voltages_frame, command=self.current_available_power_budget_input_event, text = "AVAILABLE PWR BUDGET")
        self.power_pudget_dc_input_available_power_budget_input_event_button.grid(row=rownr, column=2, padx=(20,0), pady=5)
        self.power_pudget_dc_input_available_power_budget_input_event_button = customtkinter.CTkButton(self.voltages_frame, command=self.current_available_power_budget_input_read_event, width=20, text = "R")
        self.power_pudget_dc_input_available_power_budget_input_event_button.grid(row=rownr, column=3, padx=(0,20), pady=5, sticky="w")
        self.power_pudget_dc_input_available_power_budget_input_event_entry.insert(0,"360")

        # rownr += 1
        # self.power_pudget_dc_input_line_A_entry = customtkinter.CTkEntry(self.voltages_frame, width=50, justify="right", placeholder_text="10 A")
        # self.power_pudget_dc_input_line_A_entry.grid(row=rownr, column=0, padx=(20, 0), pady=(5), sticky="nsew")
        # self.power_pudget_dc_input_line_A_label = customtkinter.CTkLabel(self.voltages_frame, text="A")
        # self.power_pudget_dc_input_line_A_label.grid(row=rownr, column=1, padx=(5), sticky="nsew")
        # self.power_pudget_dc_input_line_A_button = customtkinter.CTkButton(self.voltages_frame, command=self.power_pudget_dc_input_line_A_event, text = "MAX INPUT CURR A")
        # self.power_pudget_dc_input_line_A_button.grid(row=rownr, column=2, padx=(20,0), pady=5)
        # self.power_pudget_dc_input_line_A_button = customtkinter.CTkButton(self.voltages_frame, command=self.power_pudget_dc_input_line_A_read_event, width=20, text = "R")
        # self.power_pudget_dc_input_line_A_button.grid(row=rownr, column=3, padx=(0,20), pady=5, sticky="w")
        # self.power_pudget_dc_input_line_A_entry.insert(0,"10")

        # rownr += 1
        # self.power_pudget_dc_input_line_B_entry = customtkinter.CTkEntry(self.voltages_frame, width=50, justify="right", placeholder_text="10 A")
        # self.power_pudget_dc_input_line_B_entry.grid(row=rownr, column=0, padx=(20, 0), pady=(5), sticky="nsew")
        # self.power_pudget_dc_input_line_B_label = customtkinter.CTkLabel(self.voltages_frame, text="A")
        # self.power_pudget_dc_input_line_B_label.grid(row=rownr, column=1, padx=(5), sticky="nsew")
        # self.power_pudget_dc_input_line_B_button = customtkinter.CTkButton(self.voltages_frame, command=self.power_pudget_dc_input_line_B_event, text = "MAX INPUT CURR B")
        # self.power_pudget_dc_input_line_B_button.grid(row=rownr, column=2, padx=(20,0), pady=5)
        # self.power_pudget_dc_input_line_B_button = customtkinter.CTkButton(self.voltages_frame, command=self.power_pudget_dc_input_line_B_read_event, width=20, text = "R")
        # self.power_pudget_dc_input_line_B_button.grid(row=rownr, column=3, padx=(0,20), pady=5, sticky="w")
        # self.power_pudget_dc_input_line_B_entry.insert(0,"10")

        rownr += 1
        self.current_max_load_current_entry = customtkinter.CTkEntry(self.voltages_frame, width=50, justify="right", placeholder_text="500")
        self.current_max_load_current_entry.grid(row=rownr, column=0, padx=(20, 0), pady=(5), sticky="nsew")
        self.current_max_load_current_label = customtkinter.CTkLabel(self.voltages_frame, text="W")
        self.current_max_load_current_label.grid(row=rownr, column=1, padx=(5), sticky="nsew")
        self.current_max_load_current_button = customtkinter.CTkButton(self.voltages_frame, command=self.current_max_load_current_event, text = "MAX LOAD PWR")
        self.current_max_load_current_button.grid(row=rownr, column=2, padx=(20,0), pady=5)
        self.current_max_load_current_button = customtkinter.CTkButton(self.voltages_frame, command=self.current_max_load_current_read_event, width=20, text = "R")
        self.current_max_load_current_button.grid(row=rownr, column=3, padx=(0,20), pady=5, sticky="w")
        self.current_max_load_current_entry.insert(0,"180")

        rownr += 1
        self.current_max_ess_current_entry = customtkinter.CTkEntry(self.voltages_frame, width=50, justify="right", placeholder_text="0 A")
        self.current_max_ess_current_entry.grid(row=rownr, column=0, padx=(20, 0), pady=(5), sticky="nsew")
        self.current_max_ess_current_label = customtkinter.CTkLabel(self.voltages_frame, text="A")
        self.current_max_ess_current_label.grid(row=rownr, column=1, padx=(5), sticky="nsew")
        self.current_max_ess_current_button = customtkinter.CTkButton(self.voltages_frame, command=self.current_max_ess_current_event, text = "ESS CURRENT")
        self.current_max_ess_current_button.grid(row=rownr, column=2, padx=(20,0), pady=5)
        self.current_max_ess_current_button = customtkinter.CTkButton(self.voltages_frame, command=self.current_max_ess_current_read_event, width=20, text = "R")
        self.current_max_ess_current_button.grid(row=rownr, column=3, padx=(0,20), pady=5, sticky="w")
        self.current_max_ess_current_entry.insert(0,"2")

        rownr += 1
        self.VI_sub_frame = customtkinter.CTkFrame(self.voltages_frame)
        self.VI_sub_frame.grid(row=rownr, column=0, columnspan=3, padx=(10, 10), pady=10, sticky="")
        self.VI_sub_frame_label = customtkinter.CTkLabel(master=self.VI_sub_frame, text="VOLTAGES AND CURRENTS", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.VI_sub_frame_label.grid(row=rownr, column=0, columnspan=2, padx=10, pady=10, sticky="")

        rownr += 1
        self.read_power_dc_voltage_entry = customtkinter.CTkEntry(master=self.VI_sub_frame)
        self.read_power_dc_voltage_entry.grid(row=rownr, column=0, pady=(20, 0), padx=20, sticky="w")
        self.read_power_dc_voltage_label = customtkinter.CTkLabel(self.VI_sub_frame, text="DC BUS VOLTAGE")
        self.read_power_dc_voltage_label.grid(row=rownr, column=1, pady=(20, 0), padx=20, sticky="w")
        self.read_power_dc_voltage_button = customtkinter.CTkButton(self.VI_sub_frame, command=self.read_power_dc_voltage_event, width=20, text = "R")
        self.read_power_dc_voltage_button.grid(row=rownr, column=2, padx=(0,20), pady=5, sticky="w")

        rownr += 1
        self.read_power_dc_vstore_entry = customtkinter.CTkEntry(master=self.VI_sub_frame)
        self.read_power_dc_vstore_entry.grid(row=rownr, column=0, pady=(20, 0), padx=20, sticky="w")
        self.read_power_dc_vstore_label = customtkinter.CTkLabel(self.VI_sub_frame, text="SUPERCAP VOLTAGE")
        self.read_power_dc_vstore_label.grid(row=rownr, column=1, pady=(20, 0), padx=20, sticky="w")
        self.read_power_dc_vstore_button = customtkinter.CTkButton(self.VI_sub_frame, command=self.read_power_dc_vstore_event, width=20, text = "R")
        self.read_power_dc_vstore_button.grid(row=rownr, column=2, padx=(0,20), pady=5, sticky="w")

        rownr += 1
        self.read_power_input_current_entry = customtkinter.CTkEntry(master=self.VI_sub_frame)
        self.read_power_input_current_entry.grid(row=rownr, column=0, pady=(20, 0), padx=20, sticky="w")
        self.read_power_input_current_label = customtkinter.CTkLabel(self.VI_sub_frame, text="INPUT CURRENT")
        self.read_power_input_current_label.grid(row=rownr, column=1, pady=(20, 0), padx=20, sticky="w")
        self.read_power_input_current_button = customtkinter.CTkButton(self.VI_sub_frame, command=self.read_power_input_current_event, width=20, text = "R")
        self.read_power_input_current_button.grid(row=rownr, column=2, padx=(0,20), pady=5, sticky="w")

        rownr += 1
        self.read_power_load_current_entry = customtkinter.CTkEntry(master=self.VI_sub_frame)
        self.read_power_load_current_entry.grid(row=rownr, column=0, pady=(20, 0), padx=20, sticky="w")
        self.read_power_input_current_label = customtkinter.CTkLabel(self.VI_sub_frame, text="LOAD CURRENT")
        self.read_power_input_current_label.grid(row=rownr, column=1, pady=(20, 0), padx=20, sticky="w")
        self.read_power_load_current_button = customtkinter.CTkButton(self.VI_sub_frame, command=self.read_power_load_current_event, width=20, text = "R")
        self.read_power_load_current_button.grid(row=rownr, column=2, padx=(0,20), pady=5, sticky="w")
        
        rownr += 1
        self.read_power_supercap_current_entry = customtkinter.CTkEntry(master=self.VI_sub_frame)
        self.read_power_supercap_current_entry.grid(row=rownr, column=0, pady=(20, 0), padx=20, sticky="w")
        self.read_power_supercap_current_label = customtkinter.CTkLabel(self.VI_sub_frame, text="SUPERCAP CURRENT")
        self.read_power_supercap_current_label.grid(row=rownr, column=1, pady=(20, 0), padx=20, sticky="w")
        self.read_power_supercap_current_button = customtkinter.CTkButton(self.VI_sub_frame, command=self.read_power_supercap_current_event, width=20, text = "R")
        self.read_power_supercap_current_button.grid(row=rownr, column=2, padx=(0,20), pady=5, sticky="w")


        # create tabview
        self.tabview = customtkinter.CTkTabview(self, width=250, corner_radius=10)
        self.tabview.grid(row=1, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.tabview.add("Store Parameters")
        self.tabview.add("Restore Parameters")
        self.tabview.add("DPMU Type")
        self.tabview.tab("DPMU Type").grid_columnconfigure(0, weight=1)  # configure grid of individual tabs
        self.tabview.tab("Restore Parameters").grid_columnconfigure(0, weight=1)
        self.tabview.add("Node ID")

        self.optionmenu_1 = customtkinter.CTkOptionMenu(self.tabview.tab("DPMU Type"), dynamic_resizing=False,
                                                        values=["Value 1", "Restore Parameters", "Value Long Long Long"])
        self.optionmenu_1.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.combobox_DPMU_Type = customtkinter.CTkComboBox(self.tabview.tab("DPMU Type"), command=self.set_DPMU_Type_event, width=200,
                                                    values=["DFLT_CAP", "DFLT_CAP_W_RDNT", "DFLT_CAP_W_SUPP", "DFLT_CAP_W_RDNT_SUPP",
                                                            "DFLT_BAT", "DFLT_BAT_W_RDNT", "DFLT_BAT_W_SUPP", "DFLT_BAT_W_RDNT_SUPP",
                                                            "RDNT_CAP", "RDNT_CAP_W_SUPP", "RDNT_BAT", "RDNT_BAT_W_SUPP",
                                                            "SUPP_CAP", "SUPP_BAT"])
        self.combobox_DPMU_Type.grid(row=1, column=0, padx=(20,10), pady=(10, 10))
        self.combobox_DPMU_Type.set("DFLT_CAP")
        self.combobox_DPMU_Type_button = customtkinter.CTkButton(self.tabview.tab("DPMU Type"), command=self.read_DPMU_Type_event, width=20, text = "R")
        self.combobox_DPMU_Type_button.grid(row=1, column=1, padx=(20,20))
        self.string_input_button = customtkinter.CTkButton(self.tabview.tab("DPMU Type"), text="Open CTkInputDialog",
                                                           command=self.open_input_dialog_event)
        self.string_input_button.grid(row=2, column=0, padx=(10,20), pady=(10, 10))

        self.store_parameters_frame = customtkinter.CTkFrame(self.tabview.tab("Store Parameters"), width=140, corner_radius=10)
        self.store_parameters_frame.grid(row=0, column=0, padx=(20, 20), pady=(20, 0), sticky="nsew")
        rownr = 0
        colnr = 0
        self.store_all_params_button = customtkinter.CTkButton(self.store_parameters_frame, command=self.store_all_params_event, width=20, text = "ALL PARAMETERS")
        self.store_all_params_button.grid(row=rownr, column=colnr, padx=(10,10), pady=10, sticky="nsew")
        rownr += 1
        self.store_comm_params_button = customtkinter.CTkButton(self.store_parameters_frame, command=self.store_comm_params_event, width=20, text = "COMM PARAMETERS")
        self.store_comm_params_button.grid(row=rownr, column=colnr, padx=(10,10), pady=10, sticky="nsew")
        rownr = 0
        colnr += 1
        self.store_app_params_button = customtkinter.CTkButton(self.store_parameters_frame, command=self.store_app_params_event, width=20, text = "APP PARAMETERS")
        self.store_app_params_button.grid(row=rownr, column=colnr, padx=(10,10), pady=10, sticky="nsew")
        rownr += 1
        self.store_mf_aparams_button = customtkinter.CTkButton(self.store_parameters_frame, command=self.store_mf_params_event, width=20, text = "MF PARAMETERS")
        self.store_mf_aparams_button.grid(row=rownr, column=colnr, padx=(10,10), pady=(10,10), sticky="nsew")

        self.restore_parameters_frame = customtkinter.CTkFrame(self.tabview.tab("Restore Parameters"), width=140, corner_radius=10)
        self.restore_parameters_frame.grid(row=0, column=0, padx=(20, 20), pady=(20, 0), sticky="nsew")
        rownr = 0
        colnr = 1
        self.restore_all_params_button = customtkinter.CTkButton(self.restore_parameters_frame, command=self.restore_all_params_event, width=20, text = "ALL PARAMETERS")
        self.restore_all_params_button.grid(row=rownr, column=colnr, padx=(10,10), pady=10, sticky="nsew")
        rownr += 1
        self.restore_comm_params_button = customtkinter.CTkButton(self.restore_parameters_frame, command=self.restore_comm_params_event, width=20, text = "COMM PARAMETERS")
        self.restore_comm_params_button.grid(row=rownr, column=colnr, padx=(10,10), pady=10, sticky="nsew")
        rownr = 0
        colnr += 1
        self.restore_app_params_button = customtkinter.CTkButton(self.restore_parameters_frame, command=self.restore_app_params_event, width=20, text = "APP PARAMETERS")
        self.restore_app_params_button.grid(row=rownr, column=colnr, padx=(10,10), pady=10, sticky="nsew")
        rownr += 1
        self.restore_mf_aparams_button = customtkinter.CTkButton(self.restore_parameters_frame, command=self.restore_mf_params_event, width=20, text = "MF PARAMETERS")
        self.restore_mf_aparams_button.grid(row=rownr, column=colnr, padx=(10,10), pady=(10,10), sticky="nsew")

        self.nodeid_frame = customtkinter.CTkFrame(self.tabview.tab("Node ID"), width=140, corner_radius=10)
        self.nodeid_frame.grid(row=0, column=0, padx=(20, 20), pady=(20, 0), sticky="nsew")
        rownr = 0
        colnr = 0
        self.nodeid_label = customtkinter.CTkLabel(self.nodeid_frame, text="UPDATE NODE ID", anchor="w")
        self.nodeid_label.grid(row=rownr, column=1, padx=(5), sticky="nsew")
        rownr += 1
        self.nodeid_entry = customtkinter.CTkEntry(self.nodeid_frame, width=50, justify="right", placeholder_text="0")
        self.nodeid_entry.grid(row=rownr, column=0, padx=(10, 10), pady=(10), sticky="nsew")
        self.nodeid_entry.insert("0","125")
        colnr += 1
        self.nodeid_button = customtkinter.CTkButton(self.nodeid_frame, command=self.nodeid_event, width=20, text = "SET SERVER NODE ID")
        self.nodeid_button.grid(row=rownr, column=colnr, padx=(10,10), pady=10, sticky="nsew")
        rownr += 1
        self.nodeid_gui_button = customtkinter.CTkButton(self.nodeid_frame, command=self.nodeid_gui_event, width=20, text = "SET GUI SENDING NODE ID")
        self.nodeid_gui_button.grid(row=rownr, column=colnr, padx=(10,10), pady=10, sticky="nsew")


        # create row0-col0-master frame
        rownr = 0
        self.row0_col3_master_frame = customtkinter.CTkFrame(self, width=140, corner_radius=10)
        self.row0_col3_master_frame.grid(row=0, column=3, padx=(20, 20), pady=(20, 0), sticky="nsew")

        # create temperature frame
        rownr = 0
        self.temperature_frame = customtkinter.CTkFrame(self.row0_col3_master_frame, corner_radius=10)
        self.temperature_frame.grid(row=0, column=3, padx=0, pady=0, sticky="nw")
        self.label_temperature_frame = customtkinter.CTkLabel(master=self.temperature_frame, text="TEMPERATURE", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.label_temperature_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="")

        rownr += 1
        self.temperature_max_entry = customtkinter.CTkEntry(self.temperature_frame, width=50, justify="right", placeholder_text="0")
        self.temperature_max_entry.grid(row=rownr, column=0, padx=(20, 0), pady=(5), sticky="nsew")
        self.temperature_max_label = customtkinter.CTkLabel(self.temperature_frame, text="\u2103  MAX TEMP", anchor="w")
        self.temperature_max_label.grid(row=rownr, column=1, padx=(5), sticky="nsew")
        self.temperature_max_button = customtkinter.CTkButton(self.temperature_frame, command=self.temperature_max_allowed_event, width=20, text = "S")
        self.temperature_max_button.grid(row=rownr, column=2, padx=(0,20), pady=5, sticky="w")
        self.temperature_max_button = customtkinter.CTkButton(self.temperature_frame, command=self.temperature_max_allowed_read_event, width=20, text = "R")
        self.temperature_max_button.grid(row=rownr, column=3, padx=(0,20), pady=5, sticky="w")
        self.temperature_max_entry.insert(0,"85")

        rownr += 1
        self.temperature_high_entry = customtkinter.CTkEntry(self.temperature_frame, width=50, justify="right", placeholder_text="0")
        self.temperature_high_entry.grid(row=rownr, column=0, padx=(20, 0), pady=(5), sticky="nsew")
        self.temperature_high_label = customtkinter.CTkLabel(self.temperature_frame, text="\u2103  HIGH TEMP", anchor="w")
        self.temperature_high_label.grid(row=rownr, column=1, padx=(5), sticky="nsew")
        self.temperature_high_button = customtkinter.CTkButton(self.temperature_frame, command=self.temperature_high_limit_event, width=20, text = "S")
        self.temperature_high_button.grid(row=rownr, column=2, padx=(0,20), pady=5, sticky="w")
        self.temperature_high_button = customtkinter.CTkButton(self.temperature_frame, command=self.temperature_high_limit_read_event, width=20, text = "R")
        self.temperature_high_button.grid(row=rownr, column=3, padx=(0,20), pady=5, sticky="w")
        self.temperature_high_entry.insert(0,"70")

        rownr += 1
        self.temperature_energy_bank_entry = customtkinter.CTkEntry(self.temperature_frame, width=50, justify="right", placeholder_text="0")
        self.temperature_energy_bank_entry.grid(row=rownr, column=0, padx=(20, 0), pady=(5), sticky="nsew")
        self.temperature_energy_bank_label = customtkinter.CTkLabel(self.temperature_frame, text="\u2103  ENERGY BANK", anchor="w")
        self.temperature_energy_bank_label.grid(row=rownr, column=1, padx=(5), sticky="nsew")
        self.temperature_energy_bank_button = customtkinter.CTkButton(self.temperature_frame, command=self.temperature_energy_bank_read_event, width=20, text = "R")
        self.temperature_energy_bank_button.grid(row=rownr, column=3, padx=(0,20), pady=5, sticky="w")

        rownr += 1
        self.temperature_mezzanine_entry = customtkinter.CTkEntry(self.temperature_frame, width=50, justify="right", placeholder_text="0")
        self.temperature_mezzanine_entry.grid(row=rownr, column=0, padx=(20, 0), pady=(5), sticky="nsew")
        self.temperature_mezzanine_label = customtkinter.CTkLabel(self.temperature_frame, text="\u2103  MEZZANINE", anchor="w")
        self.temperature_mezzanine_label.grid(row=rownr, column=1, padx=(5), sticky="nsew")
        self.temperature_mezzanine_button = customtkinter.CTkButton(self.temperature_frame, command=self.temperature_mezzanine_read_event, width=20, text = "R")
        self.temperature_mezzanine_button.grid(row=rownr, column=3, padx=(0,20), pady=5, sticky="w")

        rownr += 1
        self.temperature_main_entry = customtkinter.CTkEntry(self.temperature_frame, width=50, justify="right", placeholder_text="0")
        self.temperature_main_entry.grid(row=rownr, column=0, padx=(20, 0), pady=(5), sticky="nsew")
        self.temperature_main_label = customtkinter.CTkLabel(self.temperature_frame, text="\u2103  MAIN", anchor="w")
        self.temperature_main_label.grid(row=rownr, column=1, padx=(5), sticky="nsew")
        self.temperature_main_button = customtkinter.CTkButton(self.temperature_frame, command=self.temperature_main_read_event, width=20, text = "R")
        self.temperature_main_button.grid(row=rownr, column=3, padx=(0,20), pady=5, sticky="w")

        rownr += 1
        self.temperature_dsp_base_entry = customtkinter.CTkEntry(self.temperature_frame, width=50, justify="right", placeholder_text="0")
        self.temperature_dsp_base_entry.grid(row=rownr, column=0, padx=(20, 0), pady=(5), sticky="nsew")
        self.temperature_dsp_base_label = customtkinter.CTkLabel(self.temperature_frame, text="\u2103  DSP BASE", anchor="w")
        self.temperature_dsp_base_label.grid(row=rownr, column=1, padx=(5), sticky="nsew")
        self.temperature_dsp_base_button = customtkinter.CTkButton(self.temperature_frame, command=self.temperature_dsp_card_read_event, width=20, text = "R")
        self.temperature_dsp_base_button.grid(row=rownr, column=3, padx=(0,20), pady=5, sticky="w")

        rownr += 1
        self.temperature_stack_entry = customtkinter.CTkEntry(self.temperature_frame, width=50, justify="right", placeholder_text="0")
        self.temperature_stack_entry.grid(row=rownr, column=0, padx=(20, 0), pady=(5), sticky="nsew")
        self.temperature_stack_label = customtkinter.CTkLabel(self.temperature_frame, text="\u2103  STACK", anchor="w")
        self.temperature_stack_label.grid(row=rownr, column=1, padx=(5), sticky="nsew")
        self.temperature_stack_button = customtkinter.CTkButton(self.temperature_frame, command=self.temperature_stack_read_event, width=20, text = "R")
        self.temperature_stack_button.grid(row=rownr, column=3, padx=(0,20), pady=5, sticky="w")


        # temperature sub frame
        rownr += 1
        self.temperature_sub_frame = customtkinter.CTkFrame(self.temperature_frame)
        self.temperature_sub_frame.grid(row=rownr, column=0, columnspan=2, padx=(20, 20), pady=(20, 20), sticky="nsew")
        self.radio_var = tkinter.IntVar(value=0)
        rownr += 1
        self.temperature_sub_button = customtkinter.CTkButton(self.temperature_sub_frame, command=self.temperature_highest_read_event, width=20, text = "READ TEMPERATURE")
        self.temperature_sub_button.grid(row=rownr, column=2, padx=(20,20), pady=(20,5), sticky="")
        rownr += 1
        self.temperature_sub_status = customtkinter.CTkLabel(self.temperature_sub_frame, width=70, text = "TEMP STATUS")
        self.temperature_sub_status.grid(row=rownr, column=2, padx=(20,20), pady=(5,20), sticky="")

        # create CAN/debug log frame
        self.debuglog_frame = customtkinter.CTkFrame(self, corner_radius=10)
        self.debuglog_frame.grid(row=1, column=3, padx=(20,20), pady=(20, 20), sticky="nsew")
        rownr = 0
        self.label_debuglog_frame = customtkinter.CTkLabel(master=self.debuglog_frame, text="DEBUG LOG", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.label_debuglog_frame.grid(row=rownr, column=0, padx=10, pady=10, sticky="")

        rownr += 1
        debuglog_checkbox_state_var = customtkinter.StringVar(value="on")
        self.debuglog_checkbox_state = customtkinter.CTkCheckBox(master=self.debuglog_frame, command=self.debuglog_state_event, variable=debuglog_checkbox_state_var, onvalue="on", offvalue="off")
        self.debuglog_checkbox_state.grid(row=rownr, column=0, pady=(20, 0), padx=20, sticky="")
        self.debuglog_checkbox_state.configure(state="normal",text="STATE", fg_color="green")
        self.debuglog_read_state_button = customtkinter.CTkButton(self.debuglog_frame, command=self.debuglog_read_state_event, width=20, text = "READ STATE")
        self.debuglog_read_state_button.grid(row=rownr, column=1, padx=(0,20), pady=5, sticky="")
        rownr += 1
        self.debuglog_read_button = customtkinter.CTkButton(self.debuglog_frame, command=self.debuglog_read_event, width=20, text = "READ DBG LOG")
        self.debuglog_read_button.grid(row=rownr, column=0, padx=(0,20), pady=5, sticky="")
        self.debuglog_reset_button = customtkinter.CTkButton(self.debuglog_frame, command=self.debuglog_reset_event, width=20, text = "RESET DBG LOG")
        self.debuglog_reset_button.grid(row=rownr, column=1, padx=(0,20), pady=5, sticky="")

        rownr += 1
        self.label_debuglog_frame = customtkinter.CTkLabel(master=self.debuglog_frame, text="CAN LOG", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.label_debuglog_frame.grid(row=rownr, column=0, padx=10, pady=10, sticky="")

        rownr += 1
        self.canlog_read_button = customtkinter.CTkButton(self.debuglog_frame, command=self.canlog_read_event, width=20, text = "READ CAN LOG")
        self.canlog_read_button.grid(row=rownr, column=0, padx=(0,20), pady=5, sticky="")
        self.canlog_reset_button = customtkinter.CTkButton(self.debuglog_frame, command=self.canlog_reset_event, width=20, text = "RESET CAN LOG")
        self.canlog_reset_button.grid(row=rownr, column=1, padx=(0,20), pady=5, sticky="")

        # create slider and progressbar frame
        # self.seg_button_1 = customtkinter.CTkSegmentedButton(self.row1_col1_master_frame)
        # self.seg_button_1.grid(row=0, column=0, columnspan=3, padx=(20, 10), pady=(10, 10), sticky="ew")
        # self.progressbar_1 = customtkinter.CTkProgressBar(self.row1_col1_master_frame)
        # self.progressbar_1.grid(row=1, column=0, columnspan=3, padx=(20, 10), pady=(10, 10), sticky="ew")
        # self.progressbar_2 = customtkinter.CTkProgressBar(self.row1_col1_master_frame)
        # self.progressbar_2.grid(row=2, column=0, columnspan=3, padx=(20, 10), pady=(10, 10), sticky="ew")
        # self.slider_1 = customtkinter.CTkSlider(self.row1_col1_master_frame, from_=0, to=1, number_of_steps=4)
        # self.slider_1.grid(row=3, column=0, columnspan=3, padx=(20, 10), pady=(10, 10), sticky="ew")
        # self.slider_2 = customtkinter.CTkSlider(self.row1_col1_master_frame, orientation="vertical")
        # self.slider_2.grid(row=0, column=1, rowspan=5, padx=(10, 10), pady=(10, 10), sticky="ns")
        # self.progressbar_3 = customtkinter.CTkProgressBar(self.row1_col1_master_frame, orientation="vertical")
        # self.progressbar_3.grid(row=0, column=2, rowspan=5, padx=(10, 20), pady=(10, 10), sticky="ns")
        rownr = 0
        # self.current_max_l = customtkinter.CTkEntry(self.voltages_frame          , width=50, justify="right", placeholder_text="20 A")
        self.row1_col0_master_frame = customtkinter.CTkFrame(self, width=140, corner_radius=10)
        self.row1_col0_master_frame.grid(row=1, column=0, rowspan=1, padx=(20, 0), pady=(20, 0), sticky="nsew")

        ### HEARTBEAT
        self.heartbeat_entry = customtkinter.CTkEntry(self.row1_col0_master_frame, width=30, justify="right", placeholder_text="0")
        self.heartbeat_entry.grid(row=rownr, column=0, padx=(20, 0), pady=(20, 0), sticky="new")
        self.heartbeat_label = customtkinter.CTkLabel(self.row1_col0_master_frame, text="ms")
        self.heartbeat_label.grid(row=rownr, column=1, padx=(0, 0), pady=(20, 0), sticky="new")
        self.heartbeat_button = customtkinter.CTkButton(self.row1_col0_master_frame, command=self.heartbeat_event, text = "HEARTBEAT")
        self.heartbeat_button.grid(row=rownr, column=2, columnspan=2, padx=(10, 10), pady=(20, 0), sticky="new")
        self.heartbeat_entry.insert(0,"0")

        rownr += 1
        self.time_entry = customtkinter.CTkEntry(self.row1_col0_master_frame, width=85, justify="right", placeholder_text="0")
        self.time_entry.grid(row=rownr, column=0, padx=(10, 0), pady=(20, 0), sticky="nsew")
        self.time_label = customtkinter.CTkLabel(self.row1_col0_master_frame, text="s")
        self.time_label.grid(row=rownr, column=1, padx=(0, 0), pady=(20, 0), sticky="nsew")
        self.time_button = customtkinter.CTkButton(self.row1_col0_master_frame, command=self.time_set_event, width=80, text = "TIME")
        self.time_button.grid(row=rownr, column=2, padx=(10,0), pady=(20, 0))
        self.time_button = customtkinter.CTkButton(self.row1_col0_master_frame, command=self.time_read_event, width=20, text = "R")
        self.time_button.grid(row=rownr, column=3, padx=(10, 10), pady=(20, 0), sticky="w")
        self.time_entry.insert(0,"0")


        ### create appearance frame
        rownr = 0
        self.appearance_mode_frame = customtkinter.CTkFrame(self.row1_col0_master_frame, corner_radius = 10)
        self.appearance_mode_frame.grid(row=2, column=0, rowspan=1, columnspan=4, padx=(20, 20), pady=20, sticky="nsew")
        rownr = 0
        self.appearance_mode_frame = customtkinter.CTkLabel(self.appearance_mode_frame, text="Appearance Mode:")
        self.appearance_mode_frame.grid(row=1, column=0, padx=10, pady=0)
        rownr += 1
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.appearance_mode_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=rownr, column=0, padx=10, pady=0)
        # rownr += 1
        # self.scaling_label_frame = customtkinter.CTkFrame(self.appearance_mode_frame, corner_radius=10)
        # self.scaling_label_frame.grid(row=rownr, column=0, rowspan=1, sticky="nsew")
        rownr += 1
        self.scaling_label_frame = customtkinter.CTkLabel(self.appearance_mode_frame, text="UI Scaling:", anchor="w")
        self.scaling_label_frame.grid(row=rownr, column=0, padx=10, pady=0)
        rownr += 1
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.appearance_mode_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=rownr, column=0, padx=10, pady=(0,10))


        # create switches frame
        self.row1_col1_master_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.row1_col1_master_frame.grid(row=1, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.row1_col1_master_frame.grid_columnconfigure(0, weight=1)
        self.row1_col1_master_frame.grid_rowconfigure(4, weight=1)

        self.row1_col1_sub_master_frame = customtkinter.CTkFrame(self.row1_col1_master_frame, fg_color="transparent")
        self.row1_col1_sub_master_frame.grid(row=1, column=0, columnspan=2, padx=(0, 0), pady=(0, 0), sticky="nsew")
        self.heartbeat_button = customtkinter.CTkButton(self.row1_col1_sub_master_frame, command=self.clear_log_box_event, text = "CLEAR LOG BOX")
        self.heartbeat_button.grid(row=0, column=0, padx=20, pady=5, sticky="new")


        self.switches_frame = customtkinter.CTkFrame(self.row1_col1_master_frame, width=140, corner_radius=10)
        self.switches_frame.grid(row=5, column=0, rowspan=2, columnspan=3, padx=(20, 20), pady=(20, 0), sticky="nsew")
        rownr = 0
        rownr += 1
        self.logo_label = customtkinter.CTkLabel(self.switches_frame, text="SWITCHES", font=customtkinter.CTkFont(size=20, weight="bold"))
        #self.switches_frame = customtkinter.CTkFrame(self, label_text="SWITCHES")
        self.logo_label.grid(row=rownr, column=0, padx=20, pady=(20, 10))
        self.switches_frame.grid_columnconfigure(4, weight=1)
        #self.switches_frame = []
        # self.switches_inrush = customtkinter.CTkSwitch(self.switches_frame, command=self.switches_inrush_event, text=f"INRUSH")#, variable=switch_var, onvalue="ON", offvalue="OFF")
        # self.switches_inrush.grid(row=1, column=0, pady=5, padx=12, sticky="n")
        rownr += 1
        # self.switches_inrush = customtkinter.CTkSwitch(self.switches_frame, command=self.switches_inrush_event, text=f"INRUSH")
        self.switches_inrush = customtkinter.CTkCheckBox(self.switches_frame, command=None, state=DISABLED, text=f"INRUSH")
        self.switches_inrush.grid(row=rownr, column=0, pady=5, padx=12, sticky="n")
        # self.switches_inrush_toggle = customtkinter.CTkButton(self.switches_frame, command=self.switches_inrush_event, width=20, text=f"T")
        # self.switches_inrush_toggle.grid(row=rownr, column=1, pady=5, padx=12, sticky="n")
        self.switches_inrush_read = customtkinter.CTkButton(self.switches_frame, command=self.switches_inrush_read_event, width=20, text=f"R")
        self.switches_inrush_read.grid(row=rownr, column=2, pady=5, padx=12, sticky="n")
        rownr += 1
        # self.switches_load = customtkinter.CTkSwitch(self.switches_frame, command=self.switches_load_event, text=f"LOAD")
        self.switches_load = customtkinter.CTkCheckBox(self.switches_frame, command=None, state=DISABLED, text=f"LOAD")
        self.switches_load.grid(row=rownr, column=0, pady=5, padx=12, sticky="n")
        self.switches_load_toggle = customtkinter.CTkButton(self.switches_frame, command=self.switches_load_event, width=20, text=f"T")
        self.switches_load_toggle.grid(row=rownr, column=1, pady=5, padx=12, sticky="n")
        self.switches_load_read = customtkinter.CTkButton(self.switches_frame, command=self.switches_load_read_event, width=20, text=f"R")
        self.switches_load_read.grid(row=rownr, column=2, pady=5, padx=12, sticky="n")
        rownr += 1
        # self.switches_share = customtkinter.CTkSwitch(self.switches_frame, command=self.switches_share_event, text=f"SHARE")
        self.switches_share = customtkinter.CTkCheckBox(self.switches_frame, command=None, state=DISABLED ,text=f"SHARE")
        self.switches_share.grid(row=rownr, column=0, pady=5, padx=12, sticky="n")
        self.switches_share_toggle = customtkinter.CTkButton(self.switches_frame, command=self.switches_share_event, width=20, text=f"T")
        self.switches_share_toggle.grid(row=rownr, column=1, pady=5, padx=12, sticky="n")
        self.switches_share_read = customtkinter.CTkButton(self.switches_frame, command=self.switches_share_read_event, width=20, text=f"R")
        self.switches_share_read.grid(row=rownr, column=2, pady=5, padx=12, sticky="n")
        rownr += 1
        # self.switches_input = customtkinter.CTkSwitch(self.switches_frame, command=self.switches_input_event, text=f"INPUT")
        self.switches_input = customtkinter.CTkCheckBox(self.switches_frame, command=None, state=DISABLED, text=f"INPUT")
        self.switches_input.grid(row=rownr, column=0, pady=5, padx=12, sticky="n")
        self.switches_input_toggle = customtkinter.CTkButton(self.switches_frame, command=self.switches_input_event, width=20, text=f"T")
        self.switches_input_toggle.grid(row=rownr, column=1, pady=5, padx=12, sticky="n")
        self.switches_input_read = customtkinter.CTkButton(self.switches_frame, command=self.switches_input_read_event, width=20, text=f"R")
        self.switches_input_read.grid(row=rownr, column=2, pady=5, padx=12, sticky="n")
        #switch.grid(row=i, column=0, padx=10, pady=(0, 20))
        #self.scrollable_frame_switches.append(switch)


        # create checkbox and switch frame
        self.checkbox_slider_frame = customtkinter.CTkFrame(self.row0_col3_master_frame)
        self.checkbox_slider_frame.grid(row=1, column=3, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.checkbox_1 = customtkinter.CTkCheckBox(master=self.checkbox_slider_frame)
        self.checkbox_1.grid(row=1, column=0, pady=(20, 0), padx=20, sticky="n")
        self.checkbox_2 = customtkinter.CTkCheckBox(master=self.checkbox_slider_frame, fg_color="green")
        self.checkbox_2.grid(row=2, column=0, pady=(20, 0), padx=20, sticky="n")
        self.checkbox_3 = customtkinter.CTkCheckBox(master=self.checkbox_slider_frame)
        self.checkbox_3.grid(row=3, column=0, pady=20, padx=20, sticky="n")


        # set default values
        #self.state_off_button.configure(state="disabled")
        self.checkbox_1.configure(state="disabled", text="OFF", fg_color="red")
        self.checkbox_1.select()
        #self.scrollable_frame_switches[0].select()
        #self.scrollable_frame_switches[4].select()
        # self.radio_button_1.configure(state="enabled")

        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")
        self.optionmenu_1.set("CTkOptionmenu")
        # self.combobox_1.set("CTkComboBox")

        # self.slider_1.configure(command=self.progressbar_2.set)
        # self.slider_2.configure(command=self.progressbar_3.set)
        # self.progressbar_1.configure(mode="indeterminnate")
        # self.progressbar_1.start()
        self.textbox.insert("0.0", "START\r\n")
        self.textbox.configure(state="disabled") # read only
        # self.seg_button_1.configure(values=["CTkSegmBut", "Value 2", "Value 3"])
        # self.seg_button_1.set("Value 2")


        # create state of charge frame
        self.state_of_charge_frame = customtkinter.CTkFrame(self, width=140, corner_radius=10)
        self.state_of_charge_frame.grid(row=0, column=4, rowspan=3, pady=(20, 0), sticky="nsew")
        self.state_of_charge_frame.grid_rowconfigure(5, weight=0)
        rownr = 0
        self.state_of_charge_logo_label = customtkinter.CTkLabel(self.state_of_charge_frame, text="CHARGE/HEALTH", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.state_of_charge_logo_label.grid(row=rownr, column=0, columnspan=2, padx=20, pady=(20, 10))

        rownr += 1
        self.state_of_cell_frame = customtkinter.CTkFrame(self.state_of_charge_frame, width=140, corner_radius=10)
        self.state_of_cell_frame.grid(row=rownr, column=0, rowspan=3, sticky="nsew")
        self.state_of_cell_frame.grid_rowconfigure(5, weight=1)

        rownr = 0
        self.state_of_charge_logo_label = customtkinter.CTkLabel(self.state_of_cell_frame, text="CELL CHARGE [V]", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.state_of_charge_logo_label.grid(row=rownr, column=0, columnspan=3, padx=20, pady=(20, 10))
        self.state_of_charge_cell_charge_read_button = customtkinter.CTkButton(self.state_of_cell_frame, command=self.energy_cell_charge_read_event, width=20, text = "R")
        self.state_of_charge_cell_charge_read_button.grid(row=rownr, column=3, padx=(0,20), pady=5, sticky="w")
        self.state_of_charge_cell_health_read_button = customtkinter.CTkButton(self.state_of_cell_frame, command=self.bank_charge_read_event, width=20, text = "R")
        self.state_of_charge_cell_health_read_button.grid(row=rownr, column=4, padx=(0,20), pady=5, sticky="")

        for i in range(1, 16):
            self.state_of_charge_2_entry = customtkinter.CTkEntry(self.state_of_cell_frame, width=50, justify="right", placeholder_text="20")
            self.state_of_charge_2_entry.grid(row=i+rownr, column=0, padx=(20, 0), pady=(5), sticky="nsew")
            self.state_of_charge_2_label = customtkinter.CTkLabel(self.state_of_cell_frame, text=f'{i}')
            self.state_of_charge_2_label.grid(row=i, column=1, padx=(5), sticky="nsew")
            self.cellVoltage[OD.S_STATE_OF_CHARGE_OF_ENERGY_CELL_01+(i-1)]=self.state_of_charge_2_entry
        for i in range(16, 31):
            self.state_of_charge_2_entry = customtkinter.CTkEntry(self.state_of_cell_frame, width=50, justify="right", placeholder_text="20")
            self.state_of_charge_2_entry.grid(row=i-15, column=2, padx=(20, 0), pady=(5), sticky="nsew")
            self.state_of_charge_2_label = customtkinter.CTkLabel(self.state_of_cell_frame, text=f'{i}')
            self.state_of_charge_2_label.grid(row=i-15, column=3, padx=(5), sticky="nsew")
            self.cellVoltage[OD.S_STATE_OF_CHARGE_OF_ENERGY_CELL_16+(i-16)]=self.state_of_charge_2_entry
        self.cell_progressbar_charge = customtkinter.CTkProgressBar(self.state_of_cell_frame, orientation="vertical")
        self.cell_progressbar_charge.grid(row=1, column=4, rowspan=15, padx=(20, 10), pady=(10, 10), sticky="ns")


        # rownr = 0
        # self.state_of_charge_logo_label = customtkinter.CTkLabel(self.state_of_cell_frame, text="CELL HEALTH [%F]", font=customtkinter.CTkFont(size=20, weight="bold"))
        # self.state_of_charge_logo_label.grid(row=0, column=5, columnspan=3, padx=20, pady=(20, 10))
        # self.state_of_charge_cell_health_read_button = customtkinter.CTkButton(self.state_of_cell_frame, command=self.energy_cell_health_read_event, width=20, text = "R")
        # self.state_of_charge_cell_health_read_button.grid(row=rownr, column=8, padx=(0,20), pady=5, sticky="w")
        # self.state_of_charge_cell_health_read_button = customtkinter.CTkButton(self.state_of_cell_frame, command=self.bank_health_read_event, width=20, text = "R")
        # self.state_of_charge_cell_health_read_button.grid(row=rownr, column=9, padx=(0,20), pady=5, sticky="")

        rownr = 0
        self.state_of_charge_label = customtkinter.CTkLabel(self.state_of_cell_frame, text="STATE OF CHARGE [%]") #, font=customtkinter.CTkFont(size=10, weight="bold"))
        self.state_of_charge_label.grid(row=rownr, column=5, columnspan=3, padx=20, pady=(20, 10))
        rownr += 1
        self.state_of_charge_entry = customtkinter.CTkEntry(self.state_of_cell_frame, width=25, justify="right", placeholder_text="20")
        self.state_of_charge_entry.grid(row=rownr, column=5, padx=(20, 0), pady=(5), sticky="nsew")
        self.state_of_charge_unit_label = customtkinter.CTkLabel(self.state_of_cell_frame, text="%")
        self.state_of_charge_unit_label.grid(row=rownr, column=6, padx=(5), sticky="nsew")
        self.state_of_charge_read_button = customtkinter.CTkButton(self.state_of_cell_frame, command=self.bank_charge_read_event, width=20, text = "R")
        self.state_of_charge_read_button.grid(row=rownr, column=7, padx=(0,20), pady=5, sticky="")
        
        rownr += 1
        self.state_of_health_label = customtkinter.CTkLabel(self.state_of_cell_frame, text="STATE OF HEALTH [%]") #, font=customtkinter.CTkFont(size=10, weight="bold"))
        self.state_of_health_label.grid(row=rownr, column=5, columnspan=3, padx=20, pady=(5))
        rownr += 1
        self.state_of_health_entry = customtkinter.CTkEntry(self.state_of_cell_frame, width=25, justify="right", placeholder_text="20")
        self.state_of_health_entry.grid(row=rownr, column=5, padx=(20, 0), pady=(5), sticky="nsew")
        self.state_of_health_unit_label = customtkinter.CTkLabel(self.state_of_cell_frame, text="%")
        self.state_of_health_unit_label.grid(row=rownr, column=6, padx=(5), sticky="nsew")
        self.state_of_health_read_button = customtkinter.CTkButton(self.state_of_cell_frame, command=self.bank_health_read_event, width=20, text = "R")
        self.state_of_health_read_button.grid(row=rownr, column=7, padx=(0,20), pady=5, sticky="")


        rownr += 1
        self.state_of_remaining_energy_label = customtkinter.CTkLabel(self.state_of_cell_frame, text="REMAINING ENERGY [J]") #, font=customtkinter.CTkFont(size=10, weight="bold"))
        self.state_of_remaining_energy_label.grid(row=rownr, column=5, columnspan=3, padx=20, pady=(5))
        rownr += 1
        self.state_of_remaining_energy_entry = customtkinter.CTkEntry(self.state_of_cell_frame, width=25, justify="right", placeholder_text="20")
        self.state_of_remaining_energy_entry.grid(row=rownr, column=5, padx=(10, 0), pady=(5), sticky="nsew")
        self.state_of_remaining_energy_unit_label = customtkinter.CTkLabel(self.state_of_cell_frame, text="J")
        self.state_of_remaining_energy_unit_label.grid(row=rownr, column=6, padx=(5), sticky="nsew")
        self.state_of_remaining_energy_read_button = customtkinter.CTkButton(self.state_of_cell_frame, command=self.bank_remaining_energy_read_event, width=20, text = "R")
        self.state_of_remaining_energy_read_button.grid(row=rownr, column=7, padx=(0,20), pady=5, sticky="")

        
        # for i in range(1, 16):
        #     self.state_of_charge_2_entry = customtkinter.CTkEntry(self.state_of_cell_frame, width=50, justify="right", placeholder_text="20")
        #     self.state_of_charge_2_entry.grid(row=i+rownr, column=5, padx=(20, 0), pady=(5), sticky="nsew")
        #     self.state_of_charge_2_label = customtkinter.CTkLabel(self.state_of_cell_frame, text=f'{i}')
        #     self.state_of_charge_2_label.grid(row=i, column=6, padx=(5), sticky="nsew")
        # for i in range(16, 31):
        #     self.state_of_charge_2_entry = customtkinter.CTkEntry(self.state_of_cell_frame, width=50, justify="right", placeholder_text="20")
        #     self.state_of_charge_2_entry.grid(row=i-15, column=7, padx=(20, 0), pady=(5), sticky="nsew")
        #     self.state_of_charge_2_label = customtkinter.CTkLabel(self.state_of_cell_frame, text=f'{i}')
        #     self.state_of_charge_2_label.grid(row=i-15, column=8, padx=(5), sticky="nsew")
        # self.cell_progressbar_health = customtkinter.CTkProgressBar(self.state_of_cell_frame, orientation="vertical")
        # self.cell_progressbar_health.grid(row=1, column=9, rowspan=15, padx=(20, 10), pady=(10, 10), sticky="ns")

        rownr = 4
        self.state_of_charge_set_cell_value_frame = customtkinter.CTkFrame(self.state_of_charge_frame, width=140, corner_radius=10)
        self.state_of_charge_set_cell_value_frame.grid(row=rownr, column=0, rowspan=2, pady=(20,0), sticky="nsew")
        self.state_of_charge_set_cell_value_frame.grid_rowconfigure(5, weight=1)

        rownr = 0
        self.energy_cell_max_volt_entry = customtkinter.CTkEntry(self.state_of_charge_set_cell_value_frame, width=50, justify="right", placeholder_text="2")
        self.energy_cell_max_volt_entry.grid(row=rownr, column=0, padx=(20, 0), pady=(5), sticky="new")
        self.energy_cell_max_volt_label = customtkinter.CTkLabel(self.state_of_charge_set_cell_value_frame, text="V")
        self.energy_cell_max_volt_label.grid(row=rownr, column=1, padx=(5), sticky="nsew")
        self.energy_cell_max_volt_button = customtkinter.CTkButton(self.state_of_charge_set_cell_value_frame, command=self.cell_max_volt_event, text = "MAX VOLTAGE ENERGY CELL")
        self.energy_cell_max_volt_button.grid(row=rownr, column=2, padx=20, pady=5, sticky="new")
        self.energy_cell_max_volt_button_read = customtkinter.CTkButton(self.state_of_charge_set_cell_value_frame, command=self.cell_max_volt_read_event, width=20, text = "R")
        self.energy_cell_max_volt_button_read.grid(row=rownr, column=3, padx=(0,20), pady=5, sticky="w")
        self.energy_cell_max_volt_entry.insert(0,"3")

        rownr += 1
        self.energy_cell_min_volt_entry = customtkinter.CTkEntry(self.state_of_charge_set_cell_value_frame, width=50, justify="right", placeholder_text="1")
        self.energy_cell_min_volt_entry.grid(row=rownr, column=0, padx=(20, 0), pady=(5), sticky="new")
        self.energy_cell_min_volt_label = customtkinter.CTkLabel(self.state_of_charge_set_cell_value_frame, text="V")
        self.energy_cell_min_volt_label.grid(row=rownr, column=1, padx=(5), sticky="nsew")
        self.energy_cell_min_volt_cellt_button = customtkinter.CTkButton(self.state_of_charge_set_cell_value_frame, command=self.cell_min_volt_event, text = "MIN VOLTAGE ENERGY CELL")
        self.energy_cell_min_volt_cellt_button.grid(row=rownr, column=2, padx=20, pady=5, sticky="new")
        self.energy_cell_max_volt_button_read = customtkinter.CTkButton(self.state_of_charge_set_cell_value_frame, command=self.cell_min_volt_read_event, width=20, text = "R")
        self.energy_cell_max_volt_button_read.grid(row=rownr, column=3, padx=(0,20), pady=5, sticky="w")
        self.energy_cell_min_volt_entry.insert(0,"1")
        # self.cell_progressbar_health.grid(row=1, column=9, rowspan=15, padx=(20, 10), pady=(10, 10), sticky="ns")

        rownr = 6
        self.state_of_charge_set_bank_value_frame = customtkinter.CTkFrame(self.state_of_charge_frame, width=140, corner_radius=10)
        self.state_of_charge_set_bank_value_frame.grid(row=rownr, column=0, rowspan=3, pady=(20,0), sticky="nsew")
        self.state_of_charge_set_bank_value_frame.grid_rowconfigure(5, weight=1)

        rownr = 0
        self.energy_bank_max_volt_entry = customtkinter.CTkEntry(self.state_of_charge_set_bank_value_frame, width=50, justify="right", placeholder_text="60")
        self.energy_bank_max_volt_entry.grid(row=rownr, column=0, padx=(20, 0), pady=(5), sticky="new")
        self.energy_bank_max_volt_label = customtkinter.CTkLabel(self.state_of_charge_set_bank_value_frame, text="V")
        self.energy_bank_max_volt_label.grid(row=rownr, column=1, padx=(5), sticky="nsew")
        self.energy_bank_max_volt_button = customtkinter.CTkButton(self.state_of_charge_set_bank_value_frame, command=self.bank_max_volt_event, text = "MAX VOLTAGE ENERGY BANK")
        self.energy_bank_max_volt_button.grid(row=rownr, column=2, padx=20, pady=5, sticky="new")
        self.energy_bank_max_volt_button = customtkinter.CTkButton(self.state_of_charge_set_bank_value_frame, command=self.bank_max_volt_read_event, width=20, text = "R")
        self.energy_bank_max_volt_button.grid(row=rownr, column=3, padx=(0,20), pady=5, sticky="w")
        self.energy_bank_max_volt_entry.insert(0,"90")

        rownr += 1
        self.energy_bank_const_volt_threshold_entry = customtkinter.CTkEntry(self.state_of_charge_set_bank_value_frame, width=50, justify="right", placeholder_text="60")
        self.energy_bank_const_volt_threshold_entry.grid(row=rownr, column=0, padx=(20, 0), pady=(5), sticky="new")
        self.energy_bank_const_volt_threshold_entry_label = customtkinter.CTkLabel(self.state_of_charge_set_bank_value_frame, text="V")
        self.energy_bank_const_volt_threshold_entry_label.grid(row=rownr, column=1, padx=(5), sticky="nsew")
        self.energy_bank_const_volt_threshold_entry_button = customtkinter.CTkButton(self.state_of_charge_set_bank_value_frame, command=self.bank_const_volt_event, text = "CONSTANT VOLT CHARGE THRESHOLD")
        self.energy_bank_const_volt_threshold_entry_button.grid(row=rownr, column=2, padx=20, pady=5, sticky="new")
        self.energy_bank_const_volt_threshold_entry_button = customtkinter.CTkButton(self.state_of_charge_set_bank_value_frame, command=self.bank_const_volt_read_event, width=20, text = "R")
        self.energy_bank_const_volt_threshold_entry_button.grid(row=rownr, column=3, padx=(0,20), pady=5, sticky="w")
        self.energy_bank_const_volt_threshold_entry.insert(0,"90")

        rownr += 1
        self.energy_bank_min_volt_entry = customtkinter.CTkEntry(self.state_of_charge_set_bank_value_frame, width=50, justify="right", placeholder_text="30")
        self.energy_bank_min_volt_entry.grid(row=rownr, column=0, padx=(20, 0), pady=(5), sticky="new")
        self.energy_bank_min_volt_label = customtkinter.CTkLabel(self.state_of_charge_set_bank_value_frame, text="V")
        self.energy_bank_min_volt_label.grid(row=rownr, column=1, padx=(5), sticky="nsew")
        self.energy_bank_min_volt_button = customtkinter.CTkButton(self.state_of_charge_set_bank_value_frame, command=self.bank_min_volt_event, text = "MIN VOLTAGE ENERGY BANK")
        self.energy_bank_min_volt_button.grid(row=rownr, column=2, padx=20, pady=5, sticky="new")
        self.energy_bank_min_volt_button = customtkinter.CTkButton(self.state_of_charge_set_bank_value_frame, command=self.bank_min_volt_read_event, width=20, text = "R")
        self.energy_bank_min_volt_button.grid(row=rownr, column=3, padx=(0,20), pady=5, sticky="w")
        self.energy_bank_min_volt_entry.insert(0,"30")

        rownr += 1
        self.energy_bank_trickle_charge_threshold_entry = customtkinter.CTkEntry(self.state_of_charge_set_bank_value_frame, width=50, justify="right", placeholder_text="40")
        self.energy_bank_trickle_charge_threshold_entry.grid(row=rownr, column=0, padx=(20, 0), pady=(5), sticky="new")
        self.energy_bank_trickle_charge_threshold_label = customtkinter.CTkLabel(self.state_of_charge_set_bank_value_frame, text="V")
        self.energy_bank_trickle_charge_threshold_label.grid(row=rownr, column=1, padx=(5), sticky="nsew")
        self.energy_bank_trickle_charge_threshold_button = customtkinter.CTkButton(self.state_of_charge_set_bank_value_frame, command=self.bank_trickle_charge_event, text = "TRICKLE CHARGE THRESHOLD")
        self.energy_bank_trickle_charge_threshold_button.grid(row=rownr, column=2, padx=20, pady=5, sticky="new")
        self.energy_bank_trickle_charge_threshold_button = customtkinter.CTkButton(self.state_of_charge_set_bank_value_frame, command=self.bank_trickle_charge_read_event, width=20, text = "R")
        self.energy_bank_trickle_charge_threshold_button.grid(row=rownr, column=3, padx=(0,20), pady=5, sticky="w")
        self.energy_bank_trickle_charge_threshold_entry.insert(0,"30")


        # for testing and for show
        # self.state_of_charge_logo_label = customtkinter.CTkLabel(self.state_of_charge_frame, text="BAR", font=customtkinter.CTkFont(size=20, weight="bold"))
        # self.state_of_charge_logo_label.grid(row=0, column=3, columnspan=2, padx=20, pady=(20, 10))
        # self.slider_charge = customtkinter.CTkSlider(self.state_of_charge_frame, orientation="vertical")
        # self.slider_charge.grid(row=1, column=3, rowspan=15, padx=(10, 10), pady=(10, 10), sticky="ns")
        # self.slider_heatlh = customtkinter.CTkSlider(self.state_of_charge_frame, orientation="vertical")
        # self.slider_heatlh.grid(row=1, column=4, rowspan=15, padx=(10, 10), pady=(10, 10), sticky="ns")
        # self.slider_charge.configure(command=self.cell_progressbar_charge.set)
        # self.slider_heatlh.configure(command=self.cell_progressbar_health.set)

        self.state_read_state_event()

    ### DC BUS
    def voltages_max_allowed_dc_bus_voltage_event(self):
        voltages_max_allowed_dc_bus_voltage.ccs = 0x2F
        value = int(self.voltages_max_allowed_dc_bus_voltage_entry.get())
        voltages_max_allowed_dc_bus_voltage.set_data_byte4(value)
        voltages_max_allowed_dc_bus_voltage.sendCanMessage()

    def voltages_max_allowed_dc_bus_voltage_read_event(self):
        value = int(self.voltages_max_allowed_dc_bus_voltage_entry.get())
        voltages_max_allowed_dc_bus_voltage.ccs = 0x40
        voltages_max_allowed_dc_bus_voltage.set_data_byte4(0)
        voltages_max_allowed_dc_bus_voltage.sendCanMessage()

    def voltages_target_voltage_event(self):
        voltages_target_voltage.ccs = 0x2F
        value = int(self.voltages_target_voltage_entry.get())
        voltages_target_voltage.set_data_byte4(value)
        voltages_target_voltage.sendCanMessage()

    def voltages_target_voltage_read_event(self):
        voltages_target_voltage.ccs = 0x40
        value = int(self.voltages_target_voltage_entry.get())
        voltages_target_voltage.set_data_byte4(value)
        voltages_target_voltage.sendCanMessage()

    def voltages_min_allowed_dc_bus_voltage_event(self):
        voltages_min_allowed_dc_bus_voltage.ccs = 0x2F
        value = int(self.voltages_min_allowed_dc_bus_voltage_entry.get())
        voltages_min_allowed_dc_bus_voltage.set_data_byte4(value)
        voltages_min_allowed_dc_bus_voltage.sendCanMessage()

    def voltages_min_allowed_dc_bus_voltage_read_event(self):
        voltages_min_allowed_dc_bus_voltage.ccs = 0x40
        value = int(self.voltages_min_allowed_dc_bus_voltage_entry.get())
        voltages_min_allowed_dc_bus_voltage.set_data_byte4(value)
        voltages_min_allowed_dc_bus_voltage.sendCanMessage()

    def voltages_short_circuit_voltage_event(self):
        voltages_dc_bus_short_circuit_limit.ccs = 0x2F
        value = int(self.voltages_dc_bus_short_circuit_limit_entry.get())
        voltages_dc_bus_short_circuit_limit.set_data_byte4(value)
        voltages_dc_bus_short_circuit_limit.sendCanMessage()

    def voltages_short_circuit_voltage_read_event(self):
        voltages_dc_bus_short_circuit_limit.ccs = 0x40
        value = int(self.voltages_dc_bus_short_circuit_limit_entry.get())
        voltages_dc_bus_short_circuit_limit.set_data_byte4(value)
        voltages_dc_bus_short_circuit_limit.sendCanMessage()

    def current_available_power_budget_input_event(self):
        power_pudget_dc_input.ccs = 0x2B
        power_pudget_dc_input.subIndex = OD.S_AVAILABLE_POWER_BUDGET_DC_INPUT
        value = int(self.power_pudget_dc_input_available_power_budget_input_event_entry.get())
        power_pudget_dc_input.set_data_byte4(low_byte(value))
        power_pudget_dc_input.set_data_byte5(high_byte(value))
        power_pudget_dc_input.sendCanMessage()

    def current_available_power_budget_input_read_event(self):
        power_pudget_dc_input.ccs = 0x40
        power_pudget_dc_input.subIndex = OD.S_AVAILABLE_POWER_BUDGET_DC_INPUT
        value = int(self.power_pudget_dc_input_available_power_budget_input_event_entry.get())
        power_pudget_dc_input.set_data_byte4(low_byte(value))
        power_pudget_dc_input.set_data_byte5(high_byte(value))
        power_pudget_dc_input.sendCanMessage()

    def power_pudget_dc_input_line_A_event(self):
        power_pudget_dc_input.ccs = 0x2B
        power_pudget_dc_input.subIndex = OD.S_MAX_CURRENT_POWER_LINE_A
        value = int(self.power_pudget_dc_input_line_A_entry.get())
        power_pudget_dc_input.set_data_byte4(low_byte(value))
        power_pudget_dc_input.set_data_byte5(high_byte(value))
        power_pudget_dc_input.sendCanMessage()

    def power_pudget_dc_input_line_A_read_event(self):
        power_pudget_dc_input.ccs = 0x40
        power_pudget_dc_input.subIndex = OD.S_MAX_CURRENT_POWER_LINE_A
        value = int(self.power_pudget_dc_input_line_A_entry.get())
        power_pudget_dc_input.set_data_byte4(low_byte(value))
        power_pudget_dc_input.set_data_byte5(high_byte(value))
        power_pudget_dc_input.sendCanMessage()

    # def power_pudget_dc_input_line_B_event(self):
        # power_pudget_dc_input.ccs = 0x2B
        # power_pudget_dc_input.subIndex = OD.S_MAX_CURRENT_POWER_LINE_B
        # value = int(self.power_pudget_dc_input_line_B_entry.get())
        # power_pudget_dc_input.set_data_byte4(low_byte(value))
        # power_pudget_dc_input.set_data_byte5(high_byte(value))
        # power_pudget_dc_input.sendCanMessage()

    # def power_pudget_dc_input_line_B_read_event(self):
        # power_pudget_dc_input.ccs = 0x40
        # power_pudget_dc_input.subIndex = OD.S_MAX_CURRENT_POWER_LINE_B
        # value = int(self.power_pudget_dc_input_line_B_entry.get())
        # power_pudget_dc_input.set_data_byte4(low_byte(value))
        # power_pudget_dc_input.set_data_byte5(high_byte(value))
        # power_pudget_dc_input.sendCanMessage()

    def current_max_load_current_event(self):
        current_max_load_current.ccs = 0x2B
        value = int(float(self.current_max_load_current_entry.get())) & 0xffff
        current_max_load_current.set_data_byte4(low_byte(value))
        current_max_load_current.set_data_byte5(high_byte(value))
        current_max_load_current.sendCanMessage()

    def current_max_load_current_read_event(self):
        current_max_load_current.ccs = 0x40
        value = int(float(self.current_max_load_current_entry.get())) & 0xffff
        current_max_load_current.set_data_byte4(high_byte(value))
        current_max_load_current.set_data_byte5(low_byte(value))
        current_max_load_current.sendCanMessage()

    def current_max_ess_current_event(self):
        current_max_ess_current.ccs = 0x2F
        value = float(self.current_max_ess_current_entry.get())
        value = int(value*16) & 0xff
        current_max_ess_current.set_data_byte4(value)
        current_max_ess_current.sendCanMessage()

    def current_max_ess_current_read_event(self):
        current_max_ess_current.ccs = 0x40
        value = float(self.current_max_ess_current_entry.get())
        value = int(value*16)
        current_max_ess_current.set_data_byte4(high_byte(value))
        current_max_ess_current.sendCanMessage()

    def read_power_dc_voltage_event(self):
        read_power.subIndex = OD.S_READ_VOLTAGE_AT_DC_BUS
        read_power.sendCanMessage()

    def read_power_dc_vstore_event(self):
        self.bank_charge_read_event()

    def read_power_load_current_event(self):
        read_power.subIndex = OD.S_READ_LOAD_CURRENT
        read_power.sendCanMessage()
    
    def read_power_supercap_current_event(self):
        read_current_ess_current.sendCanMessage()

    def read_power_load_power_event(self):
        read_power.subIndex = OD.S_POWER_CONSUMED_BY_LOAD
        read_power.sendCanMessage()

    def read_power_input_power_event(self):
        read_power.subIndex = OD.S_POWER_FROM_DC_INPUT
        read_power.sendCanMessage()

    def read_power_input_current_event(self):
        self.read_power_dc_voltage_event()
        self.read_power_input_power_event()
        

    ### store parameters
    def store_all_params_event(self):
        store_od.setSubIndex(OD.S_SAVE_ALL_PARAMETERS)
        store_od.set_data_byte7(0x65)
        store_od.set_data_byte6(0x76)
        store_od.set_data_byte5(0x61)
        store_od.set_data_byte4(0x73)
        store_od.sendCanMessage()

    def store_comm_params_event(self):
        store_od.setSubIndex(OD.S_SAVE_COMMUNICATION_PARAMETERS)
        store_od.sendCanMessage()

    def store_app_params_event(self):
        store_od.setSubIndex(OD.S_SAVE_APPLICATION_PARAMETERS)
        store_od.sendCanMessage()

    def store_mf_params_event(self):
        store_od.setSubIndex(OD.S_SAVE_MANUFACTURER_DEFINED_PARAMETERS)
        store_od.sendCanMessage()


    ### restore parameters
    def restore_all_params_event(self):
        restore_od.subIndex = OD.S_RESTORE_ALL_DEFAULT_PARAMETERS
        restore_od.sendCanMessage()

    def restore_comm_params_event(self):
        restore_od.setSubIndex(OD.S_RESTORE_COMMUNICATION_DEFAULT_PARAMETERS)
        restore_od.sendCanMessage()

    def restore_app_params_event(self):
        restore_od.setSubIndex(OD.S_RESTORE_APPLICATION_DEFAULT_PARAMETERS)
        restore_od.sendCanMessage()

    def restore_mf_params_event(self):
        restore_od.setSubIndex(OD.S_RESTORE_MANUFACTURER_DEFINED_DEFAULT_PARAMETERS)
        restore_od.sendCanMessage()


    ### DPMU type
    def read_DPMU_Type_event(self):
        print("A");
        dpmu_type_od.ccs = 0x40
        dpmu_type_od.sendCanMessage()
    def set_DPMU_Type_event(self, type_string):
        print("B");
        dpmu_type_od.ccs = 0x2F
        print("type string: ", type_string)
        match type_string:
            case "DFLT_CAP":
                dpmu_type_val = 0
            case "DFLT_CAP_W_RDNT":
                dpmu_type_val = 1
            case "DFLT_CAP_W_SUPP":
                dpmu_type_val = 2
            case "DFLT_CAP_W_RDNT_SUPP":
                dpmu_type_val = 3
            case "DFLT_BAT":
                dpmu_type_val = 4
            case "DFLT_BAT_W_RDNT":
                dpmu_type_val = 5
            case "DFLT_BAT_W_SUPP":
                dpmu_type_val = 6
            case "DFLT_BAT_W_RDNT_SUPP":
                dpmu_type_val = 7
            case "RDNT_CAP":
                dpmu_type_val = 8
            case "RDNT_CAP_W_SUPP":
                dpmu_type_val = 9
            case "RDNT_BAT":
                dpmu_type_val = 10
            case "RDNT_BAT_W_SUPP":
                dpmu_type_val = 11
            case "SUPP_CAP":
                dpmu_type_val = 12
            case "SUPP_BAT":
                dpmu_type_val = 13
            case _:
                print("BAD TYPE")
                return
        dpmu_type_od.set_data_byte4( dpmu_type_val )
        dpmu_type_od.sendCanMessage()


    ### set nodeID
    def nodeid_event(self):
        nodeid_od.ccs = 0x2F
        nodeId = int(self.nodeid_entry.get())
        nodeid_od.set_data_byte4(nodeId)
        nodeid_od.sendCanMessage()
        global nmtNodeId
        print(nmtNodeId)
        print("Set server Node Id:", nodeId)

    def nodeid_gui_event(self):
        global nmtNodeId
        nodeId = int(self.nodeid_entry.get())
        setNodeId(nodeId)
        nmtNodeId = nodeId
        print(nmtNodeId)
        print(nodeId)

        
    ### energy cell
    def energy_cell_charge_read_event(self):
        for i in range( 0 , 30):
            energy_cell.ccs = 0x40
            energy_cell.subIndex = OD.S_STATE_OF_CHARGE_OF_ENERGY_CELL_01+i
            energy_cell.set_data_byte4(0)
            energy_cell.sendCanMessage()
            timer.sleep(10/1000)
            

    def energy_cell_health_read_event(self):
        pass


    ### cell charge/health
    def cell_max_volt_event(self):
        energy_cell.ccs = 0x2F
        energy_cell.subIndex = OD.S_MAX_VOLTAGE_ENERGY_CELL
        value = float(self.energy_cell_max_volt_entry.get())
        value = int(value*16) & 0xff
        energy_cell.set_data_byte4(value)
        energy_cell.sendCanMessage()

    def cell_max_volt_read_event(self):
        energy_cell.ccs = 0x40
        energy_cell.subIndex = OD.S_MAX_VOLTAGE_ENERGY_CELL
        value = float(self.energy_cell_max_volt_entry.get())
        value = int(value*16) & 0xff
        energy_cell.set_data_byte4(0)
        energy_cell.sendCanMessage()

    def cell_min_volt_event(self):
        energy_cell.ccs = 0x2F
        energy_cell.subIndex = OD.S_MIN_VOLTAGE_ENERGY_CELL
        value = float(self.energy_cell_min_volt_entry.get())
        value = int(value*16) & 0xff
        energy_cell.set_data_byte4(value)
        energy_cell.sendCanMessage()

    def cell_min_volt_read_event(self):
        energy_cell.ccs = 0x40
        energy_cell.subIndex = OD.S_MIN_VOLTAGE_ENERGY_CELL
        value = float(self.energy_cell_min_volt_entry.get())
        value = int(value*16) & 0xff
        energy_cell.set_data_byte4(value)
        energy_cell.sendCanMessage()


    ### bank charge/health
    def bank_max_volt_event(self):
        energy_bank.ccs = 0x2F
        energy_bank.subIndex = OD.S_MAX_VOLTAGE_APPLIED_TO_ENERGY_BANK
        value = float(self.energy_bank_max_volt_entry.get())
        value = int(value) & 0xff
        energy_bank.set_data_byte4(value)
        energy_bank.sendCanMessage()

    def bank_max_volt_read_event(self):
        energy_bank.ccs = 0x40
        energy_bank.subIndex = OD.S_MAX_VOLTAGE_APPLIED_TO_ENERGY_BANK
        value = float(self.energy_bank_max_volt_entry.get())
        value = int(value) & 0xff
        energy_bank.set_data_byte4(value)
        energy_bank.sendCanMessage()

    def bank_const_volt_event(self):
        energy_bank.ccs = 0x2F
        energy_bank.subIndex = OD.S_CONSTANT_VOLTAGE_THRESHOLD
        value = float(self.energy_bank_const_volt_threshold_entry.get())
        value = int(value) & 0xff
        energy_bank.set_data_byte4(value)
        energy_bank.sendCanMessage()

    def bank_const_volt_read_event(self):
        energy_bank.ccs = 0x40
        energy_bank.subIndex = OD.S_CONSTANT_VOLTAGE_THRESHOLD
        value = float(self.energy_bank_const_volt_threshold_entry.get())
        value = int(value) & 0xff & 0xff
        energy_bank.set_data_byte4(value)
        energy_bank.sendCanMessage()

    def bank_min_volt_event(self):
        energy_bank.ccs = 0x2F
        energy_bank.subIndex = OD.S_MIN_VOLTAGE_APPLIED_TO_ENERGY_BANK
        value = float(self.energy_bank_min_volt_entry.get())
        value = int(value * 2) & 0xff
        energy_bank.set_data_byte4(value)
        energy_bank.sendCanMessage()

    def bank_min_volt_read_event(self):
        energy_bank.ccs = 0x40
        energy_bank.subIndex = OD.S_MIN_VOLTAGE_APPLIED_TO_ENERGY_BANK
        value = float(self.energy_bank_min_volt_entry.get())
        value = int(value * 2) & 0xff
        energy_bank.set_data_byte4(value)
        energy_bank.sendCanMessage()

    def bank_trickle_charge_event(self):
        energy_bank.ccs = 0x2F
        energy_bank.subIndex = OD.S_PRECONDITIONAL_THRESHOLD
        value = float(self.energy_bank_trickle_charge_threshold_entry.get())
        value = int(value) & 0xff
        energy_bank.set_data_byte4(value)
        energy_bank.sendCanMessage()

    def bank_trickle_charge_read_event(self):
        energy_bank.ccs = 0x40
        energy_bank.subIndex = OD.S_PRECONDITIONAL_THRESHOLD
        value = float(self.energy_bank_trickle_charge_threshold_entry.get())
        value = int(value) & 0xff
        energy_bank.set_data_byte4(value)
        energy_bank.sendCanMessage()

    def bank_safey_threshold_event(self):
        energy_bank.ccs = 0x2B
        energy_bank.subIndex = OD.S_SAFETY_THRESHOLD_STATE_OF_CHARGE
        value = float(self.energy_bank_safey_threshold_entry.get())
        value = int(value) & 0xffff
        energy_bank.set_data_byte4(low_byte(value))
        energy_bank.set_data_byte5(high_byte(value))
        energy_bank.sendCanMessage()

    def bank_safey_threshold_read_event(self):
        energy_bank.ccs = 0x40
        energy_bank.subIndex = OD.S_SAFETY_THRESHOLD_STATE_OF_CHARGE
        value = float(self.energy_bank_safey_threshold_entry.get())
        value = int(value) & 0xffff
        energy_bank.set_data_byte4(low_byte(value))
        energy_bank.set_data_byte5(high_byte(value))
        energy_bank.sendCanMessage()

    def bank_charge_read_event(self):
        energy_bank.ccs = 0x40
        energy_bank.subIndex = OD.S_STATE_OF_CHARGE_OF_ENERGY_BANK
        energy_bank.sendCanMessage()

    def bank_health_read_event(self):
        energy_bank.ccs = 0x40
        energy_bank.subIndex = OD.S_STATE_OF_HEALTH_OF_ENERGY_BANK
        energy_bank.sendCanMessage()

    def bank_remaining_energy_read_event(self):
        energy_bank.ccs = 0x40
        energy_bank.subIndex = OD.S_REMAINING_ENERGY_TO_MIN_SOC_AT_ENERGY_BANK
        energy_bank.sendCanMessage()

    ### TEMPERATURES
    def temperature_max_allowed_event(self):
        temperature.ccs = 0x2f
        temperature.subIndex = OD.S_DPMU_TEMPERATURE_MAX_LIMIT
        value = int(app.temperature_max_entry.get())
        temperature.set_data_byte4(value)
        temperature.sendCanMessage()

    def temperature_max_allowed_read_event(self):
        temperature.ccs = 0x40
        temperature.subIndex = OD.S_DPMU_TEMPERATURE_MAX_LIMIT
        temperature.sendCanMessage()

    def temperature_highest_read_event(self):
        temperature.ccs = 0x40
        temperature.subIndex = OD.S_TEMPERATURE_MEASURED_AT_DPMU_HOTTEST_POINT
        temperature.sendCanMessage()

    def temperature_high_limit_event(self):
        temperature.ccs = 0x2f
        temperature.subIndex = OD.S_DPMU_TEMPERATURE_HIGH_LIMIT
        value = int(app.temperature_high_entry.get())
        temperature.set_data_byte4(value)
        temperature.sendCanMessage()

    def temperature_high_limit_read_event(self):
        temperature.ccs = 0x40
        temperature.subIndex = OD.S_DPMU_TEMPERATURE_HIGH_LIMIT
        temperature.sendCanMessage()

    def temperature_energy_bank_read_event(self):
        temperature.ccs = 0x40
        temperature.subIndex = OD.S_TEMPERATURE_PWR_BANK
        temperature.sendCanMessage()

    def temperature_mezzanine_read_event(self):
        temperature.ccs = 0x40
        temperature.subIndex = OD.S_TEMPERATURE_MEZZANINE
        temperature.sendCanMessage()

    def temperature_main_read_event(self):
        temperature.ccs = 0x40
        temperature.subIndex = OD.S_TEMPERATURE_MAIN
        temperature.sendCanMessage()

    def temperature_dsp_card_read_event(self):
        temperature.ccs = 0x40
        temperature.subIndex = OD.S_TEMPERATURE_BASE
        temperature.sendCanMessage()

    def temperature_stack_read_event(self):
        energy_bank.ccs = 0x40
        energy_bank.subIndex = OD.S_STACK_TEMPERATURE
        energy_bank.sendCanMessage()


    ### DEBUG LOG
    def debuglog_state_event(self):
        debuglog.ccs = 0x2f
        debuglog.set_data_byte1( low_byte(OD.I_DEBUG_LOG))
        debuglog.set_data_byte2(high_byte(OD.I_DEBUG_LOG))
        debuglog.subIndex = OD.S_DEBUG_LOG_STATE
        var = app.debuglog_checkbox_state.get()
        print("cget()", app.debuglog_checkbox_state.cget("variable"))
        print("var", var)
        if(var == "on"):
            app.debuglog_checkbox_state.configure(fg_color="green")
            app.debuglog_checkbox_state.configure(text="RUNNING")
            debuglog.set_data_byte4(1)
        else:
            app.debuglog_checkbox_state.configure(fg_color="red")
            app.debuglog_checkbox_state.configure(text="OFF")
            debuglog.set_data_byte4(0)
        debuglog.sendCanMessage()
    def debuglog_read_state_event(self):
        debuglog.ccs = 0x40
        debuglog.set_data_byte1( low_byte(OD.I_DEBUG_LOG))
        debuglog.set_data_byte2(high_byte(OD.I_DEBUG_LOG))
        debuglog.set_data_byte3(OD.S_DEBUG_LOG_STATE)
        debuglog.subIndex = OD.S_DEBUG_LOG_STATE
        debuglog.sendCanMessage()
    def debuglog_read_event(self):
        # debuglog.ccs = 0x40
        debuglog.ccs = 0xA0
        debuglog.set_data_byte1( low_byte(OD.I_DEBUG_LOG))
        debuglog.set_data_byte2(high_byte(OD.I_DEBUG_LOG))
        debuglog.subIndex = OD.S_DEBUG_LOG_READ
        debuglog.set_data_byte4(4)
        debuglog.set_data_byte5(4)
        debuglog.sendCanMessage()
    def debuglog_reset_event(self):
        debuglog.ccs = 0x2f
        debuglog.set_data_byte1( low_byte(OD.I_DEBUG_LOG))
        debuglog.set_data_byte2(high_byte(OD.I_DEBUG_LOG))
        debuglog.subIndex = OD.S_DEBUG_LOG_RESET
        debuglog.sendCanMessage()


    ### CAN LOG
    def canlog_read_event(self):
        canlog.ccs = 0xA0
        canlog.set_data_byte1( low_byte(OD.I_CAN_LOG))
        canlog.set_data_byte2(high_byte(OD.I_CAN_LOG))
        canlog.subIndex = OD.S_CAN_LOG_READ
        canlog.set_data_byte4(4)
        canlog.set_data_byte5(4)
        canlog.sendCanMessage()
    def canlog_reset_event(self):
        canlog.ccs = 0x2f
        canlog.set_data_byte1( low_byte(OD.I_CAN_LOG))
        canlog.set_data_byte2(high_byte(OD.I_CAN_LOG))
        canlog.subIndex = OD.S_CAN_LOG_RESET
        canlog.sendCanMessage()


    ### DATE AND TIME
    def time_set_event(self):
        time.ccs = 0x23
        #value = int(self.time_entry.get())
        value = int( timer.time() )
        time.set_data_byte4((value    ) & 0xff)
        time.set_data_byte5((value>> 8) & 0xff)
        time.set_data_byte6((value>>16) & 0xff)
        time.set_data_byte7((value>>24) & 0xff)
        time.sendCanMessage()

    def time_read_event(self):
        time.ccs = 0x40
        time.set_data_byte4(0)
        time.set_data_byte5(0)
        time.set_data_byte6(0)
        time.set_data_byte7(0)
        time.sendCanMessage()


    ### APPEARANCE
    def open_input_dialog_event(self):
        dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="CTkInputDialog")
        print("CTkInputDialog:", dialog.get_input())

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)


    ### DPMU STATES
    def state_off_event(self):
        print("state_button FORCE FAULT click")
        state.ccs=0x2F
        state.setSubIndex(OD.S_DPMU_OPERATION_REQUEST_STATE)
        state.set_data_byte4(15) # state_fault
        state.sendCanMessage()

    def state_initialize_event(self):
        print("state_button INIT click")        
        self.time_set_event()
        timer.sleep(10/1000)
        self.current_available_power_budget_input_event()
        timer.sleep(10/1000)
        self.current_max_load_current_event()
        timer.sleep(10/1000)
        self.current_max_ess_current_event()
        timer.sleep(10/1000)
        self.cell_max_volt_event()
        timer.sleep(10/1000)
        self.cell_min_volt_event()
        timer.sleep(10/1000)
        self.bank_max_volt_event()
        timer.sleep(10/1000)
        self.bank_const_volt_event()
        timer.sleep(10/1000)
        self.bank_min_volt_event()
        timer.sleep(10/1000)
        self.bank_trickle_charge_event()
        timer.sleep(10/1000)
        self.bank_safey_threshold_event()
        timer.sleep(10/1000)
        self.voltages_max_allowed_dc_bus_voltage_event()
        timer.sleep(10/1000)
        self.voltages_target_voltage_event()
        timer.sleep(10/1000)
        self.voltages_min_allowed_dc_bus_voltage_event()
        timer.sleep(10/1000)
        self.voltages_short_circuit_voltage_event()
        timer.sleep(10/1000)
        self.temperature_max_allowed_event()
        timer.sleep(10/1000)        
        self.temperature_high_limit_event()
        timer.sleep(10/1000)
        dpmu_type_cboBox = app.combobox_DPMU_Type.get() 
        self.set_DPMU_Type_event( dpmu_type_cboBox )
        timer.sleep(10/1000)
        state.ccs=0x2F
        state.setSubIndex(OD.S_DPMU_OPERATION_REQUEST_STATE)
        state.set_data_byte4(1) # state_initialize
        state.sendCanMessage()

    def state_charge_event(self):
        print("state_button CHARGE click")
        state.ccs=0x2F
        state.setSubIndex(OD.S_DPMU_OPERATION_REQUEST_STATE)
        state.set_data_byte4(4) # state_charge
        state.sendCanMessage()

    def state_idle_event(self):
        print("state_button IDLE click")
        state.ccs=0x2F
        state.setSubIndex(OD.S_DPMU_OPERATION_REQUEST_STATE)
        state.set_data_byte4(0) #state_idle
        state.sendCanMessage()

    def state_regulate_event(self):
        print("state_button REGULATE click")
        state.ccs=0x2F
        state.setSubIndex(OD.S_DPMU_OPERATION_REQUEST_STATE)
        state.set_data_byte4(12) # state_regulate
        state.sendCanMessage()

    def state_read_state_event(self):
        
        #print("state_button READ click")
        if( canOD.sdoBlockTransferOngoing == 0 ): 
            state.ccs=0x40
            state.setSubIndex(OD.S_DPMU_OPERATION_CURRENT_STATE)
            state.set_data_byte4(0)
            state.sendCanMessage()
            
            self.switches_inrush_read_event()
            self.switches_load_read_event()
            self.switches_input_read_event()
            self.switches_share_read_event()

            match self.dpmuCurrentState:                
                case [ DPMUState.ChargeInit, DPMUState.Charge, DPMUState.ChargeRamp, DPMUState.TrickleCharge, 
                      DPMUState.TrickleChargeDelay, DPMUState.TrickleChargeInit, DPMUState.BalancingInit, DPMUState.Balancing ]:
                    self.energy_cell_charge_read_event()
                    self.bank_charge_read_event()
                    self.bank_remaining_energy_read_event()    
                    self.stateReadUpdateTime = 1000
                case [ DPMUState.RegulateInit, DPMUState.Regulate, DPMUState.RegulateVoltageInit, DPMUState.RegulateVoltage ]:
                    self.energy_cell_charge_read_event()
                    self.bank_charge_read_event()
                    self.bank_remaining_energy_read_event()    
                    self.stateReadUpdateTime = 200
                case [ DPMUState.SoftstartInit, DPMUState.Softstart ]:
                    self.stateReadUpdateTime = 250
                case [ DPMUState.Fault, DPMUState.FaultDelay ]:
                    self.stateReadUpdateTime = 250                    
                case _:
                    self.energy_cell_charge_read_event()
                    self.bank_charge_read_event()
                    timer.sleep(10/1000)
                    self.read_power_dc_vstore_event()
                    timer.sleep(10/1000)
                    self.read_power_input_current_event()
                    timer.sleep(10/1000)
                    self.read_power_dc_voltage_event()
                    timer.sleep(10/1000)
                    self.read_power_load_current_event()
                    timer.sleep(10/1000)
                    self.read_power_supercap_current_event()                    
                    timer.sleep(10/1000)
                    self.bank_health_read_event()  
                    timer.sleep(10/1000)
                    self.bank_remaining_energy_read_event()   
                    timer.sleep(10/1000)
                    self.temperature_energy_bank_read_event()                 
                    timer.sleep(10/1000)
                    self.temperature_stack_read_event()
                    timer.sleep(10/1000)
                    self.temperature_mezzanine_read_event()
                    timer.sleep(10/1000)
                    self.temperature_main_read_event()
                    timer.sleep(10/1000)
                    self.temperature_dsp_card_read_event()
                    timer.sleep(10/1000)
                    self.temperature_highest_read_event()
                    self.stateReadUpdateTime = 2500
                    
            self.state_read_button.after(self.stateReadUpdateTime, self.state_read_state_event)

    def state_reboot_event(self):
        print("state_button REBOOT click")
        reboot.set_data_byte4(0x5A)
        reboot.sendCanMessage()

    ### NMT
    def nmt_reset_application_event(self):
        print("nmt_reset_application_button click")
        # nmt.set_data_byte4(0x81) # Reset node
        # nmt = canOD(id=0, ccs=0x0C, indexHigh=0x81, indexLow=0x01) # FIXME NOT IN OD
        # canopen_DPMU_A.write_raw(0, [0x81,1], flag=0, dlc=None)
        canopen_DPMU_A.write_raw(0, [0x81,nmtNodeId], flag=0, dlc=None)

    def nmt_reset_communication_event(self):
        print("nmt_reset_communication_button click")
        # nmt.set_data_byte4(0x82) #  Reset communication
        # frame = [0,0,0,0]
        # canopen_DPMU_A.write_raw(0, [0x82,1], flag=0, dlc=None)
        canopen_DPMU_A.write_raw(0, [0x82,nmtNodeId], flag=0, dlc=None)

    def nmt_pre_operational_event(self):
        print("nmt_pre_operational_button click")
        # nmt.set_data_byte4(0x80) # Enter Pre-operational
        # nmt = canOD(id=0, ccs=0x0C, indexHigh=0x80, indexLow=0x01) # FIXME NOT IN OD
        # canopen_DPMU_A.write_raw(0, [0x80,1], flag=0, dlc=None)
        canopen_DPMU_A.write_raw(0, [0x80,nmtNodeId], flag=0, dlc=None)

    def nmt_operational_event(self):
        print("nmt_operational_button click")
        # nmt.set_data_byte4(0x01) # Enter Operational
        # nmt = canOD(id=0, ccs=0x0C, indexHigh=0x01, indexLow=0x01) # FIXME NOT IN OD
        # canopen_DPMU_A.write_raw(0, [0x01,1], flag=0, dlc=None)
        canopen_DPMU_A.write_raw(0, [0x01,nmtNodeId], flag=0, dlc=None)
        
    def nmt_stop_event(self):
        print("nmt_stop_button click")
        # nmt.set_data_byte4(0x02) #  Enter Stop
        # nmt = canOD(id=0, ccs=0x0C, indexHigh=0x02, indexLow=0x01) # FIXME NOT IN OD
        # canopen_DPMU_A.write_raw(0, [0x02,1], flag=0, dlc=None)
        canopen_DPMU_A.write_raw(0, [0x02,nmtNodeId], flag=0, dlc=None)


    ### HEARTBEAT
    def heartbeat_event(self):
        value = int(self.heartbeat_entry.get())
        # print("heart beat value ", value)
        heartbeat.set_data_byte4(low_byte(value))
        heartbeat.set_data_byte5(high_byte(value))
        heartbeat.sendCanMessage()

    def clear_log_box_event(self):
        app.textbox.configure(state="normal") #writable
        app.textbox.delete(0.0 ,customtkinter.END)
        self.textbox.insert("0.0", "START\r\n")
        app.textbox.configure(state="disable")


    ### SWITCHES - SET

    def switches_inrush_event(self):
        switch_inrush.ccs = 0x2F

        if app.switches_inrush_state:
            # app.switches_inrush_state = False
            switch_inrush.set_data_byte4(0)
            # self.switches_inrush.progress_color="red"
        else:
            # app.switches_inrush_state = True
            switch_inrush.set_data_byte4(1)
            # self.switches_inrush.progress_color="green"
        switch_inrush.sendCanMessage()
        self.switches_inrush_read_event()
        
    def switches_load_event(self):
        switch_load.ccs = 0x2F

        if app.switch_load_state:
            # switch_load_state = False
            switch_load.set_data_byte4(0)
            #self.switches_load_event.progress_color="red"
        else:
            # switch_load_state = True
            switch_load.set_data_byte4(1)
            #self.switches_load_event.progress_color="green"
        switch_load.sendCanMessage()
        self.switches_load_read_event()
        
    def switches_share_event(self):
        switch_share.ccs = 0x2F

        if app.switch_share_state:
            # switch_share_state = False
            switch_share.set_data_byte4(0)
            #self.switches_share_event.progress_color="red"
        else:
            # switch_share_state = True
            switch_share.set_data_byte4(1)
            #self.switches_share_event.progress_color="green"
        switch_share.sendCanMessage()
        self.switches_share_read_event()
        
    def switches_input_event(self):
        switch_input.ccs = 0x2F

        if app.switch_input_state:
            # switch_input_state = False
            switch_input.set_data_byte4(0)
            self.switches_input.progress_color="red"
        else:
            # switch_input_state = True
            switch_input.set_data_byte4(1)
            self.switches_input.progress_color="green"

        switch_input.sendCanMessage()
        self.switches_input_read_event()

    ### SWITCHES - READ
    def switches_inrush_read_event(self):
        switch_inrush.ccs = 0x40
        switch_inrush.sendCanMessage()

    def switches_load_read_event(self):
        switch_load.ccs = 0x40
        switch_load.sendCanMessage()

    def switches_share_read_event(self):
        switch_share.ccs = 0x40
        switch_share.sendCanMessage()

    def switches_input_read_event(self):
        switch_input.ccs = 0x40
        switch_input.sendCanMessage()


def high_byte(x):
    return (x>>8)&0x00ff

def low_byte(x):
    return (x)&0x00ff

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

        app.textbox.configure(state="normal") #writable
        # app.textbox.insert(customtkinter.END, "ID {:03x}".format(msg.id) + " CCS {:02x}".format(msg.data[0]) + " I {:04x}".format((msg.data[2] << 8) | msg.data[1]) + " S {:02x}".format(msg.data[3]) \
                            # + " : {:02x}".format(msg.data[4]) + " {:02x}".format(msg.data[5]) + " {:02x}".format(msg.data[6]) + " {:02x}".format(msg.data[7]) + "\r\n")
        app.textbox.insert(customtkinter.END, string)
        app.textbox.configure(state="disable")
        app.textbox.see(customtkinter.END)
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

        app.textbox.configure(state="normal") #writable
        # app.textbox.insert(customtkinter.END, "ID {:03x}".format(msg.id) + " CCS {:02x}".format(msg.data[0]) + " I {:04x}".format((msg.data[2] << 8) | msg.data[1]) + " S {:02x}".format(msg.data[3]) \
                            # + " : {:02x}".format(msg.data[4]) + " {:02x}".format(msg.data[5]) + " {:02x}".format(msg.data[6]) + " {:02x}".format(msg.data[7]) + "\r\n")
        app.textbox.insert(customtkinter.END, string)
        app.textbox.configure(state="disable")
        app.textbox.see(customtkinter.END)
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
                # if msg.flags == 0x2f:
                # try:
                    # app.textbox.configure(state="normal") #writable
                    # app.textbox.insert(customtkinter.END, "ID {:03x}".format(msg.id) + " CCS {:02x}".format(msg.data[0]) + " I {:04x}".format((msg.data[2] << 8) | msg.data[1]) + " S {:02x}".format(msg.data[3]) \
                                        # + " : {:02x}".format(msg.data[4]) + " {:02x}".format(msg.data[5]) + " {:02x}".format(msg.data[6]) + " {:02x}".format(msg.data[7]) + "\r\n")
                    # app.textbox.configure(state="disable")
                    # app.textbox.see(customtkinter.END)
                # except Exception as err:
                    # print(f"Unexpected {err=}, {type(err)=}")
                if msg.flags == canlib.MessageFlag.ERROR_FRAME :
                    pass
                else :
                    # print_can_message(msg)
                    match msg.id & 0x780 :
                        # case 0x700:
                            # match msg.data[0]:
                            #     case 0:
                            #         print("Heartbeat BOOT_UP " + print_can_message(msg))
                            #     case 4:
                            #         print("Heartbeat STOPPED " + print_can_message(msg))
                            #     case 5:
                            #         print("Heartbeat OPERATIONAL ")
                            #     case 127:
                            #         print("Heartbeat PRE_OPERATIONAL ")
                            #     case _:
                            #         print("Heartbeat ERROR - UNKNOWN STATE ")
                        # case 0x080:
                        #     print("PDO 080 " + print_can_message_raw(msg))#format(msg))
                        # case 0x180:
                        #     print("PDO 180 " + print_can_message(msg))#format(msg))
                        # case 0x280:
                        #     print("PDO 280 " + print_can_message(msg))#format(msg))
                        # case 0x380:
                        #     print("PDO 380 " + print_can_message(msg))#format(msg))
                        # case 0x480:
                        #     print("PDO 480 " + print_can_message(msg))#format(msg))
                        # case 0x330:
                        #     print("NMT answer " + print_can_message(msg))#format(msg))
                        #case 0x600:
                            #print("SDO 600 " + print_can_message(msg))#msg_as_string(msg))
                        case 0x580:
                            if 1 == canOD.sdoBlockTransferOngoing:
                                print("SDO 580 " + print_can_message_raw(msg))
                            #else:
                                #print("SDO 580 " + print_can_message(msg))#msg_as_string(msg))
                            can_input_event(msg)
                        # case 0x000:
                            # print("SDO 000 " + msg_as_string(msg))
                        # case _:
                        #     #print(msg)
                        #     print(print_can_message(msg))
                            # app.textbox.configure(state="normal") #writable
                            # app.textbox.insert(customtkinter.END, "  ERROR\r\n")
                            # app.textbox.configure(state="disable")
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
        debuglog.writeDataToLogFile(data)
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
                #debuglog.writeDataToLogFile(data)
                #debuglog.closeDPMULogFile()
                
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
            debuglog.closeDPMULogFile()

def can_input_event(msg):
    data = msg.data
    # print_can_message(msg)
    # print(data)
    # print("sdoBlock ", canOD.sdoBlock)

    index = (data[2] << 8) | data[1]
    # print("index {:04x}".format(index))
    subIndex = data[3]
    # print("subIndex {:02x}".format(subIndex))
    value = data[4]
    #value16 = (data[4]<<8) + data[5]
    value16 = (data[5]<<8) + data[4]
    # print("value   ", value)
    # print("value16 ", value16)
    # print("data[0] ", hex(data[0]))

    if 0 != canOD.sdoBlock :
        sdo_block_transfer(data)
    else:
        if 0x40 == (data[0] & 0xE0):
            if index == OD.I_DC_BUS_VOLTAGE:
                match subIndex:
                    case OD.S_MAX_ALLOWED_DC_BUS_VOLTAGE:
                        app.voltages_max_allowed_dc_bus_voltage_entry.delete(0,customtkinter.END)
                        app.voltages_max_allowed_dc_bus_voltage_entry.insert(0,value)
                        placeholder_text = app.voltages_max_allowed_dc_bus_voltage_entry.get()
                        print("placeholder_text ",placeholder_text)
                    case OD.S_TARGET_VOLTAGE_AT_DC_BUS:
                        app.voltages_target_voltage_entry.delete(0,customtkinter.END)
                        app.voltages_target_voltage_entry.insert(0,value)
                        placeholder_text = app.voltages_target_voltage_entry.get()
                        print("placeholder_text ",placeholder_text)
                    case OD.S_MIN_ALLOWED_DC_BUS_VOLTAGE:
                        app.voltages_min_allowed_dc_bus_voltage_entry.delete(0,customtkinter.END)
                        app.voltages_min_allowed_dc_bus_voltage_entry.insert(0,value)
                        placeholder_text = app.voltages_min_allowed_dc_bus_voltage_entry.get()
                        print("placeholder_text ",placeholder_text)
                    case OD.S_VDC_BUS_SHORT_CIRCUIT_LIMIT:
                        app.voltages_dc_bus_short_circuit_limit_entry.delete(0,customtkinter.END)
                        app.voltages_dc_bus_short_circuit_limit_entry.insert(0,value)
                        placeholder_text = app.voltages_dc_bus_short_circuit_limit_entry.get()
                        print("placeholder_text ",placeholder_text)

            if index == OD.I_POWER_BUDGET_DC_INPUT:
                match subIndex:
                    case OD.S_AVAILABLE_POWER_BUDGET_DC_INPUT:
                        app.power_pudget_dc_input_available_power_budget_input_event_entry.delete(0,customtkinter.END)
                        app.power_pudget_dc_input_available_power_budget_input_event_entry.insert(0,value16)
                        placeholder_text = app.power_pudget_dc_input_available_power_budget_input_event_entry.get()
                        print("placeholder_text ",placeholder_text)
                    case OD.S_MAX_CURRENT_POWER_LINE_A:
                        app.power_pudget_dc_input_line_A_entry.delete(0,customtkinter.END)
                        app.power_pudget_dc_input_line_A_entry.insert(0,value16)
                        placeholder_text = app.power_pudget_dc_input_line_A_entry.get()
                        print("placeholder_text ",placeholder_text)
                    case OD.S_MAX_CURRENT_POWER_LINE_B:
                        app.power_pudget_dc_input_line_B_entry.delete(0,customtkinter.END)
                        app.power_pudget_dc_input_line_B_entry.insert(0,value16)
                        placeholder_text = app.power_pudget_dc_input_line_B_entry.get()
                        print("placeholder_text ",placeholder_text)

            if index == OD.I_MAXIMUM_ALLOWED_LOAD_POWER:
                app.current_max_load_current_entry.delete(0,customtkinter.END)
                app.current_max_load_current_entry.insert(0,value16)
                placeholder_text = app.current_max_load_current_entry.get()
                print("placeholder_text ",placeholder_text)

            if index == OD.I_ESS_CURRENT:
                #Twos complement
                if (value & (1 << (7))) != 0: # if sign bit is set e.g., 8bit: 128-255
                    value = value - (1 << 8)        # compute negative value
                value = float(value) / 16.0
                app.current_max_ess_current_entry.delete(0,customtkinter.END)
                app.current_max_ess_current_entry.insert(0,"%.2f" % value)
                placeholder_text = app.current_max_ess_current_entry.get()                               
                print("ess_current ",placeholder_text)
                app.read_power_supercap_current_entry.delete(0,customtkinter.END)
                app.read_power_supercap_current_entry.insert(0, "%.2f" % value)

            if index == OD.I_READ_POWER:
                print(int(app.power_pudget_dc_input_available_power_budget_input_event_entry.get()))
                match subIndex:
                    case OD.S_READ_VOLTAGE_AT_DC_BUS:
                        print("S_READ_VOLTAGE_AT_DC_BUS")
                        print("dc bus over/under voltage {:02x}".format(value))
                        app.read_power_dc_voltage_entry.delete(0, customtkinter.END)
                        app.read_power_dc_voltage_entry.insert(0, value)
                    case OD.S_POWER_FROM_DC_INPUT:                        
                        print("S_POWER_FROM_DC_INPUT")
                        if value16 > int(app.power_pudget_dc_input_available_power_budget_input_event_entry.get()):                            
                            # app.read_power_input_power.configure(state="enabled")
                            # app.read_power_input_power.select()
                            print("dc input overcurrent")
                        else:
                            # app.read_power_input_power.configure(state="disabled")
                            # app.read_power_input_power.deselect()
                            print("no dc input overcurrent")
                        try:
                            dc_bus_voltage = app.read_power_dc_voltage_entry.get()
                            if( dc_bus_voltage == "0"): 
                                app.read_power_input_current_entry.delete(0, customtkinter.END)
                                app.read_power_input_current_entry.insert(0, 0)
                            else:
                                inputCurrent = float( value16 ) / float( dc_bus_voltage )
                                app.read_power_input_current_entry.delete(0, customtkinter.END)
                                app.read_power_input_current_entry.insert(0, "{:.1f}".format(inputCurrent) )
                        except:
                            app.read_power_input_current_entry.delete(0, customtkinter.END)
                            app.read_power_input_current_entry.insert(0, "Invalid DC BUS VOLTAGE")
                            
                    case OD.S_READ_LOAD_CURRENT:
                        print("S_READ_LOAD_CURRENT")
                        if (value & (1 << (7))) != 0: # if sign bit is set e.g., 8bit: 128-255
                            value = value - (1 << 8)        # compute negative value
                        loadCurrent = float(value) / 16.0
                        app.read_power_load_current_entry.delete(0, customtkinter.END)
                        app.read_power_load_current_entry.insert(0, "{:.1f}".format(loadCurrent) )
                        
                    case OD.S_POWER_CONSUMED_BY_LOAD:
                        print("S_POWER_CONSUMED_BY_LOAD")
                        if value > int(app.current_max_load_current_entry.get()):
                            app.read_power_input_power.configure(state="enabled")
                            app.read_power_input_power.select()
                            print("output overload")
                        else:
                            app.read_power_input_power.configure(state="disabled")
                            app.read_power_input_power.deselect()
                            print("no output overload")

            if index == OD.I_ENERGY_CELL_SUMMARY:
                match subIndex:
                    case OD.S_MAX_VOLTAGE_ENERGY_CELL:
                        value = float(value) / 16
                        app.energy_cell_max_volt_entry.delete(0,customtkinter.END)
                        app.energy_cell_max_volt_entry.insert(0,value)
                        placeholder_text = app.energy_cell_max_volt_entry.get()
                        print("placeholder_text ",placeholder_text)
                    case OD.S_MIN_VOLTAGE_ENERGY_CELL:
                        value = float(value) / 16
                        app.energy_cell_min_volt_entry.delete(0,customtkinter.END)
                        app.energy_cell_min_volt_entry.insert(0,value)
                        placeholder_text = app.energy_cell_min_volt_entry.get()
                        print("placeholder_text ",placeholder_text)
                    case _:
                        if (subIndex >= OD.S_STATE_OF_CHARGE_OF_ENERGY_CELL_01) and (subIndex <= OD.S_STATE_OF_CHARGE_OF_ENERGY_CELL_30):
                            app.cellVoltage[subIndex].delete(0, customtkinter.END)
                            app.cellVoltage[subIndex].insert(0, "{:.2f}".format( float(value)/16 ) )
                        
            if index == OD.I_DPMU_STATE:                
                app.dpmuCurrentState = msg.data[4]
                # if app.dpmuCurrentState == DPMUState.Idle:
                if app.dpmuCurrentState == 0:
                    app.state_idle_button.configure(fg_color="blue")
                    #self.switches_load_event.progress_color="red"
                else:
                    app.state_idle_button.configure(fg_color="slategrey")
                if app.dpmuCurrentState in [DPMUState.Initialize , DPMUState.SoftstartInitDefault, DPMUState.SoftstartInitRedundant, DPMUState.Softstart ]:
                    app.state_initialize_button.configure(fg_color="blue")
                else:
                    app.state_initialize_button.configure(fg_color="slategrey")

                # if  app.dpmuCurrentState in [DPMUState.TrickleChargeInit, DPMUState.TrickleChargeDelay, DPMUState.TrickleCharge]:
                if  app.dpmuCurrentState in [4, 5, 6]:
                    app.chargingFlag = True
                    app.state_charge_button.configure(fg_color="blue")
                # elif app.dpmuCurrentState in [DPMUState.ChargeInit, DPMUState.Charge, DPMUState.ChargeRamp, DPMUState.ChargeStop]:
                elif app.dpmuCurrentState in [7, 8, 9, 22]:
                    app.chargingFlag = True
                    app.state_charge_button.configure(fg_color="red")
                # elif app.dpmuCurrentState in [ int(DPMUState.ChargeConstantVoltageInit), int(DPMUState.ChargeConstantVoltage)]:
                elif app.dpmuCurrentState in [10, 11]:    
                    app.chargingFlag = True
                    app.state_charge_button.configure(fg_color="yellow")
                else:
                    app.state_charge_button.configure(fg_color="slategrey")
                
                # if  app.dpmuCurrentState in [DPMUState.RegulateVoltageInit, DPMUState.RegulateVoltage]:
                if  app.dpmuCurrentState in [140, 141]:    
                    app.state_regulate_button.configure(fg_color="red")
                # elif app.dpmuCurrentState in [DPMUState.RegulateInit, DPMUState.Regulate, DPMUState.RegulateStop]:
                elif app.dpmuCurrentState in [ 12, 13, 14]:
                    app.state_regulate_button.configure(fg_color="blue")
                else:
                    app.state_regulate_button.configure(fg_color="slategrey")
                
                if app.switches_inrush_state  == False and  app.switch_input_state == True and  app.switch_load_state == True and app.switch_share_state == True:
                    app.state_initialize_button.configure(fg_color="green")
                else:
                    app.state_initialize_button.configure(fg_color="slategrey")
                #print("DPMU state:", msg.data[4])

            if index == OD.I_ENERGY_BANK_SUMMARY:
                match subIndex:
                    case OD.S_MAX_VOLTAGE_APPLIED_TO_ENERGY_BANK:
                        app.energy_bank_max_volt_entry.delete(0,customtkinter.END)
                        app.energy_bank_max_volt_entry.insert(0,value)
                        placeholder_text = app.energy_bank_max_volt_entry.get()
                        print("MAX_VOLTAGE_APPLIED_TO_STORAGE_BANK: ",placeholder_text)
                    case OD.S_MIN_VOLTAGE_APPLIED_TO_ENERGY_BANK:
                        value = float(value) / 2
                        app.energy_bank_min_volt_entry.delete(0,customtkinter.END)
                        app.energy_bank_min_volt_entry.insert(0,value)
                        placeholder_text = app.energy_bank_min_volt_entry.get()
                        print("MIN_ALLOWED_STATE_OF_CHARGE_OF_ENERGY_BANK: ",placeholder_text)
                    case OD.S_SAFETY_THRESHOLD_STATE_OF_CHARGE:
                        app.energy_bank_safey_threshold_entry.delete(0,customtkinter.END)
                        app.energy_bank_safey_threshold_entry.insert(0,value16)
                        placeholder_text = app.energy_bank_safey_threshold_entry.get()
                        print("SAFETY_THRESHOLD_STATE_OF_CHARGE: ",placeholder_text)
                    case OD.S_STATE_OF_CHARGE_OF_ENERGY_BANK:
                        print("BANK PERCENT %d" % value)
                        value = value / 2;
                        app.state_of_charge_entry.delete(0, customtkinter.END)
                        app.state_of_charge_entry.insert(0, value)
                        currentVStoreRatio = math.sqrt( float( value ) / 100.0 )
                        maxVoltageEnergyBank = float ( app.energy_bank_max_volt_entry.get() )
                        calcSupercapVoltage = ( ( 0.8733 * maxVoltageEnergyBank ) *  currentVStoreRatio  )
                        app.read_power_dc_vstore_entry.delete(0, customtkinter.END)
                        app.read_power_dc_vstore_entry.insert(0, ("%.1f" % calcSupercapVoltage) )
                        # if int( app.energy_bank_max_volt_entry.get() ) > 0:
                        #     progressBarValue = value/int(app.energy_bank_max_volt_entry.get())
                        # else:
                        #     app.cell_progressbar_charge.set(0.01)
                        #     app.cell_progressbar_charge.configure(progress_color="DeepSkyBlue3")
                        #     pass
                        progressBarValue = currentVStoreRatio
                        app.cell_progressbar_charge.set( progressBarValue )#value/int(app.energy_bank_max_volt_entry.get()))
                        app.cell_progressbar_charge.configure(progress_color="DeepSkyBlue3")
                        if calcSupercapVoltage > int(app.energy_bank_max_volt_entry.get()):
                            app.cell_progressbar_charge.configure(progress_color="red")
                        if calcSupercapVoltage < int(app.energy_bank_safey_threshold_entry.get()):
                            app.cell_progressbar_charge.configure(progress_color="yellow")
                        if calcSupercapVoltage < int(app.energy_bank_min_volt_entry.get()):
                            app.cell_progressbar_charge.configure(progress_color="red")
                    case OD.S_STATE_OF_HEALTH_OF_ENERGY_BANK:
                        #app.cell_progressbar_health.set(value)
                        app.state_of_health_entry.delete(0, customtkinter.END)
                        app.state_of_health_entry.insert(0, "%.1f" % (value/2) )
                    case OD.S_REMAINING_ENERGY_TO_MIN_SOC_AT_ENERGY_BANK:
                        print("S_REMAINING_ENERGY_TO_MIN_SOC_AT_ENERGY_BANK %d" % float(value16) )
                        app.state_of_remaining_energy_entry.delete(0, customtkinter.END)
                        app.state_of_remaining_energy_entry.insert(0, "%d" % ( float(value16) ) )
                    case OD.S_STACK_TEMPERATURE:
                        app.temperature_stack_entry.delete(0,customtkinter.END)
                        app.temperature_stack_entry.insert(0,value)
                        placeholder_text = app.temperature_stack_entry.get()
                        print("STACK_TEMPERATURE: ",placeholder_text)
                    case OD.S_CONSTANT_VOLTAGE_THRESHOLD:
                        app.energy_bank_const_volt_threshold_entry.delete(0,customtkinter.END)
                        app.energy_bank_const_volt_threshold_entry.insert(0,value)
                        placeholder_text = app.energy_bank_const_volt_threshold_entry.get()
                        print("CONSTANT_VOLTAGE_THRESHOLD: ",placeholder_text)
                    case OD.S_PRECONDITIONAL_THRESHOLD:
                        app.energy_bank_trickle_charge_threshold_entry.delete(0,customtkinter.END)
                        app.energy_bank_trickle_charge_threshold_entry.insert(0,value)
                        placeholder_text = app.energy_bank_trickle_charge_threshold_entry.get()
                        print("PRECONDITIONAL_THRESHOLD: ",placeholder_text)
                    case _:
                        print("ERROR: out of index - I_ENERGY_BANK_SUMMAR")

            if index == OD.I_TEMPERATURE:
                match subIndex:
                    case OD.S_DPMU_TEMPERATURE_MAX_LIMIT:
                        app.temperature_max_entry.delete(0,customtkinter.END)
                        app.temperature_max_entry.insert(0,value)
                        placeholder_text = app.temperature_max_entry.get()
                        print("Max allowed temperature: ",placeholder_text)
                    case OD.S_TEMPERATURE_MEASURED_AT_DPMU_HOTTEST_POINT:
                        ## clear old settings

                        temp_max = int(app.temperature_max_entry.get())
                        temp_highest_measured = int(data[4])

                        # update new settings
                        # print("max: " + format(temp_max))
                        # print("hig: " + format(temp_highest_measured))
                        print("Temperature at hottest point: ", value )
                        if value >= int(app.temperature_max_entry.get()):
                            app.temperature_sub_status.configure(bg_color="red", text="ALARM")
                        else:
                            if value >= int(app.temperature_high_entry.get()):
                                app.temperature_sub_status.configure(bg_color="yellow", text="HIGH")
                            else:
                                app.temperature_sub_status.configure(bg_color="green", text="OK")
                    case OD.S_DPMU_TEMPERATURE_HIGH_LIMIT:
                        app.temperature_high_entry.delete(0,customtkinter.END)
                        app.temperature_high_entry.insert(0,value)
                        placeholder_text = app.temperature_high_entry.get()
                        print("High temperature limit: ",placeholder_text)
                    case OD.S_TEMPERATURE_BASE:
                        app.temperature_dsp_base_entry.delete(0,customtkinter.END)
                        app.temperature_dsp_base_entry.insert(0,value)
                        placeholder_text = app.temperature_dsp_base_entry.get()
                        print("Temp DSP Base: ",placeholder_text)
                    case OD.S_TEMPERATURE_MAIN:
                        app.temperature_main_entry.delete(0,customtkinter.END)
                        app.temperature_main_entry.insert(0,value)
        # app.textbox.configure(state="normal") #writable
        # app.textbox.delete(0.0 ,customtkinter.END)
        # self.textbox.insert("0.0", "START\r\n")
        # app.textbox.configure(state="disable")
                        placeholder_text = app.temperature_main_entry.get()
                        print("Temp Main: ",placeholder_text)
                    case OD.S_TEMPERATURE_MEZZANINE:
                        app.temperature_mezzanine_entry.delete(0,customtkinter.END)
                        app.temperature_mezzanine_entry.insert(0,value)
                        placeholder_text = app.temperature_mezzanine_entry.get()
                        print("Temp Mezzanine: ",placeholder_text)
                    case OD.S_TEMPERATURE_PWR_BANK:
                        app.temperature_energy_bank_entry.delete(0,customtkinter.END)
                        app.temperature_energy_bank_entry.insert(0,value)
                        placeholder_text = app.temperature_energy_bank_entry.get()
                        print("Temp Energy Bank: ",placeholder_text)

            if index == OD.I_DEBUG_LOG:
                match subIndex:
                    case OD.S_DEBUG_LOG_STATE:
                        pass
                    case OD.S_DEBUG_LOG_READ:
                        print("S_DEBUG_LOG_READ")

            if index == OD.I_SWITCH_STATE:
                match subIndex:
                    case OD.S_SW_QINRUSH_STATE:
                        if 0 == msg.data[4]:
                            app.switch_inrush_state = False
                            app.switches_inrush.deselect()
                        else:
                            app.switch_inrush_state = True
                            app.switches_inrush.select()
                        pass
                    case OD.S_SW_QLB_STATE:
                        if 0 == msg.data[4]:
                            app.switch_load_state = False
                            app.switches_load.deselect()
                            #self.switches_load_event.progress_color="red"
                        else:
                            app.switch_load_state = True
                            app.switches_load.select()
                            #self.switches_load_event.progress_color="green"
                    case OD.S_SW_QSB_STATE:
                        if 0 == msg.data[4]:
                            app.switch_share_state = False
                            app.switches_share.deselect()
                        else:
                            app.switch_share_state = True
                            app.switches_share.select()

                    case OD.S_SW_QINB_STATE:
                        if 0 == msg.data[4]:
                            app.switch_input_state = False
                            app.switches_input.deselect()
                        else:
                            app.switch_input_state = True
                            app.switches_input.select()

            if index == OD.I_DPMU_POWER_SOURCE_TYPE:
                match data[4]:
                    case 0:  app.combobox_DPMU_Type.set("DFLT_CAP")
                    case 1:  app.combobox_DPMU_Type.set("DFLT_CAP_W_RDNT")
                    case 2:  app.combobox_DPMU_Type.set("DFLT_CAP_W_SUPP")
                    case 3:  app.combobox_DPMU_Type.set("DFLT_CAP_W_RDNT_SUPP")
                    case 4:  app.combobox_DPMU_Type.set("DFLT_BAT")
                    case 5:  app.combobox_DPMU_Type.set("DFLT_BAT_W_RDNT")
                    case 6:  app.combobox_DPMU_Type.set("DFLT_BAT_W_SUPP")
                    case 7:  app.combobox_DPMU_Type.set("DFLT_BAT_W_RDNT_SUPP")
                    case 8:  app.combobox_DPMU_Type.set("RDNT_CAP")
                    case 9:  app.combobox_DPMU_Type.set("RDNT_CAP_W_SUPP")
                    case 10: app.combobox_DPMU_Type.set("RDNT_BAT")
                    case 11: app.combobox_DPMU_Type.set("RDNT_BAT_W_SUPP")
                    case 12: app.combobox_DPMU_Type.set("SUPP_CAP")
                    case 13: app.combobox_DPMU_Type.set("SUPP_BAT")
                    case _:
                        app.combobox_DPMU_Type.set("BAD TYPE")
                        print("BAD TYPE")
                        return

            if index == OD.I_DATE_AND_TIME:
                value  = data[4]
                value |= data[5] <<  8
                value |= data[6] << 16
                value |= data[7] << 24
                app.time_entry.delete(0,customtkinter.END)
                app.time_entry.insert(0,value)
                placeholder_text = app.time_entry.get()
                print("time ",placeholder_text)

        if 0xc2 == data[0]: # SDO Block transfer initate transfer response
            if index == OD.I_DEBUG_LOG:
                print("I_DEBUG_LOG SDO BLOCK INIT")
                # if OD.S_DEBUG_LOG_READ == subIndex:
                print("S_DEBUG_LOG_READ")
                canOD.sdoBlock = 1
                canOD.sdoBlockTransferOngoing = 1
                debuglog.createDPMULogFile(OD.I_DEBUG_LOG)
                debuglog.ccs = 0xA3
                debuglog.set_data_byte1(0)
                debuglog.set_data_byte2(0)
                debuglog.set_data_byte3(0)
                debuglog.set_data_byte4(0)
                debuglog.set_data_byte5(0)
                debuglog.set_data_byte6(0)
                debuglog.set_data_byte7(0)
                debuglog.sendCanMessage()
                
            if index == OD.I_CAN_LOG:
                print("I_CAN_LOG SDO BLOCK INIT")
                # if OD.S_DEBUG_LOG_READ == subIndex:
                print("S_CAN_LOG_READ")
                canOD.sdoBlock = 1
                canOD.sdoBlockTransferOngoing = 1
                debuglog.createDPMULogFile(OD.I_CAN_LOG)
                canlog.ccs = 0xA3
                canlog.set_data_byte1(0)
                canlog.set_data_byte2(0)
                canlog.set_data_byte3(0)
                canlog.set_data_byte4(0)
                canlog.set_data_byte5(0)
                canlog.set_data_byte6(0)
                canlog.set_data_byte7(0)
                canlog.sendCanMessage()
                

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
        # canlog.closeDPMULogFile()

def setNodeId(value):
    heartbeat.setID(value)
    state.setID(value)
    reboot.setID(value)
    switch_share.setID(value)
    switch_load.setID(value)
    switch_input.setID(value)
    switch_inrush.setID(value)
    voltages_max_allowed_dc_bus_voltage.setID(value)
    voltages_min_allowed_dc_bus_voltage.setID(value)
    voltages_target_voltage.setID(value)
    voltages_dc_bus_short_circuit_limit.setID(value)
    power_pudget_dc_input.setID(value)
    current_max_load_current.setID(value)
    current_max_ess_current.setID(value)
    read_power.setID(value)
    energy_cell.setID(value)
    energy_bank.setID(value)
    temperature.setID(value)
    debuglog.setID(value)
    canlog.setID(value)
    log.setID(value)
    # time.setID(value)
    store_od.setID(value)
    restore_od.setID(value)
    dpmu_type_od.setID(value)
    nodeid_od.setID(value)


if __name__ == "__main__":
    print("DPMU: HELLO\r\n")
    nodeId = 0x67d
    heartbeat     = canOD(id=nodeId, ccs=0x2B, indexHigh=high_byte(OD.I_PRODUCER_HEARTBEAT_TIME), indexLow=low_byte(OD.I_PRODUCER_HEARTBEAT_TIME), subIndex=0)
    state         = canOD(id=nodeId, ccs=0x2F, indexHigh=high_byte(OD.I_DPMU_STATE),              indexLow=low_byte(OD.I_DPMU_STATE),              subIndex=OD.S_DPMU_OPERATION_REQUEST_STATE, data_byte4=0)
    reboot        = canOD(id=nodeId, ccs=0x2F, indexHigh=high_byte(OD.I_SEND_REBOOT_REQUEST),     indexLow=low_byte(OD.I_SEND_REBOOT_REQUEST),     subIndex=0) # FIXME NOT IN OD
    # nmt           = canOD(id=nodeId, ccs=0x2F, indexHigh=high_byte(OD.I_SWITCH_STATE),            indexLow=low_byte(OD.I_SWITCH_STATE),            subIndex=OD.S_SW_QSB_STATE) # sent using canopen_DPMU_A.write_raw()

    switch_share  = canOD(id=nodeId, ccs=0x2F, indexHigh=high_byte(OD.I_SWITCH_STATE), indexLow=low_byte(OD.I_SWITCH_STATE), subIndex=OD.S_SW_QSB_STATE) # SW_Qsb_State     - GLOAD_3 - J7.16
    switch_load   = canOD(id=nodeId, ccs=0x2F, indexHigh=high_byte(OD.I_SWITCH_STATE), indexLow=low_byte(OD.I_SWITCH_STATE), subIndex=OD.S_SW_QLB_STATE) # SW_Qlb_State     - GLOAD_2 - J9.5
    switch_input  = canOD(id=nodeId, ccs=0x2F, indexHigh=high_byte(OD.I_SWITCH_STATE), indexLow=low_byte(OD.I_SWITCH_STATE), subIndex=OD.S_SW_QINB_STATE) # SW_Qinb_State    - GLOAD_4 - J7.18
    switch_inrush = canOD(id=nodeId, ccs=0x2F, indexHigh=high_byte(OD.I_SWITCH_STATE), indexLow=low_byte(OD.I_SWITCH_STATE), subIndex=OD.S_SW_QINRUSH_STATE) # SW_Qnrush_State     - GLOAD_1 - J9.3

    voltages_max_allowed_dc_bus_voltage = canOD(id=nodeId, ccs=0x2F, indexHigh=high_byte(OD.I_DC_BUS_VOLTAGE), indexLow=low_byte(OD.I_DC_BUS_VOLTAGE), subIndex=OD.S_MAX_ALLOWED_DC_BUS_VOLTAGE)
    voltages_min_allowed_dc_bus_voltage = canOD(id=nodeId, ccs=0x2F, indexHigh=high_byte(OD.I_DC_BUS_VOLTAGE), indexLow=low_byte(OD.I_DC_BUS_VOLTAGE), subIndex=OD.S_MIN_ALLOWED_DC_BUS_VOLTAGE)
    voltages_target_voltage             = canOD(id=nodeId, ccs=0x2F, indexHigh=high_byte(OD.I_DC_BUS_VOLTAGE), indexLow=low_byte(OD.I_DC_BUS_VOLTAGE), subIndex=OD.S_TARGET_VOLTAGE_AT_DC_BUS)
    voltages_dc_bus_short_circuit_limit = canOD(id=nodeId, ccs=0x2F, indexHigh=high_byte(OD.I_DC_BUS_VOLTAGE), indexLow=low_byte(OD.I_DC_BUS_VOLTAGE), subIndex=OD.S_VDC_BUS_SHORT_CIRCUIT_LIMIT)

    power_pudget_dc_input               = canOD(id=nodeId, ccs=0x2B, indexHigh=high_byte(OD.I_POWER_BUDGET_DC_INPUT), indexLow=low_byte(OD.I_POWER_BUDGET_DC_INPUT), subIndex=0)
    current_max_load_current            = canOD(id=nodeId, ccs=0x2B, indexHigh=high_byte(OD.I_MAXIMUM_ALLOWED_LOAD_POWER), indexLow=low_byte(OD.I_MAXIMUM_ALLOWED_LOAD_POWER), subIndex=0)
    current_max_ess_current             = canOD(id=nodeId, ccs=0x2F, indexHigh=high_byte(OD.I_ESS_CURRENT), indexLow=low_byte(OD.I_ESS_CURRENT), subIndex=0)
    read_current_ess_current             = canOD(id=nodeId, ccs=0x40, indexHigh=high_byte(OD.I_ESS_CURRENT), indexLow=low_byte(OD.I_ESS_CURRENT), subIndex=0)
    read_power                          = canOD(id=nodeId, ccs=0x40, indexHigh=high_byte(OD.I_READ_POWER), indexLow=low_byte(OD.I_READ_POWER), subIndex=0)

    energy_cell                         = canOD(id=nodeId, ccs=0x2F, indexHigh=high_byte(OD.I_ENERGY_CELL_SUMMARY), indexLow=low_byte(OD.I_ENERGY_CELL_SUMMARY), subIndex=0)
    energy_bank                         = canOD(id=nodeId, ccs=0x2F, indexHigh=high_byte(OD.I_ENERGY_BANK_SUMMARY), indexLow=low_byte(OD.I_ENERGY_BANK_SUMMARY), subIndex=0)

    temperature                         = canOD(id=nodeId, ccs=0x40, indexHigh=high_byte(OD.I_TEMPERATURE), indexLow=low_byte(OD.I_TEMPERATURE), subIndex=0)

    debuglog                            = canOD(id=nodeId, ccs=0x40, indexHigh=high_byte(OD.I_DEBUG_LOG), indexLow=low_byte(OD.I_DEBUG_LOG), subIndex=0)
    canlog                              = canOD(id=nodeId, ccs=0x40, indexHigh=high_byte(OD.I_CAN_LOG), indexLow=low_byte(OD.I_CAN_LOG), subIndex=0)
    log                                 = canOD(id=nodeId, ccs=0x40, indexHigh=high_byte(OD.I_CAN_LOG), indexLow=low_byte(OD.I_CAN_LOG), subIndex=0)
    time                                = canOD(id=nodeId, ccs=0x40, indexHigh=high_byte(OD.I_DATE_AND_TIME), indexLow=low_byte(OD.I_DATE_AND_TIME), subIndex=0)

    store_od                            = canOD(id=nodeId, ccs=0x23, indexHigh=high_byte(OD.I_STORE_PARAMETERS), indexLow=low_byte(OD.I_STORE_PARAMETERS), subIndex=0,
                                                data_byte4=0x73, data_byte5=0x61, data_byte6=0x76, data_byte7=0x65)
    restore_od                          = canOD(id=nodeId, ccs=0x23, indexHigh=high_byte(OD.I_RESTORE_DEFAULT_PARAMETERS), indexLow=low_byte(OD.I_RESTORE_DEFAULT_PARAMETERS), subIndex=0,
                                                data_byte4=0x6C, data_byte5=0x6F, data_byte6=0x61, data_byte7=0x64)
    dpmu_type_od                         = canOD(id=nodeId, ccs=0x2F, indexHigh=high_byte(OD.I_DPMU_POWER_SOURCE_TYPE), indexLow=low_byte(OD.I_DPMU_POWER_SOURCE_TYPE), subIndex=0)
    nodeid_od                           = canOD(id=nodeId, ccs=0x2F, indexHigh=high_byte(OD.I_SET_NODEID), indexLow=low_byte(OD.I_SET_NODEID), subIndex=0)
    
    canopen_DPMU_A = setUpChannel(channel=0)
    canopen_DPMU_A.iocontrol.local_txecho = False
    canopen_DPMU_A_2 = setUpChannel(channel=0)
    # canopen_DPMU_A_2.iocontrol.local_txecho = False
    app = App()

    # t1 = threading(app.mainloop)
    t2 = threading.Thread(target=CanReceive.events)
    # t1.start()
    t2.start()
    # t1.join()
    # t2.join()

    # for i in range (0,3):
        # msg = canopen_DPMU_A_2.read(timeout=500)
        # print(msg)

    # app.temperature_entry.insert(0,"rr")

    app.mainloop()

    tearDownChannel(canopen_DPMU_A)
    tearDownChannel(canopen_DPMU_A_2)
