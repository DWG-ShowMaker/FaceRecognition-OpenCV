# 智能人脸识别系统

这是一个使用OpenCV和Python实现的人脸识别系统，支持人脸录入和验证功能，具有现代化的图形界面。支持 Intel 和 Apple Silicon (M1/M2) 芯片的 Mac 系统。

## 功能特性

- 实时摄像头人脸检测
- 人脸特征录入和验证
- 完整的用户管理系统：
  - 添加新用户
  - 删除现有用户
  - 修改用户信息
  - 重新采集人脸数据
- 用户验证历史记录
- 实时状态显示和视觉反馈：
  - 绿色状态块：验证通过
  - 红色状态块：验证失败
  - 蓝色状态块：录入/采集中
- 响应式图形用户界面(GUI)：
  - 自适应窗口大小
  - 支持深色模式
  - 现代化界面设计
- 用户搜索功能（实时过滤）
- 多线程处理保证界面流畅

## 技术栈

- Python 3.x
- OpenCV-Python (图像处理和人脸识别)
  - Intel Mac: opencv-contrib-python
  - M1/M2 Mac: opencv-contrib-python-headless
- tkinter (GUI界面)
- PIL/Pillow (图像处理)
- Threading (多线程处理)
- LBPH人脸识别算法

## 系统要求

- macOS 10.13 或更高版本
- Python 3.x
- 摄像头设备
- 支持 Intel 和 Apple Silicon (M1/M2) 芯片

## 安装依赖

1. 克隆项目：
   ```bash
   git clone <repository_url>
   cd <project_directory>
   ```

2. 创建虚拟环境（推荐）：
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 开发环境运行

1. 确保已安装所有依赖
2. 在命令行中进入程序所在目录
3. 运行以下命令启动程序：
   ```bash
   python face_detector.py
   ```

## 打包说明

### 环境要求

- macOS 10.13 或更高版本
- Python 3.x
- py2app

### 打包步骤

1. 给打包脚本添加执行权限：
   ```bash
   chmod +x build_app.sh
   ```

2. 运行打包脚本：
   ```bash
   ./build_app.sh
   ```

脚本会自动：
- 检测系统架构（Intel/M1）
- 安装对应版本的依赖
- 创建开发模式应用进行测试
- 创建发布版本
- 复制必要的资源文件
- 修复动态库链接
- 设置正确的权限

### 打包文件说明

- `setup.py`: py2app打包配置文件
- `build_app.sh`: 应用程序打包脚本
- `requirements.txt`: 项目依赖列表
- `face_detector.py`: 主程序文件

## 使用说明

1. 程序启动后会显示GUI界面，包含：
   - 左侧：摄像头视频显示区域（自适应大小）
   - 右侧：控制面板
     - 用户信息输入
     - 功能按钮
     - 状态显示
     - 用户管理区域

2. 人脸录入：
   - 输入用户名
   - 点击"录入人脸"按钮
   - 保持面部在摄像头前，系统会自动采集20张人脸样本
   - 右上角蓝色状态块显示采集进度
   - 采集完成后自动保存

3. 人脸验证：
   - 点击"开始验证"按钮
   - 将面部对准摄像头
   - 系统会实时显示验证结果
   - 右上角状态块显示验证结果（绿色为通过，红色为失败）

4. 用户管理：
   - 支持用户搜索（实时过滤）
   - 选择用户后可以：
     - 删除用户
     - 修改用户名
     - 重新采集人脸
   - 显示用户详细信息：
     - 用户ID
     - 注册时间
     - 最后验证时间
     - 最后更新时间

## 项目结构

```
.
├── README.md               # 项目说明文档
├── face_detector.py        # 主程序文件
├── setup.py               # 打包配置文件
├── build_app.sh           # 打包脚本
├── requirements.txt       # 项目依赖
├── face_data/            # 用户数据目录
│   └── users.pkl         # 用户信息文件
└── face_model.yml        # 人脸识别模型文件
```

## 注意事项

1. 确保摄像头可用且已授权
2. 录入人脸时保持适当的光线条件
3. 录入时尽量展示不同角度的面部表情
4. 验证时保持自然表情
5. 首次使用时需要先录入人脸
6. 程序会自动保存用户数据和训练模型
7. 对于 M1/M2 Mac，使用 headless 版本的 OpenCV 可能需要额外安装 XQuartz

## 数据存储

- 用户数据存储在 `face_data` 目录下
- 人脸识别模型保存为 `face_model.yml`
- 用户信息保存在 `face_data/users.pkl` 文件中

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

[MIT License](LICENSE)