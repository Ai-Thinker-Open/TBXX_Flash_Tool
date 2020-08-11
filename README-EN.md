# An Xinke TB series module serial port burning tool

This repo is used for translation to English - by google translate

This tool is used to burn firmware triplets of Enxin TB series modules, etc. It currently supports `` `TB-01```,` `` TB-02```.

The download address of the latest Windows version of the graphical interface burning tool (CN)':https://ai-thinker.oss-cn-shenzhen.aliyuncs.com/TB_Tool/Ai-Thinker_TB_Tools.exe
Donwload English version here: TBD

## Introduction to tool principles
This tool is written in python language and has a command line and a graphical interface with two versions. The command line version is highly efficient and easy to integrate; the graphical interface version is simple and intuitive to operate and easy to use.

All the code of the command line tool is in the file `Telink_Tools.py`.

The interface logic of the graphical interface tool is in `` `TBXX_Flash_Tool.py```, and the final operation still needs to call the function in the` Telink_Tools.py` file.

## Module wiring instructions

You need to use the USB to serial port module to connect to the TB module, and the USB to serial port must have `` `DTR``` and` `` RTS``` pins.

### TB-01 module wiring method:

| USB To TTL | TB-01 |
|:---------:|:------:|
|  Vcc      |        |
|  Gnd      |  Gnd   |
|  Tx       |  Rx    |
|  Rx       |  Tx    |
|  RTS      |  VCC   |
|  DTR      |  SWS   |

### TB-02 module wiring method:

|USB To TTL |TB-01   |
|:---------:|:------:|
|  Vcc      |  Vcc   |
|  Gnd      |  Gnd   |
|  Tx       |  Rx    |
|  Rx       |  Tx    |
|  RTS      |  RST   |
|  DTR      |  SWS   |

## Graphical interface version operating instructions

![image](https://shyboy.oss-cn-shenzhen.aliyuncs.com/readonly/main.png)

The graphical interface is shown in the figure above, which provides functions such as burning firmware, burning triples, and erasing firmware.

### Burn firmware
First click the serial port selection box to select the corresponding serial port, and then click the `` `···` `button to select the firmware to be burned, click the burn```firmware button` '' to burn, after successful burning` The `` Log window '' will turn green, and the failed programming "Log window" will turn red.
### Burn the Tmall Genie Triad
There are three input boxes on the line where the triplet is burned on the graphical interface, corresponding to the triplet `` `ProductID```,` `` MAC```, `` `Secert```, in the input box Enter the corresponding data and select the serial port number correctly, click the `` `Burn Triad '' button to burn the triplet. Similarly, after successful programming, the `Log window` will turn green, and if the programming fails, the` Log window` will turn red.

### Erase the firmware
Click the `` `Erase Firmware''` button to erase the firmware in the module.

### Erase Mesh data
Click the `` `Erase Mesh Key` '' button to erase the Mesh configuration information in the module, including` `` Application Key``` and `` `NetWork Key```.

### Whole Chip Erase
Clicking the `` `Whole Chip Erase` '' button will erase all flash areas outside the bootloader in the module.

### common problem
#### Failed to open the serial port
If the prompt "` `Failed to open the serial port xxxx ...", it may be that the serial port is occupied by other software, try again after releasing the temporary use.

#### Failed to connect the chip
If it prompts `` Failed to connect to the chip '', it may be a wiring error. Please check the wiring. If the wiring is correct and the connection fails, the bootloader may be damaged. If the bootloader is damaged, the official writer can only be used to reprogram the botloader.

### Packaging executable files
    pyinstaller -F -w -i aithinker.ico Ai-Thinker_TB_Tools.py

## Command line version operating instructions
The command format of the command line version is:

    python Telink_Tools.py [--port PORT] {burn, burn_triad, write_flash, read_flash, erase_flash}

### Burn firmware
Instruction example:

    python Telink_Tools.py --port com3 burn at_v1.2.bin
`` `--port``` specifies the port number,` `` burn``` is the burn command, and the following parameters are the firmware to be burned

### Burning triples
Instruction example:

    python Telink_Tools.py --port com3 burn_triad 1345 78da07fa44a7 221746e805ac0e6269bd4d3e55f1145c
`` `--port``` specifies the port number,` `` burn_triad``` is the instruction to burn the triplet, and the following three parameters are in turn the triplet `` `ProductID```,` `` MAC```, `` `Secret```

### Erase Flash
Command example:
    
    python Telink_Tools.py --port com3 erase_flash 0x4000 16

`` `--port``` specifies the port number,` `` erase_flash``` erase flash command, the next two parameters are the starting address of the flash to be erased and the number of sectors erased. The minimum erase unit of Flash is one sector, and each sector of TB module Flash is 4096 bytes.

The Flash size of the TB series module is 512KB, among which 0x0-0x4000 (16KB) stores the bootloader and cannot be erased. 0x4000-0x30000 (176KB) stores user firmware, 0x30000-0x40000 (64KB) stores Mesh configuration data, 0x76000-0x77000 stores module Mac address, and 0x78000-0x79000 stores Tmall Genie triplet.
