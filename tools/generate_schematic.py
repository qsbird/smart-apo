#!/usr/bin/env python3
"""Generate the Rev.A1 KiCad schematic and custom symbol library.

This generator uses labels on every pin so the schematic stays readable while
remaining electrically connected in KiCad.  All pin maps are kept in one data
structure and are also exported as CSV for independent review.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import kicad_sch_api as ksa
from kicad_sch_api.library.cache import SymbolLibraryCache, set_symbol_cache

ROOT = Path(__file__).resolve().parents[1]
HW = ROOT / "hardware"
LIB = HW / "smart_apo_symbols.kicad_sym"
OUT = HW / "smart_apo_common_revA1.kicad_sch"


SYMBOLS = {
    "MCU20": ["PB7/I2C_SDA", "VDD/VDDA", "PA1/ADC", "PF2/NRST", "PB6/I2C_SCL",
              "PA13/SWDIO", "PA5/SPI_SCK", "PA6/SPI_MISO", "PA7/SPI_MOSI", "PB0/LED",
              "PA3/UART_RX", "PA14/SWCLK", "VSS/VSSA", "PA4/FLASH_CS", "PC14/LSE_IN",
              "PC15/LSE_OUT", "PA9/REED_WAKE", "PA10/STRAIN_DRDY", "PA0/IMU_INT", "PA2/UART_TX"],
    "IMU14": ["SDO/SA0", "SDx", "SCx", "INT1", "VDDIO", "GND", "GND", "VDD",
              "INT2", "OCS_AUX", "SDO_AUX", "CS", "SCL", "SDA"],
    "PRESS7": ["SDA", "SA0", "SCL", "INT_DRDY", "GND", "VDD", "PAD2LID"],
    "ADC16": ["REFP", "VIN1N", "VIN1P", "VIN2N", "VIN2P", "VBG", "REFN", "AVSS",
              "DVSS", "XIN", "XOUT", "DRDY", "SCLK", "SDIO", "DVDD", "AVDD/LDO"],
    "FLASH8": ["/CS", "DO/IO1", "/WP/IO2", "GND", "DI/IO0", "CLK", "/HOLD/IO3", "VCC"],
    "CHARGER5": ["STAT", "VSS", "VBAT", "VDD", "PROG"],
    "LDO5": ["IN", "GND", "EN", "NC", "OUT"],
    "MOS3": ["G", "S", "D"],
    "PASSIVE2": ["1", "2"],
    "CONN6": ["E+", "E-", "S+", "S-", "A+", "A-"],
    "CONN7": ["GND", "CHARGE_IN", "SWDIO", "SWCLK", "UART_TX", "UART_RX", "NRST"],
}


def symbol_text(name: str, pins: list[str]) -> str:
    nleft = (len(pins) + 1) // 2
    nright = len(pins) - nleft
    rows = max(nleft, nright)
    half_h = max(3.81, (rows - 1) * 1.27 / 2 + 1.27)
    half_w = 7.62 if len(pins) > 8 else 5.08
    lines = [f'  (symbol "{name}"',
             '    (pin_names (offset 0.762))',
             '    (exclude_from_sim no)', '    (in_bom yes)', '    (on_board yes)',
             f'    (property "Reference" "U" (at 0 {half_h+1.27:.3f} 0) (effects (font (size 1.27 1.27))))',
             f'    (property "Value" "{name}" (at 0 {-half_h-1.27:.3f} 0) (effects (font (size 1.27 1.27))))',
             '    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
             '    (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
             '    (property "Description" "Smart Apo Rev.A1 custom symbol" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))',
             f'    (symbol "{name}_0_1"',
             f'      (rectangle (start {-half_w:.3f} {half_h:.3f}) (end {half_w:.3f} {-half_h:.3f})',
             '        (stroke (width 0) (type default)) (fill (type background))))',
             f'    (symbol "{name}_1_1"']
    for i, pname in enumerate(pins, 1):
        if i <= nleft:
            y = (nleft - 1) * 1.27 / 2 - (i - 1) * 1.27
            x, rot = -half_w - 2.54, 0
        else:
            j = i - nleft - 1
            y = -(nright - 1) * 1.27 / 2 + j * 1.27
            x, rot = half_w + 2.54, 180
        lines += [f'      (pin passive line (at {x:.3f} {y:.3f} {rot}) (length 2.54)',
                  f'        (name "{pname}" (effects (font (size 1.0 1.0))))',
                  f'        (number "{i}" (effects (font (size 1.0 1.0)))))']
    lines += ['    )', '  )']
    return "\n".join(lines)


def write_symbol_library():
    body = ['(kicad_symbol_lib (version 20231120) (generator kicad_symbol_editor)']
    for name, pins in SYMBOLS.items():
        body.append(symbol_text(name, pins))
    body.append(')')
    LIB.write_text("\n".join(body) + "\n")


# ref, value, symbol, footprint, x, y, rotation, population, pin->net
PARTS = [
    ("U1", "STM32G031F8P6", "MCU20", "Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm", 105, 100, 0, "BOTH",
     {1:"I2C_SDA",2:"3V3",3:"VBAT_SENSE",4:"NRST",5:"I2C_SCL",6:"SWDIO",7:"SPI_SCK",8:"SPI_MISO",9:"SPI_MOSI",10:"LED_GATE",11:"UART_RX",12:"SWCLK",13:"GND",14:"FLASH_CS",15:"LSE_IN",16:"LSE_OUT",17:"REED_WAKE",18:"STRAIN_DRDY",19:"IMU_INT",20:"UART_TX"}),
    ("U2", "LSM6DSOTR", "IMU14", "Package_LGA:LGA-14_2.5x3mm_P0.5mm", 160, 72, 0, "BOTH",
     {1:"GND",2:"GND",3:"GND",4:"IMU_INT",5:"3V3",6:"GND",7:"GND",8:"3V3",9:"NC",10:"NC",11:"3V3",12:"3V3",13:"I2C_SCL",14:"I2C_SDA"}),
    ("U3", "LPS28DFWTR", "PRESS7", "SmartApo:CCLGA-7_LPS28DFW", 160, 112, 0, "BOTH",
     {1:"I2C_SDA",2:"GND",3:"I2C_SCL",4:"NC",5:"GND",6:"3V3",7:"GND"}),
    ("U4", "NAU7802SGI", "ADC16", "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm", 160, 152, 0, "UNDERWATER",
     {1:"BRIDGE_S+",2:"AIN_N_FILT",3:"AIN_P_FILT",4:"NC",5:"NC",6:"VBG",7:"BRIDGE_S-",8:"GND",9:"GND",10:"NC",11:"NC",12:"STRAIN_DRDY",13:"I2C_SCL",14:"I2C_SDA",15:"3V3",16:"BRIDGE_E+"}),
    ("U5", "W25Q256JVEIQ", "FLASH8", "Package_DFN_QFN:WSON-8-1EP_6x8mm_P1.27mm", 105, 145, 0, "BOTH",
     {1:"FLASH_CS",2:"SPI_MISO",3:"3V3",4:"GND",5:"SPI_MOSI",6:"SPI_SCK",7:"3V3",8:"3V3"}),
    ("U6", "MCP73831T-2ACI/OT", "CHARGER5", "Package_TO_SOT_SMD:SOT-23-5", 55, 65, 0, "BOTH",
     {1:"CHG_STAT",2:"GND",3:"VBAT",4:"CHARGE_IN",5:"CHG_PROG"}),
    ("U7", "TPS7A0233PDBVR", "LDO5", "Package_TO_SOT_SMD:SOT-23-5", 55, 105, 0, "BOTH",
     {1:"VBAT",2:"GND",3:"VBAT",4:"NC",5:"3V3"}),
    ("Q1", "2N7002", "MOS3", "Package_TO_SOT_SMD:SOT-23", 55, 165, 0, "AWA",
     {1:"LED_GATE",2:"GND",3:"LED_K"}),
    ("J1", "BATTERY", "PASSIVE2", "Connector_Wire:SolderWire-1sqmm_1x02_P3.9mm_D1.4mm_OD2.7mm", 55, 132, 0, "BOTH", {1:"VBAT",2:"GND"}),
    ("J2", "POGO_DEBUG_CHARGE", "CONN7", "SmartApo:POGO_7x1.27mm", 105, 55, 0, "BOTH",
     {1:"GND",2:"CHARGE_IN",3:"SWDIO",4:"SWCLK",5:"UART_TX",6:"UART_RX",7:"NRST"}),
    ("J3", "FULL_BRIDGE_6WIRE", "CONN6", "SmartApo:PAD_6x1.27mm", 215, 152, 0, "UNDERWATER",
     {1:"BRIDGE_E+",2:"GND",3:"BRIDGE_S+",4:"BRIDGE_S-",5:"BRIDGE_A+",6:"BRIDGE_A-"}),
]

PASSIVES = [
    ("R1","4.7k","I2C_SDA","3V3","BOTH"),("R2","4.7k","I2C_SCL","3V3","BOTH"),
    ("R3","20k","CHG_PROG","GND","BOTH"),("R4","1M","VBAT","VBAT_SENSE","BOTH"),
    ("R5","330k","VBAT_SENSE","GND","BOTH"),("R6","68R","3V3","LED_A","AWA"),
    ("R7","100k","LED_GATE","GND","AWA"),("R8","100R","BRIDGE_A+","AIN_P_FILT","UNDERWATER"),
    ("R9","100R","BRIDGE_A-","AIN_N_FILT","UNDERWATER"),("R10","100k","3V3","REED_WAKE","BOTH"),
    ("R11","10k","3V3","NRST","BOTH"),
]

CAPS = [
    ("C1","100n","3V3","GND","BOTH"),("C2","100n","3V3","GND","BOTH"),
    ("C3","100n","3V3","GND","BOTH"),("C4","100n","3V3","GND","BOTH"),
    ("C5","100n","3V3","GND","BOTH"),("C6","1u","BRIDGE_E+","GND","UNDERWATER"),
    ("C7","100n","VBG","GND","UNDERWATER"),("C8","100n","3V3","GND","BOTH"),
    ("C9","1u","VBAT","GND","BOTH"),("C10","1u","3V3","GND","BOTH"),
    ("C11","4.7u","CHARGE_IN","GND","BOTH"),("C12","4.7u","VBAT","GND","BOTH"),
    ("C13","10n","AIN_P_FILT","AIN_N_FILT","UNDERWATER"),("C14","100n","VBAT_SENSE","GND","BOTH"),
    ("C15","8.2p","LSE_IN","GND","BOTH"),("C16","8.2p","LSE_OUT","GND","BOTH"),
    ("C17","100n","NRST","GND","BOTH"),
]


def build_schematic():
    cache = SymbolLibraryCache(Path('/tmp/smart-apo-ksa-cache'), enable_persistence=True)
    cache.add_library_path(LIB)
    set_symbol_cache(cache)
    sch = ksa.create_schematic("smart_apo_common_revA1")
    sch.add_text("SMART APO + SMART UNDERWATER Rev.A1", (105, 25), size=2.0, bold=True)
    sch.add_text("Common core; Population=BOTH/AWA/UNDERWATER controls assembly variant", (105, 30), size=1.1)

    pin_rows = []
    for ref,value,symbol,footprint,x,y,rot,pop,pins in PARTS:
        comp = sch.components.add(f"smart_apo_symbols:{symbol}", ref, value, (x,y), footprint,
                                  rotation=rot, Population=pop)
        for number, net in pins.items():
            if net == "NC":
                pos = comp.get_pin_position(str(number))
                sch.no_connects.add((pos.x,pos.y))
            else:
                sch.add_label(net, pin=(ref,str(number)), size=0.9)
            pin_rows.append((ref,number,SYMBOLS[symbol][number-1],net,pop))

    # Passives are arranged in three readable columns.
    for i,(ref,val,n1,n2,pop) in enumerate(PASSIVES):
        x = 45 + (i//6)*35
        y = 205 + (i%6)*12
        c = sch.components.add("smart_apo_symbols:PASSIVE2",ref,val,(x,y),
                               "Resistor_SMD:R_0402_1005Metric",Population=pop)
        sch.add_label(n1,pin=(ref,"1"),size=0.8); sch.add_label(n2,pin=(ref,"2"),size=0.8)
        pin_rows += [(ref,1,"1",n1,pop),(ref,2,"2",n2,pop)]
    for i,(ref,val,n1,n2,pop) in enumerate(CAPS):
        x = 150 + (i//9)*40
        y = 195 + (i%9)*11.5
        c = sch.components.add("smart_apo_symbols:PASSIVE2",ref,val,(x,y),
                               "Capacitor_SMD:C_0402_1005Metric",Population=pop)
        sch.add_label(n1,pin=(ref,"1"),size=0.8); sch.add_label(n2,pin=(ref,"2"),size=0.8)
        pin_rows += [(ref,1,"1",n1,pop),(ref,2,"2",n2,pop)]

    extras = [
        ("D1","RED_HIGH_BRIGHT","PASSIVE2","LED_SMD:LED_0805_2012Metric",55,185,"AWA",{1:"LED_A",2:"LED_K"}),
        ("SW1","SMT_REED_NO","PASSIVE2","Button_Switch_SMD:SW_SPST_MK16",105,185,"BOTH",{1:"REED_WAKE",2:"GND"}),
        ("Y1","32.768kHz_12.5pF","PASSIVE2","Crystal:Crystal_SMD_2012-2Pin_2.0x1.2mm",105,170,"BOTH",{1:"LSE_IN",2:"LSE_OUT"}),
    ]
    for ref,val,sym,fp,x,y,pop,pins in extras:
        sch.components.add(f"smart_apo_symbols:{sym}",ref,val,(x,y),fp,Population=pop)
        for num,net in pins.items():
            sch.add_label(net,pin=(ref,str(num)),size=0.8)
            pin_rows.append((ref,num,SYMBOLS[sym][num-1],net,pop))

    sch.save(OUT)
    issues = sch.validate()
    with (HW/"pin_net_review_revA1.csv").open("w",newline="") as f:
        w=csv.writer(f); w.writerow(["Reference","Pin","Pin name","Net","Population"]); w.writerows(pin_rows)
    return {"components":len(list(sch.components)),"validation_issues":[str(x) for x in issues],"output":str(OUT)}


def main():
    write_symbol_library()
    report=build_schematic()
    (HW/"schematic_generation_report.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))


if __name__ == "__main__":
    main()
