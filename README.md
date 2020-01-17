# 安信可TB系列模块串口烧录工具

此工具用于安信可TB系列模块烧录固件三元组等等操作，目前支持```TB-01```，```TB-02```。

最新Windows版图形界面烧录工具下载地址：https://shyboy.oss-cn-shenzhen.aliyuncs.com/readonly/TBXX_Flash_Tool.exe

## 工具原理介绍
此工具使用python语言编写，有命令行和图形界面连个版本。命令行版本效率高，方便集成; 图形界面版本操作简单直观，易于上手。

命令行工具所有代码都在```Telink_Tools.py```文件中。

图形界面工具的界面逻辑在```TBXX_Flash_Tool.py```,最终的操作还是要调用```Telink_Tools.py```文件中的函数。

## 模块接线说明

需要使用USB转串口模块连接TB模块，且USB转串口要有```DTR```和```RTS```引脚。

### TB-01模块接线方法：

|USB To TTL |TB-01模块|
|:---------:|:------:|
|  Vcc      |        |
|  Gnd      |  Gnd   |
|  Tx       |  Rx    |
|  Rx       |  Tx    |
|  RTS      |  VCC   |
|  DTR      |  SWS   |

### TB-02模块接线方法：

|USB To TTL |TB-01模块|
|:---------:|:------:|
|  Vcc      |  Vcc   |
|  Gnd      |  Gnd   |
|  Tx       |  Rx    |
|  Rx       |  Tx    |
|  RTS      |  RST   |
|  DTR      |  SWS   |

## 图形界面版本操作说明

![image](https://raw.githubusercontent.com/Ai-Thinker-Open/TBXX_Flash_Tool/master/mian.png)

图形界面如上图所示，提供烧录固件，烧录三元组，擦除固件等功能。

### 烧录固件
首先点击串口选择框选择对应的串口，然后点击```···```按钮选择要烧录的固件，点击烧录```固件按钮```即可烧录，烧录成功后```Log窗口```将变成绿色，烧录失败```Log窗口```将变成红色。
### 烧录天猫精灵三元组
在图形界面上烧录三元组那一行有三个输入框，分别对应三元组的```ProductID```,```MAC```,```Secert```，在输入框中输入相应的数据并正确选择串口号，点击```烧录三元组```按钮即可烧录三元组。同样，烧录成功后```Log窗口```将变成绿色，烧录失败```Log窗口```将变成红色。

### 擦除固件
点击```擦除固件```按钮，将擦除模块中的固件。

### 擦除Mesh数据
点击```擦除Mesh Key```按钮，将擦除模块中的Mesh配网信息，包括```Application Key``` 和 ```NetWork Key```。

### 整片擦除
点击```整片擦除```按钮，将擦除模块中出bootloader外的所有Flash区域。

### 常见问题
#### 串口打开失败
如果提示 ```打开串口xxxx失败....```,可能是串口被其他软件占用，解除暂用后再试一次即可。

#### 连接芯片失败
如果提示 ```连接芯片失败```,可能是接线错误请检查接线，如果确认接线无误仍然连接失败可能是bootloader损坏。如果bootloader损坏只能采用官方专用烧录器重新烧录botloader。

### 打包可执行文件
    pyinstaller -F -w  TBXX_Flash_Tool.py

## 命令行版本操作说明
命令行版本的指令格式为：

    python Telink_Tools.py [--port PORT] {burn,burn_triad,write_flash,read_flash,erase_flash}

### 烧录固件
指令示例：

    python Telink_Tools.py --port com3 burn at_v1.2.bin
```--port```指定端口号，```burn``` 为烧录指令，后面的参数为要烧录的固件

### 烧录三元组
指令示例：

    python Telink_Tools.py --port com3 burn_triad 1345 78da07fa44a7 221746e805ac0e6269bd4d3e55f1145c
```--port```指定端口号，```burn_triad``` 为烧录三元组指令，后面的三个参数依次为三元组的```ProductID```,```MAC```,```Secert```

### 擦除Flash
指令示例：
    
    python Telink_Tools.py --port com3 erase_flash 0x4000 16

```--port```指定端口号，```erase_flash```擦除Flash指令，后面的两个参数依次为要擦除的Flash起始地址和擦除的扇区数。Flash最小擦除单元为一个扇区，TB模块Flash的每个扇区为4096字节。

TB系列模块的Flash大小为512KB，其中0x0 - 0x4000(16KB)存放的是bootloader，不可擦除。0x4000 - 0x30000(176KB)存放用户固件，0x30000 - 0x40000(64KB)存放Mesh配网数据，0x76000-0x77000存放模组Mac地址，0x78000-0x79000存放天猫精灵三元组。