import cv2  # OpenCV库，用于图像处理和人脸识别
import numpy as np  # 数值计算库
import tkinter as tk  # GUI库
from tkinter import ttk, messagebox  # GUI组件和消息框
from PIL import Image, ImageTk, ImageDraw, ImageFont  # 图像处理库，用于GUI中显示图像
import threading  # 多线程处理
import time  # 时间处理
import os  # 文件和目录操作
import pickle  # 数据序列化
from datetime import datetime  # 日期时间处理
import re  # 正则表达式模块

class FaceRecognitionSystem:
    """
    人脸识别系统主类
    实现了人脸录入、识别和用户管理功能
    """
    def __init__(self, window):
        """
        初始化人脸识别系统
        Args:
            window: tkinter主窗口对象
        """
        # 设置主窗口
        self.window = window
        self.window.title("人脸识别系统")
        # 调整窗口大小以适应更大的视频显示
        self.window.geometry("1200x800")
        
        # 设置视频帧的目标尺寸
        self.video_width = 840  # 16:9 比例
        self.video_height = 480
        
        # 初始化人脸识别模型
        try:
            # 加载人脸检测器（Haar级联分类器）
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            # 创建LBPH人脸识别器
            self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        except AttributeError:
            # 如果没有安装OpenCV contrib模块，显示错误信息
            messagebox.showerror("错误", "请安装 OpenCV contrib 模块：\npip install opencv-contrib-python")
            self.window.destroy()
            return
        
        # 创建数据存储目录和文件路径
        self.data_dir = "face_data"  # 用户数据目录
        self.model_path = "face_model.yml"  # 模型文件路径
        os.makedirs(self.data_dir, exist_ok=True)  # 确保数据目录存在
        
        # 加载用户数据和模型
        self.users = self.load_users()  # 加载用户信息
        if os.path.exists(self.model_path):
            self.face_recognizer.read(self.model_path)  # 如果存在模型文件则加载
        
        # 设置主题颜色
        self.colors = {
            'primary': '#E3F2FD',      # 浅蓝色
            'secondary': '#FFF8E1',    # 浅琥珀色
            'success': '#E8F5E9',      # 浅绿色
            'warning': '#FFF3E0',      # 浅橙色
            'error': '#FFEBEE',        # 浅红色
            'background': '#F5F5F5',   # 浅灰色
            'text': '#212121',         # 深灰色
        }
        
        # 设置窗口最小尺寸
        self.window.minsize(1000, 600)
        # 允许窗口调整大小
        self.window.resizable(True, True)
        
        # 设置窗口样式
        self.window.configure(bg=self.colors['background'])
        self.style = ttk.Style()
        self.style.configure('Main.TFrame', background=self.colors['background'])
        self.style.configure('Main.TLabel', background=self.colors['background'], foreground=self.colors['text'])
        self.style.configure('Main.TButton', 
                            padding=10, 
                            background=self.colors['primary'],
                            foreground='white')
        
        # 设置字体
        self.fonts = {
            'title': ('Helvetica', 16, 'bold'),
            'header': ('Helvetica', 12, 'bold'),
            'normal': ('Helvetica', 10),
            'small': ('Helvetica', 9)
        }
        
        # 初始化GUI界面
        self.setup_gui()
        
    def setup_gui(self):
        """
        设置图形用户界面
        创建并布局所有GUI组件
        """
        # 创建主框架，使用grid布局
        self.main_frame = ttk.Frame(self.window, style='Main.TFrame')
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # 配置grid权重，使其响应式
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=3)  # 视频区域占3份
        self.main_frame.grid_columnconfigure(1, weight=1)  # 控制面板占1份
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # 创建左侧视频显示区域
        self.video_frame = ttk.Frame(self.main_frame, style='Main.TFrame')
        self.video_frame.grid(row=0, column=0, sticky="nsew", padx=10)
        
        # 视频显示区域（移除标题）
        self.video_label = ttk.Label(
            self.video_frame,
            borderwidth=1,  # 减小边框宽度
            relief="solid",
            style='Main.TLabel',
            background='black'  # 设置黑色背景
        )
        self.video_label.pack(expand=True, fill=tk.BOTH)  # 填充整个区域
        
        # 创建右侧控制面板
        self.control_frame = ttk.Frame(self.main_frame, style='Main.TFrame')
        self.control_frame.grid(row=0, column=1, sticky="nsew", padx=10)
        
        # 用户信息输入区域
        self.user_frame = self.create_section(
            self.control_frame, 
            "用户信息",
            self.fonts['header']
        )
        
        ttk.Label(
            self.user_frame, 
            text="用户名:", 
            font=self.fonts['normal'],
            style='Main.TLabel'
        ).pack(pady=5)
        
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(
            self.user_frame, 
            textvariable=self.username_var,
            font=self.fonts['normal'],
            width=30
        )
        username_entry.pack(pady=5, padx=10, fill=tk.X)
        
        # 控制按钮区域
        buttons_frame = self.create_section(
            self.control_frame, 
            "操作控制",
            self.fonts['header']
        )
        
        # 创建按钮组
        button_group = ttk.Frame(buttons_frame, style='Main.TFrame')
        button_group.pack(pady=10, fill=tk.X)
        
        # 主操作按钮
        self.register_button = self.create_button(
            button_group, 
            "录入人脸", 
            self.start_registration,
            'primary'
        )
        self.register_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.verify_button = self.create_button(
            button_group, 
            "开始验证", 
            self.start_verification,
            'success'
        )
        self.verify_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.stop_button = self.create_button(
            button_group, 
            "停止", 
            self.stop_camera,
            'error',
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 状态显示区域
        status_frame = self.create_section(
            self.control_frame, 
            "状态信息",
            self.fonts['header']
        )
        
        self.status_label = ttk.Label(
            status_frame,
            text="状态: 就绪",
            font=self.fonts['normal'],
            style='Main.TLabel'
        )
        self.status_label.pack(pady=5)
        
        # 用户管理区域
        users_frame = self.create_section(
            self.control_frame, 
            "用户管理",
            self.fonts['header']
        )
        
        # 搜索框
        search_frame = ttk.Frame(users_frame, style='Main.TFrame')
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(
            search_frame, 
            text="搜索:", 
            font=self.fonts['normal'],
            style='Main.TLabel'
        ).pack(side=tk.LEFT, padx=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=self.fonts['normal']
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 用户列表
        list_frame = ttk.Frame(users_frame, style='Main.TFrame')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 创建带滚动条的列表框
        self.users_listbox = self.create_scrolled_listbox(list_frame)
        
        # 用户管理按钮
        user_buttons = ttk.Frame(users_frame, style='Main.TFrame')
        user_buttons.pack(fill=tk.X, pady=5)
        
        self.create_button(
            user_buttons, 
            "删除用户", 
            self.delete_selected_user,
            'error', 
            size='small'
        ).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        self.create_button(
            user_buttons, 
            "修改用户名", 
            self.rename_selected_user,
            'warning', 
            size='small'
        ).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        self.create_button(
            user_buttons, 
            "重新采集", 
            self.recapture_user_face,
            'primary', 
            size='small'
        ).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        # 用户详情显示
        self.user_details_label = ttk.Label(
            users_frame,
            text="",
            font=self.fonts['small'],
            style='Main.TLabel',
            justify=tk.LEFT
        )
        self.user_details_label.pack(pady=5, anchor=tk.W)
        
        # 绑定用户选择事件
        self.users_listbox.bind('<<ListboxSelect>>', self.on_user_select)
        
        # 初始化运行时变量
        self.is_running = False  # 摄像头运行状态
        self.cap = None  # 摄像头对象
        self.current_mode = None  # 当前模式（注册/验证）
        self.face_samples = []  # 人脸样本列表
        
    def load_users(self):
        """
        从文件加载用户数据
        Returns:
            dict: 用户数据字典，如果文件不存在则返回空字典
        """
        users_file = os.path.join(self.data_dir, "users.pkl")
        if os.path.exists(users_file):
            with open(users_file, 'rb') as f:
                return pickle.load(f)
        return {}
        
    def save_users(self):
        """保存用户数据到文件"""
        users_file = os.path.join(self.data_dir, "users.pkl")
        with open(users_file, 'wb') as f:
            pickle.dump(self.users, f)
            
    def update_users_list(self, search_text=''):
        """
        更新用户列表显示
        Args:
            search_text: 搜索关键词
        """
        self.users_listbox.delete(0, tk.END)
        sorted_users = sorted(
            self.users.items(), 
            key=lambda x: x[1]['registered_at'],
            reverse=True  # 最新注册的用户显示在前面
        )
        
        for user_id, user_info in sorted_users:
            user_name = user_info['name']
            if search_text in user_name.lower():
                self.users_listbox.insert(
                    tk.END, 
                    f"{user_name} (ID: {user_id})"
                )
                
    def start_registration(self):
        """开始人脸注册流程"""
        # 检查用户名是否输入
        if not self.username_var.get().strip():
            messagebox.showerror("错误", "请输入用户名")
            return
            
        self.current_mode = 'register'
        self.face_samples = []
        self.start_camera()
        self.status_label.config(text="状态: 录入中 (需要采集20张人脸样本)")
        
    def start_verification(self):
        """开始人脸验证流程"""
        self.current_mode = 'verify'
        self.start_camera()
        self.status_label.config(text="状态: 验证中")
        
    def start_camera(self):
        """启动摄像头和视频处理线程"""
        self.is_running = True
        self.cap = cv2.VideoCapture(0)
        
        # 设置摄像头捕获分辨率
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.video_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.video_height)
        
        # 禁用开始按钮，启用停止按钮
        self.register_button.config(state=tk.DISABLED)
        self.verify_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # 在新线程中运行视频处理
        self.video_thread = threading.Thread(target=self.update_frame, daemon=True)
        self.video_thread.start()
        
    def stop_camera(self):
        """停止摄像头和视频处理"""
        self.is_running = False
        
        # 清除验证结果
        if hasattr(self, 'last_verify_result'):
            delattr(self, 'last_verify_result')
        
        # 等待视频线程结束
        if hasattr(self, 'video_thread') and self.video_thread.is_alive():
            self.video_thread.join(timeout=1.0)
        
        # 释放摄像头资源
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        
        # 清除显示
        if hasattr(self, 'video_label'):
            self.video_label.config(image='')
        
        # 恢复按钮状态
        if hasattr(self, 'register_button'):
            self.register_button.config(state=tk.NORMAL)
        if hasattr(self, 'verify_button'):
            self.verify_button.config(state=tk.NORMAL)
        if hasattr(self, 'stop_button'):
            self.stop_button.config(state=tk.DISABLED)
        
        # 更新状态
        if hasattr(self, 'status_label'):
            self.status_label.config(text="状态: 就绪")
        
    def update_frame(self):
        """更新视频帧"""
        try:
            while self.is_running and self.cap is not None:
                ret, frame = self.cap.read()
                if not ret:
                    print("无法读取视频帧")
                    break
                
                # 获取当前视频标签的大小
                label_width = self.video_label.winfo_width()
                label_height = self.video_label.winfo_height()
                
                if label_width > 1 and label_height > 1:  # 确保有效的尺寸
                    # 计算保持宽高比的新尺寸
                    frame_ratio = self.video_width / self.video_height
                    label_ratio = label_width / label_height
                    
                    if label_ratio > frame_ratio:
                        # 以高度为基准
                        new_height = label_height
                        new_width = int(new_height * frame_ratio)
                    else:
                        # 以宽度为基准
                        new_width = label_width
                        new_height = int(new_width / frame_ratio)
                    
                    # 调整帧大小
                    frame = cv2.resize(frame, (new_width, new_height))
                
                # 转换为灰度图像用于人脸检测
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # 检测人脸
                faces = self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(60, 60)
                )
                
                # 处理检测到的每个人脸
                for (x, y, w, h) in faces:
                    # 绘制边框
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    
                    if self.current_mode in ['register', 'recapture']:
                        self.handle_registration(gray[y:y+h, x:x+w])
                    elif self.current_mode == 'verify':
                        self.handle_verification(gray[y:y+h, x:x+w])
                
                # 添加状态颜色块
                status_color = None
                status_text = ""
                if self.current_mode == 'verify':
                    if hasattr(self, 'last_verify_result'):
                        if self.last_verify_result:
                            status_color = (0, 255, 0)  # 绿色，验证通过
                            status_text = "验证通过"
                        else:
                            status_color = (0, 0, 255)  # 红色，验证失败
                            status_text = "验证失败"
                elif self.current_mode in ['register', 'recapture']:
                    status_color = (255, 128, 0)  # 蓝色，录入/采集中
                    status_text = f"采集中: {len(self.face_samples)}/20"
                
                # 如果有状态颜色，绘制状态块和文字
                if status_color is not None:
                    # 计算状态块的位置和大小
                    block_height = 40
                    block_width = 150  # 增加宽度以适应中文
                    margin = 20
                    
                    # 在右上角绘制状态块
                    cv2.rectangle(
                        frame,
                        (frame.shape[1] - block_width - margin, margin),
                        (frame.shape[1] - margin, margin + block_height),
                        status_color,
                        -1  # 填充矩形
                    )
                    
                    # 使用PIL绘制中文文本
                    text_position = (
                        frame.shape[1] - block_width - margin + 10,
                        margin + 10
                    )
                    frame = self.draw_chinese_text(
                        frame,
                        status_text,
                        text_position,
                        (255, 255, 255)  # 白色文字
                    )
                
                # 直接更新GUI
                try:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(frame_rgb)
                    photo = ImageTk.PhotoImage(image=image)
                    self.video_label.config(image=photo)
                    self.video_label.image = photo
                except Exception as e:
                    print(f"GUI更新错误: {e}")
                
        except Exception as e:
            print(f"视频处理错误: {e}")
        finally:
            self.stop_camera()
            
    def handle_registration(self, face_roi):
        """
        处理人脸注册
        Args:
            face_roi: 人脸区域图像
        """
        try:
            if len(self.face_samples) < 20:
                face_roi = cv2.resize(face_roi, (100, 100))
                self.face_samples.append(face_roi)
                self.status_label.config(text=f"状态: 录入中 ({len(self.face_samples)}/20)")
                
                if len(self.face_samples) == 20:
                    if self.current_mode == 'recapture':
                        self.complete_recapture()
                    else:
                        self.complete_registration()
        except Exception as e:
            messagebox.showerror("错误", f"采集失败: {str(e)}")
            print(f"采集错误: {e}")
            self.stop_camera()
            
    def complete_registration(self):
        """完成人脸注册流程"""
        # 创建新用户
        user_id = len(self.users)
        self.users[user_id] = {
            'name': self.username_var.get(),
            'registered_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 训练人脸识别模型
        labels = [user_id] * len(self.face_samples)
        self.face_recognizer.train(self.face_samples, np.array(labels))
        
        # 保存模型和用户数据
        self.face_recognizer.save(self.model_path)
        self.save_users()
        self.update_users_list()
        
        messagebox.showinfo("成功", "人脸录入完成！")
        self.stop_camera()
        
    def handle_verification(self, face_roi):
        """
        处理人脸验证
        Args:
            face_roi: 人脸区域图像
        """
        try:
            face_roi = cv2.resize(face_roi, (100, 100))
            user_id, confidence = self.face_recognizer.predict(face_roi)
            
            if confidence < 65:  # 置信度阈值
                user_info = self.users.get(user_id)
                if user_info:
                    # 更新最后验证时间
                    user_info['last_verified'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.save_users()
                    self.status_label.config(text=f"验证成功: {user_info['name']} (置信度: {confidence:.2f})")
                    self.last_verify_result = True  # 记录验证结果
                else:
                    self.status_label.config(text="验证失败: 未识别")
                    self.last_verify_result = False
            else:
                self.status_label.config(text=f"验证失败: 未识别 (置信度: {confidence:.2f})")
                self.last_verify_result = False
        except Exception as e:
            print(f"验证错误: {e}")
            self.last_verify_result = False
            
    def on_user_select(self, event):
        """处理用户选择事件"""
        selection = self.users_listbox.curselection()
        if selection:
            index = selection[0]
            user_id = list(self.users.keys())[index]
            user = self.users[user_id]
            details = [
                f"用户ID: {user_id}",
                f"用户名: {user['name']}",
                f"注册时间: {user['registered_at']}",
                f"上次验证: {user.get('last_verified', '从未')}",
                f"上次更新: {user.get('updated_at', '从未')}"
            ]
            self.user_details_label.config(text="\n".join(details))
    
    def delete_selected_user(self):
        """删除选中的用户"""
        selection = self.users_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的用户")
            return
            
        if messagebox.askyesno("确认", "确定要删除选中的用户吗？"):
            index = selection[0]
            user_id = list(self.users.keys())[index]
            del self.users[user_id]
            self.save_users()
            self.update_users_list()
            self.user_details_label.config(text="")
            
            # 如果没有用户了，重新训练模型
            if not self.users:
                if os.path.exists(self.model_path):
                    os.remove(self.model_path)
                self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
            
    def rename_selected_user(self):
        """修改选中用户的用户名"""
        selection = self.users_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要修改的用户")
            return
            
        index = selection[0]
        user_id = list(self.users.keys())[index]
        user = self.users[user_id]
        
        # 创建修改用户名对话框
        dialog = tk.Toplevel(self.window)
        dialog.title("修改用户名")
        dialog.geometry("300x100")
        
        ttk.Label(dialog, text="新用户名:").pack(pady=5)
        new_name_var = tk.StringVar(value=user['name'])
        name_entry = ttk.Entry(dialog, textvariable=new_name_var)
        name_entry.pack(pady=5)
        
        def confirm():
            new_name = new_name_var.get().strip()
            if new_name:
                user['name'] = new_name
                self.save_users()
                self.update_users_list()
                dialog.destroy()
            else:
                messagebox.showwarning("警告", "用户名不能为空")
        
        ttk.Button(dialog, text="确定", command=confirm).pack(pady=5)
        
    def recapture_user_face(self):
        """重新采集用户人脸数据"""
        selection = self.users_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要重新采集的用户")
            return
        
        try:
            # 获取选中的用户ID
            index = selection[0]
            selected_text = self.users_listbox.get(index)
            # 使用正则表达式提取用户ID
            id_match = re.search(r'ID: (\d+)', selected_text)
            if not id_match:
                raise ValueError("无法获取用户ID")
            user_id = int(id_match.group(1))
            
            # 验证用户ID是否存在
            if user_id not in self.users:
                raise ValueError("用户ID不存在")
            
            # 确保摄像头已关闭
            if self.cap is not None:
                self.cap.release()
                self.cap = None
            
            # 设置重新采集模式
            self.current_mode = 'recapture'
            self.current_user_id = user_id
            self.face_samples = []
            
            # 启动摄像头前确保GUI已更新
            self.window.update()
            
            # 启动摄像头
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise ValueError("无法打开摄像头")
            
            self.is_running = True
            self.register_button.config(state=tk.DISABLED)
            self.verify_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            # 使用新线程处理视频流
            self.video_thread = threading.Thread(target=self.update_frame, daemon=True)
            self.video_thread.start()
            
            self.status_label.config(text="状态: 重新采集中 (需要采集20张人脸样本)")
            
        except Exception as e:
            messagebox.showerror("错误", f"重新采集失败: {str(e)}")
            print(f"重新采集错误: {e}")
            self.stop_camera()

    def complete_recapture(self):
        """完成重新采集流程"""
        try:
            # 确保有足够的样本
            if len(self.face_samples) < 20:
                messagebox.showerror("错误", "样本数量不足")
                return
            
            # 准备训练数据
            faces = np.array(self.face_samples)
            labels = np.array([self.current_user_id] * len(self.face_samples))
            
            # 重新创建并训练识别器
            self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
            
            # 加载现有模型（如果存在）
            if os.path.exists(self.model_path):
                self.face_recognizer.read(self.model_path)
            
            # 训练模型
            self.face_recognizer.train(faces, labels)
            
            # 更新用户信息
            self.users[self.current_user_id]['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 保存模型和用户数据
            self.face_recognizer.save(self.model_path)
            self.save_users()
            self.update_users_list()
            
            messagebox.showinfo("成功", "人脸重新采集完成！")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
            print(f"重新采集保存错误: {e}")
        finally:
            self.stop_camera()
        
    def on_search_change(self, *args):
        """处理搜索框内容变化"""
        search_text = self.search_var.get().lower()
        self.update_users_list(search_text)
            
    def __del__(self):
        """析构函数，确保释放摄像头资源"""
        if self.cap is not None:
            self.cap.release()

    def create_section(self, parent, title, font):
        """创建带标题的分区"""
        frame = ttk.LabelFrame(
            parent,
            text=title,
            style='Main.TFrame',
            padding=10
        )
        frame.pack(pady=5, fill=tk.X)
        return frame

    def create_button(self, parent, text, command, color, size='normal', **kwargs):
        """创建统一样式的按钮"""
        # 计算按钮大小
        padding_x = 15 if size == 'normal' else 10
        padding_y = 8 if size == 'normal' else 5
        font = self.fonts['normal'] if size == 'normal' else self.fonts['small']
        
        # 创建tk.Button
        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=font,
            fg=self.colors['text'],  # 文字颜色改为深灰色
            bg=self.colors[color],   # 背景色改为浅色
            activebackground=self.darken_color(self.colors[color]),  # 悬停时加深颜色
            activeforeground=self.colors['text'],  # 悬停时文字颜色保持不变
            relief='flat',  # 扁平化效果
            padx=padding_x,
            pady=padding_y,
            cursor='hand2',  # 鼠标悬停时显示手型
            **kwargs
        )
        
        # 绑定鼠标事件
        button.bind('<Enter>', lambda e: self.on_button_hover(e, self.colors[color]))
        button.bind('<Leave>', lambda e: self.on_button_leave(e, self.colors[color]))
        
        return button

    def darken_color(self, color):
        """使颜色变深"""
        # 将十六进制颜色转换为RGB
        color = color.lstrip('#')
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        
        # 使每个分量变深 20%
        factor = 0.8
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        
        # 转换回十六进制
        return f'#{r:02x}{g:02x}{b:02x}'

    def on_button_hover(self, event, color):
        """鼠标悬停时的效果"""
        event.widget.config(bg=self.darken_color(color))

    def on_button_leave(self, event, color):
        """鼠标离开时的效果"""
        event.widget.config(bg=color)

    def create_scrolled_listbox(self, parent):
        """创建带滚动条的列表框"""
        scrollbar = ttk.Scrollbar(parent)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(
            parent,
            yscrollcommand=scrollbar.set,
            font=self.fonts['normal'],
            bg='white',
            selectmode=tk.SINGLE,
            height=6,
            activestyle='none'
        )
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        return listbox

    def draw_chinese_text(self, frame, text, position, color):
        """使用PIL绘制中文文本"""
        # 转换图片为PIL格式
        frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        # 创建画布
        draw = ImageDraw.Draw(frame_pil)
        
        # 使用系统字体
        fontStyle = self.get_system_font()
        
        # 绘制文本
        draw.text(
            position,
            text,
            color,
            font=fontStyle,
            stroke_width=1
        )
        
        # 转换回OpenCV格式
        return cv2.cvtColor(np.asarray(frame_pil), cv2.COLOR_RGB2BGR)

    def get_system_font(self):
        """获取系统可用的中文字体"""
        try:
            # 尝试常见的中文字体
            font_paths = [
                "Arial Unicode.ttf",
                "msyh.ttc",  # 微软雅黑
                "STHeiti Light.ttc",  # macOS中文字体
                "PingFang.ttc",  # macOS中文字体
                "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",  # Linux字体
                "/System/Library/Fonts/STHeiti Light.ttc",  # macOS完整路径
            ]
            
            for font_path in font_paths:
                try:
                    return ImageFont.truetype(font_path, 20, encoding="utf-8")
                except:
                    continue
                
            # 如果上述字体都不可用，使用系统默认字体
            return ImageFont.load_default()
        except:
            return ImageFont.load_default()

def main():
    """主函数，创建并运行GUI应用"""
    root = tk.Tk()
    app = FaceRecognitionSystem(root)
    root.mainloop()

if __name__ == '__main__':
    main() 