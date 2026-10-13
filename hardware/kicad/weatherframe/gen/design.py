"""Weather frame main board: single source of truth for parts, nets and placement.

Used by gen_sch.py (schematic) and gen_pcb.py (board). Pin numbers follow the
KiCad library symbols / footprints named here.
"""

# fmt: off
R0402 = "Resistor_SMD:R_0402_1005Metric"
C0402 = "Capacitor_SMD:C_0402_1005Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
C0805 = "Capacitor_SMD:C_0805_2012Metric"

# LCSC numbers for JLCPCB assembly (checked in stock Oct 2026; "basic" parts where possible).
LCSC_R = {"10k": "C25744", "100k": "C25741", "1M": "C26083", "150k": "C25755", "5.1k": "C25905", "4.7k": "C25900", "2k": "C4109", "1k": "C11702"}
LCSC_C = {("100nF", C0402): "C1525", ("1uF", C0402): "C52923", ("4.7uF", C0603): "C19666",
          ("10uF", C0603): "C19702", ("10uF", C0805): "C15850", ("22uF", C0805): "C45783"}


def R(ref, value, a, b, pos, rot=0, pcb=None):
    return dict(ref=ref, sym="Device:R", fp=R0402, value=value, lcsc=LCSC_R[value],
                pins={"1": a, "2": b}, pos=pos, rot=rot, pcb=pcb)


def C(ref, value, a, b, pos, fp=C0402, rot=0, pcb=None):
    return dict(ref=ref, sym="Device:C", fp=fp, value=value, lcsc=LCSC_C[(value, fp)],
                pins={"1": a, "2": b}, pos=pos, rot=rot, pcb=pcb)


