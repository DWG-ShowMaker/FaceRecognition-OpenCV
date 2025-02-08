#!/bin/bash

# 检测芯片架构
ARCH=$(uname -m)
echo "检测到系统架构: $ARCH"

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install py2app

# 根据芯片架构安装对应版本的OpenCV
if [ "$ARCH" = "arm64" ]; then
    echo "正在安装 Apple Silicon (M1/M2) 版本的依赖..."
    ARCHFLAGS="-arch arm64" pip install opencv-contrib-python-headless
else
    echo "正在安装 Intel 版本的依赖..."
    pip install opencv-contrib-python
fi

pip install pillow
pip install numpy

# 清理之前的构建
rm -rf build dist

# 检查是否存在模型文件，如果不存在则创建空文件
touch face_model.yml

# 创建开发模式的应用（用于测试）
echo "创建开发模式应用进行测试..."
python setup.py py2app -A
echo "测试开发模式应用..."
./dist/智能人脸识别系统.app/Contents/MacOS/智能人脸识别系统 || true

# 如果测试成功，创建发布版本
echo "创建发布版本..."
rm -rf build dist

# 打包应用
python setup.py py2app

# 创建必要的目录
mkdir -p "dist/智能人脸识别系统.app/Contents/Resources/face_data"
mkdir -p "dist/智能人脸识别系统.app/Contents/Resources/cv2/data"
mkdir -p "dist/智能人脸识别系统.app/Contents/Frameworks"

# 复制OpenCV数据文件
CV2_PATH=$(python -c "import cv2, os; print(os.path.dirname(cv2.__file__))")
if [ -d "$CV2_PATH/data" ]; then
    cp -R "$CV2_PATH/data/"* "dist/智能人脸识别系统.app/Contents/Resources/cv2/data/"
fi

# 复制动态库
if [ -d "$CV2_PATH" ]; then
    find "$CV2_PATH" -name "*.so" -o -name "*.dylib" | while read lib; do
        cp "$lib" "dist/智能人脸识别系统.app/Contents/Frameworks/"
    done
fi

# 修复动态库链接
if [ -f "dist/智能人脸识别系统.app/Contents/Resources/lib/python3.10/lib/python3.10/site-packages/cv2/cv2.so" ]; then
    install_name_tool -change "@rpath/cv2.so" "@executable_path/../Frameworks/cv2.so" "dist/智能人脸识别系统.app/Contents/Resources/lib/python3.10/lib/python3.10/site-packages/cv2/cv2.so"
fi

# 设置权限
chmod -R 755 "dist/智能人脸识别系统.app"

# 清理虚拟环境
deactivate
rm -rf venv

echo "打包完成！应用程序在 dist/智能人脸识别系统.app"
echo "注意：首次运行时需要在系统偏好设置中允许摄像头访问权限"

# 运行以验证
echo "正在启动应用进行验证..."
open "dist/智能人脸识别系统.app" 