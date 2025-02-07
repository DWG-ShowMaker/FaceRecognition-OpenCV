#!/bin/bash

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install py2app
pip install opencv-contrib-python
pip install pillow

# 清理之前的构建
rm -rf build dist

# 打包应用
python setup.py py2app

# 复制必要的文件
mkdir -p "dist/FaceRecognition.app/Contents/Resources/face_data"

# 如果有自定义图标，复制图标文件
# cp app_icon.icns "dist/FaceRecognition.app/Contents/Resources/"

# 清理虚拟环境
deactivate
rm -rf venv

echo "打包完成！应用程序在 dist/FaceRecognition.app" 