# Schematic positions are in mm on an A3 sheet. pcb = (x, y, rotation_deg, side) on the board,
# origin at the board's top-left corner. Board is 64 x 46 mm.
PARTS = [
    # ---------------- USB-C + ESD ----------------
    dict(ref="J1", sym="Connector:USB_C_Receptacle_USB2.0_16P", fp="Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12",
         value="USB-C", lcsc="C165948", mpn="TYPE-C-31-M-12",
         pins={"A4": "VBUS", "A9": "VBUS", "B4": "VBUS", "B9": "VBUS",
               "A1": "GND", "A12": "GND", "B1": "GND", "B12": "GND", "SH": "GND",
               "A5": "CC1", "B5": "CC2", "A6": "USB_DP", "B6": "USB_DP", "A7": "USB_DM", "B7": "USB_DM",
               "A8": None, "B8": None},
         pos=(40.64, 76.2), pcb=(26, 42.8, 0, "F")),
    R("R1", "5.1k", "CC1", "GND", (76.2, 50.8), pcb=(21.5, 35.5, 90, "F")),
    R("R2", "5.1k", "CC2", "GND", (83.82, 50.8), pcb=(30.5, 35.5, 90, "F")),
    dict(ref="U5", sym="Power_Protection:USBLC6-2SC6", fp="Package_TO_SOT_SMD:SOT-23-6",
         value="USBLC6-2SC6", lcsc="C7519", mpn="USBLC6-2SC6",
         pins={"1": "USB_DP", "6": "USB_DP", "3": "USB_DM", "4": "USB_DM", "2": "GND", "5": "VBUS"},
         pos=(91.44, 88.9), pcb=(26, 35.0, 0, "F")),

    # ---------------- Charger ----------------
    dict(ref="U2", sym="Battery_Management:MCP73831-2-OT", fp="Package_TO_SOT_SMD:SOT-23-5",
         value="MCP73831-2", lcsc="C424093", mpn="MCP73831T-2ACI/OT",
         pins={"4": "VBUS", "2": "GND", "3": "VBAT", "5": "PROG", "1": "STAT"},
         pos=(144.78, 63.5), pcb=(19.5, 30, 0, "F")),
    C("C1", "4.7uF", "VBUS", "GND", (121.92, 50.8), fp=C0603, pcb=(19.5, 26.5, 0, "F")),
    C("C2", "4.7uF", "VBAT", "GND", (167.64, 50.8), fp=C0603, pcb=(12, 32.2, 0, "F")),
    R("R3", "2k", "PROG", "GND", (129.54, 81.28), pcb=(17, 39, 90, "F")),           # 500 mA charge current
    R("R4", "1k", "VBUS", "LED_A", (175.26, 50.8), pcb=(9.5, 38.5, 0, "F")),
    dict(ref="D2", sym="Device:LED", fp="LED_SMD:LED_0603_1608Metric", value="CHG", lcsc="C2286", mpn="KT-0603R",
         pins={"2": "LED_A", "1": "STAT"}, pos=(175.26, 68.58), rot=90, pcb=(9.5, 40.5, 0, "F")),
    R("R5", "100k", "STAT", "CHG_STAT", (182.88, 50.8), pcb=(13, 39, 90, "F")),
    R("R6", "150k", "CHG_STAT", "GND", (190.5, 50.8), pcb=(15, 39, 90, "F")),      # 100k/150k: 5 V -> 3.0 V (ESP32-S3 VIH min = 2.475 V)

    # ---------------- Battery + load sharing ----------------
    dict(ref="J2", sym="Connector_Generic:Conn_01x02", fp="Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal",
         value="LiPo 1S", lcsc="C2763693", mpn="PH-2AWT (JST PH 2.0)",
         pins={"1": "VBAT", "2": "GND"}, pos=(40.64, 139.7), pcb=(5.2, 27, -90, "F")),
    dict(ref="D1", sym="Device:D_Schottky", fp="Diode_SMD:D_SOD-123", value="B5819W", lcsc="C8598", mpn="B5819W",
         pins={"2": "VBUS", "1": "VSYS"}, pos=(76.2, 124.46), pcb=(13.5, 29.5, 0, "F")),
    dict(ref="Q1", sym="Transistor_FET:AO3401A", fp="Package_TO_SOT_SMD:SOT-23", value="AO3401A", lcsc="C15127", mpn="AO3401A",
         pins={"1": "VBUS", "2": "VSYS", "3": "VBAT"}, pos=(91.44, 142.24), pcb=(13.5, 25, 0, "F")),
    R("R8", "1M", "VBAT", "VBAT_SENSE", (63.5, 160.02), pcb=(8, 34.5, 90, "F")),
    R("R9", "1M", "VBAT_SENSE", "GND", (71.12, 160.02), pcb=(10, 34.5, 90, "F")),
    C("C3", "100nF", "VBAT_SENSE", "GND", (78.74, 160.02), pcb=(12, 34.5, 90, "F")),
    R("R10", "100k", "VBUS", "VBUS_SENSE", (88.9, 160.02), pcb=(14, 34.5, 90, "F")),
    R("R11", "150k", "VBUS_SENSE", "GND", (96.52, 160.02), pcb=(16, 34.5, 90, "F")),  # 100k/150k, see R6

    # ---------------- 3.3 V buck-boost ----------------
    dict(ref="U3", sym="Regulator_Switching:TPS63001", fp="Package_SON:Texas_DRC0010J",
         value="TPS63001", lcsc="C28060", mpn="TPS63001DRCR",
         pins={"5": "VSYS", "8": "VSYS", "6": "VSYS", "7": "GND", "3": "GND", "11": "GND", "9": "GND",
               "4": "SW1", "2": "SW2", "1": "+3V3", "10": "+3V3"},
         pos=(152.4, 139.7), pcb=(20, 15, 0, "F")),
    dict(ref="L1", sym="Device:L", fp="Inductor_SMD:L_Changjiang_FNR4030S", value="1.5uH", lcsc="C42100",
         mpn="SWPA4030S1R5NT", pins={"1": "SW1", "2": "SW2"}, pos=(127, 162.56), rot=90, pcb=(14.5, 15, 0, "F")),
    C("C4", "10uF", "VSYS", "GND", (121.92, 124.46), fp=C0805, pcb=(20, 10.5, 0, "F")),
    C("C5", "100nF", "VSYS", "GND", (129.54, 124.46), pcb=(23.5, 11, 0, "F")),
    C("C6", "22uF", "+3V3", "GND", (180.34, 124.46), fp=C0805, pcb=(26.5, 14, 90, "F")),
    C("C7", "22uF", "+3V3", "GND", (187.96, 124.46), fp=C0805, pcb=(28.8, 14, 90, "F")),

    # ---------------- ESP32-S3 ----------------
    dict(ref="U1", sym="RF_Module:ESP32-S3-WROOM-1", fp="RF_Module:ESP32-S3-WROOM-1",
         value="ESP32-S3-WROOM-1-N16R8", lcsc="C2913202", mpn="ESP32-S3-WROOM-1-N16R8",
         pins={"2": "+3V3", "1": "GND", "40": "GND", "41": "GND", "3": "EN", "27": "IO0",
               "9": "I2C_SDA", "10": "I2C_SCL", "4": "VBUS_SENSE", "5": "VBAT_SENSE",
               "6": "EPD_PWR_N", "7": "EPD_BUSY", "12": "EPD_RST", "17": "EPD_DC", "18": "EPD_CS",
               "19": "EPD_DIN", "20": "EPD_CLK", "21": "BTN", "22": "MAINT", "8": "CHG_STAT",
               "13": "USB_DM", "14": "USB_DP",
               "15": None, "38": None, "39": None, "11": None, "16": None, "23": None, "24": None, "25": None,
               "26": None, "28": None, "29": None, "30": None, "31": None, "32": None, "33": None, "34": None,
               "35": None, "36": None, "37": None},
         pos=(276.86, 96.52), pcb=(46, 6.8, 0, "F")),
    C("C8", "10uF", "+3V3", "GND", (241.3, 50.8), fp=C0603, pcb=(33, 3, 90, "F")),
    C("C9", "100nF", "+3V3", "GND", (248.92, 50.8), pcb=(34.8, 3, 90, "F")),
    R("R12", "10k", "+3V3", "EN", (220.98, 50.8), pcb=(34, 7.5, 0, "F")),
    C("C10", "1uF", "EN", "GND", (228.6, 50.8), pcb=(34, 9, 0, "F")),
    R("R13", "10k", "+3V3", "IO0", (208.28, 50.8), pcb=(58.5, 15.3, 0, "F")),

    # ---------------- Buttons + switch ----------------
    dict(ref="SW1", sym="Switch:SW_Push", fp="Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A", value="RESET",
         lcsc="C318884", mpn="TS-1187A-B-A-B", pins={"1": "EN", "2": "GND"}, pos=(220.98, 160.02), pcb=(17, 4.5, 0, "F")),
    dict(ref="SW2", sym="Switch:SW_Push", fp="Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A", value="BOOT",
         lcsc="C318884", mpn="TS-1187A-B-A-B", pins={"1": "IO0", "2": "GND"}, pos=(220.98, 175.26), pcb=(26, 4.5, 0, "F")),
    dict(ref="SW3", sym="Switch:SW_Push", fp="Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A", value="REFRESH",
         lcsc="C318884", mpn="TS-1187A-B-A-B", pins={"1": "BTN", "2": "GND"}, pos=(220.98, 190.5), pcb=(58.5, 33.5, 0, "F")),
    R("R14", "10k", "+3V3", "BTN", (241.3, 182.88), pcb=(52.5, 27, 90, "F")),
    C("C11", "100nF", "BTN", "GND", (248.92, 182.88), pcb=(54.5, 27, 90, "F")),
    dict(ref="SW4", sym="Switch:SW_SPDT", fp="Button_Switch_SMD:SW_SPDT_Shouhan_MSK12C02", value="MAINT",
         lcsc="C431540", mpn="MSK12C02", pins={"2": "MAINT", "1": "GND", "3": None}, pos=(266.7, 182.88),
         pcb=(61.0, 22, -90, "F")),

    # ---------------- SHT40 (on the isolated corner tab) ----------------
    dict(ref="U4", sym="Sensor_Humidity:SHT4x", fp="Sensor_Humidity:Sensirion_DFN-4_1.5x1.5mm_P0.8mm_SHT4x_NoCentralPad",
         value="SHT40-AD1B", lcsc="C2909890", mpn="SHT40-AD1B-R2",
         pins={"1": "I2C_SDA", "2": "I2C_SCL", "3": "+3V3", "4": "GND"}, pos=(342.9, 63.5), pcb=(6, 5, 0, "F")),
    C("C12", "100nF", "+3V3", "GND", (360.68, 50.8), pcb=(6, 8, 0, "F")),
    R("R15", "4.7k", "+3V3", "I2C_SDA", (368.3, 50.8), pcb=(34, 11.7, 0, "F")),
    R("R16", "4.7k", "+3V3", "I2C_SCL", (375.92, 50.8), pcb=(34, 13.2, 0, "F")),

    # ---------------- E-paper power switch + header ----------------
    dict(ref="Q2", sym="Transistor_FET:AO3401A", fp="Package_TO_SOT_SMD:SOT-23", value="AO3401A", lcsc="C15127", mpn="AO3401A",
         pins={"1": "EPD_PWR_N", "2": "+3V3", "3": "EPD_VCC"}, pos=(345.44, 132.08), pcb=(44, 37, 0, "F")),
    R("R17", "100k", "+3V3", "EPD_PWR_N", (327.66, 124.46), pcb=(40.5, 37, 90, "F")),
    C("C13", "4.7uF", "EPD_VCC", "GND", (365.76, 124.46), fp=C0603, pcb=(48, 37, 0, "F")),
    dict(ref="J3", sym="Connector_Generic:Conn_01x09", fp="Connector_PinHeader_2.54mm:PinHeader_1x09_P2.54mm_Vertical",
         value="E-Paper HAT", lcsc="", mpn="1x9 pin header 2.54 mm (hand-solder)",
         pins={"1": "EPD_VCC", "2": "GND", "3": "EPD_DIN", "4": "EPD_CLK", "5": "EPD_CS", "6": "EPD_DC",
               "7": "EPD_RST", "8": "EPD_BUSY", "9": "EPD_VCC"},
         pos=(378.46, 172.72), pcb=(35, 43, 90, "F"), hand_solder=True),

    # ---------------- Mounting holes (M2.5) ----------------
    *[dict(ref=f"H{i+1}", sym="Mechanical:MountingHole", fp="MountingHole:MountingHole_2.7mm_M2.5", value="M2.5",
           lcsc="", pins={}, pos=(330.2 + 10.16 * i, 241.3), pcb=p, hand_solder=True)
      for i, p in enumerate([(3.5, 42.5, 0, 'F'), (60.5, 3.5, 0, 'F'), (3.5, 17.0, 0, 'F'), (60.5, 42.5, 0, 'F')])],
]

# Nets that are driven by passive parts only; ERC needs a PWR_FLAG on them.
PWR_FLAGS = ["VBUS", "GND", "VSYS", "EPD_VCC"]

BOARD_W, BOARD_H = 64.0, 46.0

# fmt: on
