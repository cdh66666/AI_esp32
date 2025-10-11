# light_parser.py
import ujson
from ws2812_controller import WS2812Controller

class LightParser:
    def __init__(self, led_ctrl: WS2812Controller):
        self.led_ctrl = led_ctrl  # 注入灯控实例，避免重复初始化

    def extract_valid_cmds(self, reply):
        """从大模型回复中提取所有有效的灯控指令"""
        if "[LIGHT_CMD]" not in reply or "[/LIGHT_CMD]" not in reply:
            return []
        
        # 拆分所有指令片段，筛选有效JSON
        cmd_fragments = reply.split("[LIGHT_CMD]")
        valid_cmds = []
        for fragment in cmd_fragments:
            if "[/LIGHT_CMD]" in fragment:
                cmd_json = fragment.split("[/LIGHT_CMD]")[0].strip()
                if cmd_json:
                    valid_cmds.append(cmd_json)
        return valid_cmds

    def execute_light_cmd(self, cmd_json):
        """执行单个灯控指令"""
        cmd = ujson.loads(cmd_json)
        if cmd.get("action") != "set_single_led":
            return False  # 只处理单独控灯指令
        
        params = cmd.get("params", {})
        index = params.get("index", 0)
        r = params.get("r", 0)
        g = params.get("g", 0)
        b = params.get("b", 0)
        self.led_ctrl.set_single_led(index, r, g, b)
        return True

    def process_light_reply(self, reply):
        """完整流程：提取指令 → 执行 → 反馈结果"""
        valid_cmds = self.extract_valid_cmds(reply)
        if not valid_cmds:
            return False  # 无灯控指令，返回False让main处理聊天回复
        
        try:
            # 逐个执行所有灯控指令
            for cmd_json in valid_cmds:
                self.execute_light_cmd(cmd_json)
            print("Deepseek: 所有指定的灯都已经调好啦～")
        except Exception as e:
            print(f"Deepseek: 刚才控制灯时出了点小问题呢～({str(e)[:15]})")
            print("Deepseek: 换个说法试试吧，比如'第2个灯灭'～")
        return True  # 已处理灯控，无需再处理聊天回复