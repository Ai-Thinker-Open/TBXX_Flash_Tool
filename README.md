# 安信可TB系列模块串口烧录工具 V2.x.x

V2.x.x版本的烧录工具不再使用bootloader，如果您需要使用V 1.5.x 版本的工具，请转到[https://github.com/Ai-Thinker-Open/TBXX_Flash_Tool/tree/1.x.x](https://github.com/Ai-Thinker-Open/TBXX_Flash_Tool/tree/1.x.x)

最新正式版下载：[链接](https://oapi.dingtalk.com/robot/send?access_token=808f68703b923031f65966529630bee74086e12f739ca0c88ff28c19b1fb81ad)

## 工具原理介绍
此工具使用python语言编写，有命令行和图形界面连个版本。命令行版本效率高，方便集成; 图形界面版本操作简单直观，易于上手。

命令行工具所有代码都在```Telink_Tools.py```文件中。

图形界面工具的界面逻辑在```TBXX_Flash_Tool.py```,最终的操作还是要调用```Telink_Tools.py```文件中的函数。

## 模块接线说明

```
USB-TTL                 TB Moudle

                 470 Ω 
             ┌-----▅--------SWS
Tx-----------└-----▅--------Rx
                  470 Ω   
Rx---------------------------Tx
RTS--------------------------RST
```

## 图形界面版本操作说明

![image](https://shyboy.oss-cn-shenzhen.aliyuncs.com/readonly/main.png)

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
如果提示 ```连接芯片失败```,可能是接线错误请检查接线。

### 打包可执行文件
    pyinstaller -F -w  -i aithinker.ico Ai-Thinker_TB_Tools.py

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
