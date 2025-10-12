import machine
import os
import vfs
import time

# 全局SD卡硬件对象，确保仅初始化一次
_global_sd_hardware = None

class SDCard:
    def __init__(self, 
                 slot=2, 
                 sck=6, 
                 cs=4, 
                 miso=7, 
                 mosi=5, 
                 freq=5000000,  # 推荐5MHz，兼顾稳定性和速度
                 mount_point='/sd', 
                 work_dir='data', 
                 max_retry=2):
        """
        初始化SD卡控制器
        参数:
            slot: SPI通道
            sck/cs/miso/mosi: 对应SPI引脚
            freq: SPI通信频率
            mount_point: 挂载点路径
            work_dir: 工作目录（在挂载点下）
            max_retry: 操作失败重试次数
        """
        # 硬件配置参数
        self.slot = slot
        self.sck_pin = sck
        self.cs_pin = cs
        self.miso_pin = miso
        self.mosi_pin = mosi
        self.freq = freq
        
        # 文件系统配置
        self.mount_point = mount_point
        self.work_dir = work_dir
        self.full_work_path = f"{mount_point}/{work_dir}"
        
        # 容错配置
        self.max_retry = max_retry
        
        # 状态变量
        self.mounted = False
        global _global_sd_hardware
        self.sd = _global_sd_hardware

    def _initialize_once(self):
        """确保硬件只初始化一次，全局复用"""
        global _global_sd_hardware
        
        # 如果已有全局硬件对象，直接复用
        if _global_sd_hardware is not None:
            self.sd = _global_sd_hardware
            print("复用全局SD卡硬件对象")
            return True
        
        # 首次初始化，带重试机制
        for retry in range(self.max_retry):
            try:
                _global_sd_hardware = machine.SDCard(
                    slot=self.slot,
                    sck=self.sck_pin,
                    cs=self.cs_pin,
                    miso=self.miso_pin,
                    mosi=self.mosi_pin,
                    freq=self.freq
                )
                self.sd = _global_sd_hardware
                print("SD卡硬件首次初始化成功")
                return True
            except Exception as e:
                print(f"第{retry+1}次初始化失败: {e}")
                time.sleep(0.5)  # 等待硬件稳定后重试
        
        print("硬件初始化失败，无法继续操作")
        return False

    def mount(self):
        """挂载SD卡，支持重试机制处理偶发错误"""
        if self.mounted:
            print("SD卡已处于挂载状态")
            return True
        
        # 确保硬件已初始化
        if not self._initialize_once():
            return False
        
        # 带重试的挂载操作
        for retry in range(self.max_retry):
            try:
                # 先尝试卸载旧挂载点（防止残留）
                try:
                    vfs.umount(self.mount_point)
                except OSError:
                    pass  # 未挂载则忽略
                
                # 执行挂载
                vfs.mount(self.sd, self.mount_point)
                self.mounted = True
                
                # 确保工作目录存在
                self._safe_create_work_dir()
                print("SD卡挂载成功")
                return True
            except Exception as e:
                print(f"第{retry+1}次挂载失败: {e}")
                time.sleep(0.5)
        
        print("所有挂载重试均失败，建议检查硬件")
        return False

    def umount(self):
        """卸载SD卡，保留硬件对象供下次使用"""
        if not self.mounted:
            print("SD卡未挂载，无需卸载")
            return False
        
        try:
            vfs.umount(self.mount_point)
            self.mounted = False
            print("SD卡卸载成功（硬件对象保留）")
            return True
        except Exception as e:
            print(f"卸载失败: {e}")
            return False

    def _safe_create_work_dir(self):
        """安全创建工作目录，已存在则忽略"""
        try:
            os.mkdir(self.full_work_path)
            return True
        except OSError as e:
            # 错误码17表示目录已存在，属于正常情况
            return e.errno == 17

    def write_file(self, file_name, content, is_binary=False, subdir=''):
        """
        写入文件到工作目录
        参数:
            file_name: 文件名
            content: 内容（字符串或字节流）
            is_binary: 是否二进制模式
            subdir: 子目录（可选）
        """
        if not self.mounted:
            print("请先挂载SD卡")
            return False
        
        # 构建完整路径
        dir_path = self.full_work_path
        if subdir:
            dir_path = f"{self.full_work_path}/{subdir}"
            # 确保子目录存在
            self._safe_create_subdir(subdir)
        
        full_path = f"{dir_path}/{file_name}"
        mode = 'wb' if is_binary else 'w'
        
        try:
            with open(full_path, mode) as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"写入文件失败 {full_path}: {e}")
            return False

    def read_file(self, file_name, is_binary=False, subdir=''):
        """
        从工作目录读取文件
        参数:
            file_name: 文件名
            is_binary: 是否二进制模式
            subdir: 子目录（可选）
        返回:
            文件内容（字符串或字节流），失败返回None
        """
        if not self.mounted:
            print("请先挂载SD卡")
            return None
        
        # 构建完整路径
        dir_path = self.full_work_path
        if subdir:
            dir_path = f"{self.full_work_path}/{subdir}"
        
        full_path = f"{dir_path}/{file_name}"
        mode = 'rb' if is_binary else 'r'
        
        try:
            with open(full_path, mode) as f:
                return f.read()
        except Exception as e:
            print(f"读取文件失败 {full_path}: {e}")
            return None

    def list_files(self, subdir=''):
        """
        列出工作目录中的文件
        参数:
            subdir: 子目录（可选）
        返回:
            文件列表，失败返回None
        """
        if not self.mounted:
            print("请先挂载SD卡")
            return None
        
        # 构建目录路径
        dir_path = self.full_work_path
        if subdir:
            dir_path = f"{self.full_work_path}/{subdir}"
        
        try:
            return os.listdir(dir_path)
        except Exception as e:
            print(f"列出目录失败 {dir_path}: {e}")
            return None

    def _safe_create_subdir(self, subdir):
        """创建子目录，已存在则忽略"""
        full_path = f"{self.full_work_path}/{subdir}"
        try:
            os.mkdir(full_path)
            return True
        except OSError as e:
            return e.errno == 17  # 目录已存在返回True

    def delete_file(self, file_name, subdir=''):
        """
        删除工作目录中的文件
        参数:
            file_name: 文件名
            subdir: 子目录（可选）
        返回:
            成功返回True，失败返回False
        """
        if not self.mounted:
            print("请先挂载SD卡")
            return False
        
        # 构建完整路径
        dir_path = self.full_work_path
        if subdir:
            dir_path = f"{self.full_work_path}/{subdir}"
        
        full_path = f"{dir_path}/{file_name}"
        try:
            os.remove(full_path)
            return True
        except Exception as e:
            print(f"删除文件失败 {full_path}: {e}")
            return False

    def format(self):
        """
        格式化SD卡（谨慎使用！会清除所有数据）
        返回:
            成功返回True，失败返回False
        """
        # 格式化前确保已卸载
        if self.mounted:
            self.umount()
        
        try:
            # 创建FAT文件系统
            os.VfsFat.mkfs(self.sd)
            print("SD卡格式化成功")
            return True
        except Exception as e:
            print(f"SD卡格式化失败: {e}")
            return False
    