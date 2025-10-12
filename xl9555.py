import machine
import time

class XL9555:
    def __init__(self, sda_pin=10, scl_pin=11, i2c_addr=0x20):
        """
        初始化XL9555（基于规格书8.1节I2C时序、9.1节地址定义）
        - I2C频率100kHz（规格书6.6节标准模式）
        - 命令字节参考规格书表6：覆盖Port0/Port1的输入/输出/配置寄存器
        """
        self.i2c = machine.I2C(
            0,
            sda=machine.Pin(sda_pin),
            scl=machine.Pin(scl_pin),
            freq=100000  # 符合规格书I2C总线速率要求
        )
        self.i2c_addr = i2c_addr
        
        # 命令字节定义（规格书表6：Port0/Port1寄存器映射）
        self.CMD = {
            # 输入寄存器（只读，反映IO实际电平，规格书9.2.2节）
            "INPUT_PORT0": 0x00,
            "INPUT_PORT1": 0x01,
            # 输出寄存器（读写，控制IO输出电平，规格书9.2.3节）
            "OUTPUT_PORT0": 0x02,
            "OUTPUT_PORT1": 0x03,
            # 配置寄存器（读写，控制IO方向，规格书9.2.5节：1=输入，0=输出）
            "CONFIG_PORT0": 0x06,
            "CONFIG_PORT1": 0x07
        }
        
        # 初始化：所有IO默认配置为输入（符合规格书9.3节上电默认状态）
        self.set_port_config(port=0, config_data=0xFF)  # Port0全为输入
        self.set_port_config(port=1, config_data=0xFF)  # Port1全为输入

    def _write_reg(self, cmd_byte, data):
        """
        写寄存器（规格书9.6.1节：I2C写时序=地址+命令字节+数据）
        - cmd_byte：命令字节（选择目标寄存器）
        - data：8位数据（对应Port的8路IO配置/电平）
        """
        try:
            self.i2c.writeto(self.i2c_addr, bytes([cmd_byte, data]))
            return True
        except OSError as e:
            print(f"写寄存器（命令0x{cmd_byte:02X}）失败: {e}")
            return False

    def _read_reg(self, cmd_byte):
        """
        读寄存器（规格书9.6.2节：I2C读时序=地址+命令字节→读数据）
        - cmd_byte：命令字节（选择目标寄存器）
        - 返回：8位数据（对应Port的8路IO状态）
        """
        try:
            # 先发送命令字节选择寄存器，再读取1字节数据
            self.i2c.writeto(self.i2c_addr, bytes([cmd_byte]))
            return self.i2c.readfrom(self.i2c_addr, 1)[0]
        except OSError as e:
            print(f"读寄存器（命令0x{cmd_byte:02X}）失败: {e}")
            return None

    def set_port_config(self, port, config_data):
        """
        配置整个Port的IO方向（规格书9.2.5节）
        - port：0=Port0，1=Port1
        - config_data：8位配置值（bit=1→输入，bit=0→输出）
          例：0xF0→高4位输入，低4位输出；0x00→全输出；0xFF→全输入
        """
        if port not in [0, 1]:
            print("Port仅支持0或1（规格书4.2节：仅2个8位Port）")
            return False
        cmd = self.CMD["CONFIG_PORT0"] if port == 0 else self.CMD["CONFIG_PORT1"]
        result = self._write_reg(cmd, config_data)
        print(f"Port{port}配置{'成功' if result else '失败'}，配置值：0x{config_data:02X}")
        return result

    def set_single_io_config(self, port, io_num, is_input):
        """
        配置单个IO的方向（规格书9.2.5节）
        - port：0=Port0，1=Port1
        - io_num：IO编号（0~7，对应Port的8路IO，规格书4.2节引脚定义）
        - is_input：True=输入，False=输出
        """
        if port not in [0, 1] or not (0 <= io_num <= 7):
            print("Port需为0/1，IO编号需为0~7")
            return False
        # 1. 读取当前Port的配置值
        cmd_config = self.CMD["CONFIG_PORT0"] if port == 0 else self.CMD["CONFIG_PORT1"]
        current_config = self._read_reg(cmd_config)
        if current_config is None:
            return False
        # 2. 修改目标IO的配置位（1=输入，0=输出）
        new_config = current_config | (1 << io_num) if is_input else current_config & ~(1 << io_num)
        # 3. 写入新配置
        result = self._write_reg(cmd_config, new_config)
        print(f"Port{port}_IO{io_num}配置为{'输入' if is_input else '输出'}：{'成功' if result else '失败'}")
        return result

    def set_single_io_level(self, port, io_num, level):
        """
        控制单个输出IO的电平（规格书9.2.3节，仅IO为输出时有效）
        - port：0=Port0，1=Port1
        - io_num：IO编号（0~7）
        - level：True=高电平，False=低电平（规格书6.5节：输出高电平≈VCC，低电平≈0V）
        """
        if port not in [0, 1] or not (0 <= io_num <= 7):
            print("Port需为0/1，IO编号需为0~7")
            return False
        # 1. 先确认IO已配置为输出（避免误操作输入IO）
        cmd_config = self.CMD["CONFIG_PORT0"] if port == 0 else self.CMD["CONFIG_PORT1"]
        current_config = self._read_reg(cmd_config)
        if current_config is None or (current_config & (1 << io_num)):
            print(f"Port{port}_IO{io_num}未配置为输出，无法设置电平")
            return False
        # 2. 读取当前Port的输出值
        cmd_output = self.CMD["OUTPUT_PORT0"] if port == 0 else self.CMD["OUTPUT_PORT1"]
        current_output = self._read_reg(cmd_output)
        if current_output is None:
            return False
        # 3. 修改目标IO的电平位
        new_output = current_output | (1 << io_num) if level else current_output & ~(1 << io_num)
        # 4. 写入新电平
        result = self._write_reg(cmd_output, new_output)
        print(f"Port{port}_IO{io_num}电平设置为{'高' if level else '低'}：{'成功' if result else '失败'}")
        return result

    def get_single_io_level(self, port, io_num):
        """
        读取单个IO的电平（规格书9.2.2节，IO为输入/输出均有效）
        - port：0=Port0，1=Port1
        - io_num：IO编号（0~7）
        - 返回：True=高电平，False=低电平，None=读取失败
        """
        if port not in [0, 1] or not (0 <= io_num <= 7):
            print("Port需为0/1，IO编号需为0~7")
            return None
        # 读取当前Port的输入寄存器（反映IO实际电平，与方向无关）
        cmd_input = self.CMD["INPUT_PORT0"] if port == 0 else self.CMD["INPUT_PORT1"]
        current_input = self._read_reg(cmd_input)
        if current_input is None:
            return None
        # 提取目标IO的电平位
        return (current_input & (1 << io_num)) != 0
    
    def init_key_io(self, key_io_list, port=0):
        """
        初始化按键IO为输入
        - key_io_list: 按键IO编号列表
        - port: 端口号，默认为0
        """
        for io_num in key_io_list:
            self.set_single_io_config(port, io_num, True)
    
    def get_key_state(self, io_num, port=0):
        """
        获取按键状态
        - io_num: IO编号
        - port: 端口号，默认为0
        - 返回: True表示按键按下，False表示按键松开
        """
        # 假设按键按下为低电平，松开为高电平
        # 如果实际硬件相反，可以将返回值取反
        return not self.get_single_io_level(port, io_num)
    
    
