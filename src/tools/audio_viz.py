import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import queue
import threading
import sys
from matplotlib.colors import LinearSegmentedColormap

class AudioVisualizer:
    def __init__(self, sample_rate=44100, block_size=1024, channels=2, device=None, 
                 fullscreen=False, visualization_type='spectrum'):
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.channels = channels
        self.device = device
        self.visualization_type = visualization_type  # 'spectrum', 'bars', 'wave'
        
        # 获取设备信息
        self.device_info = self._get_device_info()
        self.device_name = self._get_device_name()
        
        # 创建队列存储音频数据
        self.q = queue.Queue()
        
        # 创建自定义颜色映射
        colors = [(0, 0, 0.5), (0, 0.5, 1), (0, 1, 1), (1, 1, 0), (1, 0, 0)]
        self.cmap = LinearSegmentedColormap.from_list('audio_cmap', colors)
        
        # 创建图形界面
        plt.rcParams.update({'figure.facecolor': 'black',
                            'axes.facecolor': 'black',
                            'axes.edgecolor': 'white',
                            'axes.labelcolor': 'white',
                            'text.color': 'white'})
        
        self.fig = plt.figure(figsize=(12, 8))
        self.ax = self.fig.add_subplot(111)
        
        # 设备名称将添加到标题中
        title_prefix = f"监控输出设备: {self.device_name} - "
        
        if visualization_type == 'spectrum':
            # 频谱瀑布图
            self.spectrum_data = np.zeros((100, block_size//2 + 1))
            self.img = self.ax.imshow(self.spectrum_data, 
                                    aspect='auto', 
                                    origin='lower', 
                                    interpolation='bilinear',
                                    cmap=self.cmap,
                                    vmin=-30, vmax=80)
            self.ax.set_title(f'{title_prefix}音频频谱响应', fontsize=16)
            self.ax.set_ylabel('时间', fontsize=12)
            self.ax.set_xlabel('频率', fontsize=12)
        elif visualization_type == 'bars':
            # 频谱条形图
            self.bars_data = np.zeros(block_size//16)
            self.bars = self.ax.bar(range(len(self.bars_data)), self.bars_data, 
                                  color='cyan', width=0.8)
            self.ax.set_title(f'{title_prefix}音频响应', fontsize=16)
            self.ax.set_ylim(0, 100)
        else:  # 'wave'
            # 波形图
            self.wave_data = np.zeros(block_size)
            self.line, = self.ax.plot(self.wave_data, color='cyan', lw=2)
            self.ax.set_title(f'{title_prefix}音频波形响应', fontsize=16)
            self.ax.set_ylim([-1, 1])
        
        # 移除刻度标签
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        
        # 调整布局
        self.fig.tight_layout(pad=1)
        
        # 如果需要全屏显示
        if fullscreen:
            self.fig.canvas.manager.full_screen_toggle()
        
        # 标记是否正在运行
        self.running = False

    def _get_device_info(self):
        """获取当前设备的详细信息"""
        try:
            if self.device is None:
                # 获取默认输出设备信息
                return sd.query_devices(kind='output')
            else:
                # 获取指定设备信息
                return sd.query_devices(self.device)
        except Exception as e:
            print(f"获取设备信息出错: {e}")
            return None

    def _get_device_name(self):
        """获取当前设备名称"""
        if self.device_info is None:
            return "未知设备"
        
        try:
            return self.device_info['name']
        except (KeyError, TypeError):
            return f"设备 {self.device}" if self.device is not None else "默认输出设备"

    def audio_callback(self, indata, frames, time, status):
        """这是sounddevice的回调函数，用于接收音频数据"""
        if status:
            print(status, file=sys.stderr)
        
        # 将混合的立体声数据转换为单声道用于分析
        mono_data = np.mean(indata, axis=1) if indata.shape[1] > 1 else indata[:, 0]
        self.q.put(mono_data)

    def update_plot(self, frame):
        """更新图形的回调函数"""
        try:
            data = self.q.get_nowait()
            
            if self.visualization_type == 'spectrum':
                # 计算频谱
                spectrum = np.abs(np.fft.rfft(data * np.hanning(len(data))))
                # 转换为dB
                spectrum = 20 * np.log10(spectrum / np.max(spectrum) + 1e-10)
                
                # 更新频谱图数据
                self.spectrum_data = np.roll(self.spectrum_data, -1, axis=0)
                self.spectrum_data[-1, :] = spectrum
                
                # 更新频谱图
                self.img.set_array(self.spectrum_data)
                return [self.img]
                
            elif self.visualization_type == 'bars':
                # 计算频谱
                spectrum = np.abs(np.fft.rfft(data * np.hanning(len(data))))
                # 对频谱进行降采样和平滑处理，只保留低频部分
                spectrum = spectrum[:len(spectrum)//8]
                # 分组并取平均值，减少条形数量
                n_bars = len(self.bars_data)
                spectrum_grouped = np.array([np.mean(spectrum[i:i+len(spectrum)//n_bars]) 
                                           for i in range(0, len(spectrum), len(spectrum)//n_bars)])[:n_bars]
                
                # 缩放到0-100范围
                self.bars_data = 100 * spectrum_grouped / (np.max(spectrum_grouped) + 1e-10)
                
                # 更新条形高度和颜色
                for bar, h in zip(self.bars, self.bars_data):
                    bar.set_height(h)
                    # 根据高度设置颜色
                    bar.set_color(self.cmap(h/100))
                
                return self.bars
                
            else:  # 'wave'
                # 简单平滑处理
                data = np.convolve(data, np.ones(3)/3, mode='same')
                self.line.set_ydata(data)
                return [self.line]
                
        except queue.Empty:
            if self.visualization_type == 'spectrum':
                return [self.img]
            elif self.visualization_type == 'bars':
                return self.bars
            else:  # 'wave'
                return [self.line]

    def list_devices(self):
        """列出所有可用的音频设备"""
        print("可用的音频设备:")
        devices = sd.query_devices()
        print("\n输出设备:")
        for i, dev in enumerate(devices):
            if dev['max_output_channels'] > 0:
                print(f"  {i}: {dev['name']} (输出通道: {dev['max_output_channels']})")
        
        print("\nWASAPI 设备 (支持环回):")
        for i, dev in enumerate(devices):
            host_api = sd.query_hostapis(dev['hostapi'])['name']
            if 'WASAPI' in host_api and dev['max_output_channels'] > 0:
                print(f"  {i}: {dev['name']} ({host_api})")

    def find_wasapi_loopback_device(self, target_device_name=None):
        """查找支持环回的WASAPI设备"""
        devices = sd.query_devices()
        target_name = target_device_name or self.device_name
        
        # 首先尝试找完全匹配的WASAPI设备
        for i, dev in enumerate(devices):
            host_api = sd.query_hostapis(dev['hostapi'])['name']
            if dev['name'] == target_name and 'WASAPI' in host_api:
                return i
        
        # 如果找不到完全匹配，尝试找包含设备名称的WASAPI设备
        for i, dev in enumerate(devices):
            host_api = sd.query_hostapis(dev['hostapi'])['name']
            if target_name in dev['name'] and 'WASAPI' in host_api:
                return i
                
        # 如果还找不到，返回任一WASAPI输出设备
        for i, dev in enumerate(devices):
            host_api = sd.query_hostapis(dev['hostapi'])['name']
            if 'WASAPI' in host_api and dev['max_output_channels'] > 0:
                return i
                
        # 实在找不到，返回默认设备
        return None

    def start(self):
        """开始音频采集和可视化"""
        if self.running:
            print("可视化已经在运行中")
            return
            
        self.running = True
        
        # 设置动画，明确设置save_count避免警告
        self.ani = FuncAnimation(
            self.fig, self.update_plot, 
            interval=30, blit=True,
            cache_frame_data=False,
            save_count=100
        )
        
        try:
            # 查找合适的WASAPI设备用于环回监听
            loopback_device = self.find_wasapi_loopback_device()
            
            if loopback_device is None:
                print("未找到合适的WASAPI设备，将使用默认设备")
            else:
                print(f"使用设备 {loopback_device} 进行环回监听")
            
            # 显示正在监控的设备信息
            device_info = sd.query_devices(loopback_device)
            print(f"\n正在监控输出设备: {device_info['name']}")
            print(f"设备详情: {self.channels}通道, {self.sample_rate}Hz采样率")
            
            # 启动环回监听
            self.stream = sd.InputStream(
                device=loopback_device,  # 使用找到的环回设备
                channels=self.channels,
                samplerate=self.sample_rate,
                blocksize=self.block_size,
                callback=self.audio_callback,
                latency='low',
                extra_settings={'wasapi_loopback': True}  # 启用环回模式
            )
            
            # 直接在主线程中启动，避免警告
            with self.stream:
                plt.show()
        except Exception as e:
            print(f"启动环回监听失败: {e}")
            print("请确保您正在使用Windows系统且选择了有效的输出设备")
            self.running = False
            raise
        
    def stop(self):
        """停止音频采集和可视化"""
        if not self.running:
            print("可视化未在运行")
            return
            
        self.running = False
        if hasattr(self, 'stream'):
            self.stream.abort()
        plt.close(self.fig)


# 示例用法
if __name__ == "__main__":
    # 创建可视化器 - 选择一种可视化类型: 'spectrum', 'bars', 或 'wave'
    viz_type = 'bars'  # 可以更改为 'spectrum' 或 'wave'
    
    # 列出设备
    print("正在搜索可用音频设备...")
    temp_visualizer = AudioVisualizer()
    temp_visualizer.list_devices()
    
    # 请选择一个输出设备的ID (可以从上面列出的设备中选择)
    device_id = None  # 默认使用系统默认输出设备
    # device_id = 4    # 如果要指定设备，请取消注释并填入设备ID
    
    try:
        # 创建可视化器实例
        visualizer = AudioVisualizer(
            device=device_id,
            visualization_type=viz_type,
            fullscreen=False,  # 设为True可全屏显示
            channels=2  # 通常输出设备是立体声(2通道)
        )
        
        print(f"开始音频可视化({viz_type})。关闭窗口退出。")
        print("请播放一些音频内容以查看响应...")
        visualizer.start()
    except KeyboardInterrupt:
        print("正在停止...")
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'visualizer' in locals() and hasattr(visualizer, 'running') and visualizer.running:
            visualizer.stop()