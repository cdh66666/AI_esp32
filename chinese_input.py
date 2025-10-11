import sys
import select

class ChineseInputHandler:
    @staticmethod
    def clear_input_buffer():
        """清空输入缓冲区"""
        while select.select([sys.stdin], [], [], 0)[0]:
            # 读取并丢弃输入内容
            sys.stdin.read(1)
    
    @staticmethod
    def get_input(prompt):
        """获取用户输入，支持中文处理"""
        print(prompt, end='')  # 显示提示文字
        buf = []
        
        while True:
            # 读取单个字符
            c = sys.stdin.read(1)
            
            # 处理换行情况
            if c in ('\r', '\n'):
                # 处理Windows的回车换行组合
                if c == '\r':
                    next_c = sys.stdin.read(1)
                    if next_c != '\n':
                        pass  # 不写回缓冲区，避免重复输入问题
                
                print()  # 换行
                break
            else:
                buf.append(c)
        
        # 清空输入缓冲区
        ChineseInputHandler.clear_input_buffer()
        
        # 拼接并返回结果
        result = ''.join(buf)
        return str(result)
    