if __name__ == "__main__":
    # 1. 初始化XL9555（匹配硬件：SDA=10，SCL=11，地址0x20，规格书表4）
    xl = XL9555(sda_pin=10, scl_pin=11, i2c_addr=0x20)
    time.sleep_ms(100)  # 等待芯片上电稳定（规格书9.3节上电复位时间）

    # 2. 初始化4个按键（Port0_IO1~IO4）
    key_config = [
        {"name": "KEY0", "io": 1},
        {"name": "KEY1", "io": 2},
        {"name": "KEY2", "io": 3},
        {"name": "KEY3", "io": 4}
    ]
    xl.init_key_io(key_io_list=[k["io"] for k in key_config])

    # 3. 记录上一次按键状态（初始为松开）
    last_key_states = {k["name"]: False for k in key_config}
    print("\n=== 开始4按键循环检测（按Ctrl+C停止） ===")
    print(f"{'KEY0':<6}{'KEY1':<6}{'KEY2':<6}{'KEY3':<6}")
    print("-" * 24)

    try:
        while True:
            # 读取当前所有按键状态
            current_key_states = {}
            for k in key_config:
                current_key_states[k["name"]] = xl.get_key_state(io_num=k["io"])

            # 仅在状态变化时打印（避免重复输出）
            if current_key_states != last_key_states:
                # 格式化输出：按下显示"●"，松开显示"○"
                output = ""
                for k in key_config:
                    output += f"{'●' if current_key_states[k['name']] else '○'}\t"
                print(output.strip())
                # 更新上一次状态
                last_key_states = current_key_states.copy()

            # 防抖延时（100ms，平衡实时性与稳定性）
            time.sleep_ms(100)

    except KeyboardInterrupt:
        print("\n\n=== 检测停止 ===")
    finally:
        # 恢复Port0为全输入（符合规格书9.3节默认状态）
        xl.set_port_config(0, 0xFF)
        print("Port0已恢复为全输入状态（规格书默认）")
