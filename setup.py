from setuptools import setup
import os
import sys
import cv2
import glob
import site
import shutil

# 获取OpenCV库的路径
cv2_path = os.path.dirname(cv2.__file__)

# 获取所有OpenCV相关的文件
def get_cv2_files():
    cv2_files = []
    # 添加haar cascade文件
    cascade_path = os.path.join(cv2_path, 'data')
    if os.path.exists(cascade_path):
        for xml in glob.glob(os.path.join(cascade_path, '*.xml')):
            cv2_files.append(xml)
    return cv2_files

# 获取所有需要的动态库
def get_dylibs():
    dylibs = []
    cv2_dir = os.path.dirname(cv2.__file__)
    for root, dirs, files in os.walk(cv2_dir):
        for file in files:
            if file.endswith('.so') or file.endswith('.dylib'):
                dylibs.append(os.path.join(root, file))
    return dylibs

APP = ['face_detector.py']
DATA_FILES = [
    ('face_data', []),
    ('cv2/data', get_cv2_files()),  # OpenCV数据文件
    ('lib', get_dylibs()),  # 动态库文件
]

# 如果存在图标文件则添加到配置中
icon_file = 'app_icon.icns'
plist = {
    'CFBundleName': "人脸识别系统",
    'CFBundleShortVersionString': "1.0.0",
    'CFBundleVersion': "1.0.0",
    'CFBundleIdentifier': "com.yourcompany.facerecognition",
    'NSCameraUsageDescription': '需要访问摄像头以进行人脸识别',
    'NSHighResolutionCapable': True,
    'LSMinimumSystemVersion': '10.13',  # 添加最低系统要求
    'NSRequiresAquaSystemAppearance': 'No',  # 支持深色模式
    'NSMicrophoneUsageDescription': '不需要访问麦克风',
}

OPTIONS = {
    'argv_emulation': False,  # 修改为False
    'packages': [
        'cv2',
        'numpy',
        'PIL',
        'tkinter'
    ],
    'includes': [
        'PIL',
        'PIL._imagingtk',
        'PIL._tkinter_finder',
        'numpy',
        'cv2',
        'platform',
        'os',
        'sys',
        're',
        'threading',
        'datetime',
        'pickle'
    ],
    'resources': get_cv2_files(),
    'frameworks': get_dylibs(),  # 添加动态库
    'plist': plist,
    'prefer_ppc': False,
    'semi_standalone': False,  # 改回False
    'site_packages': True,  # 包含site-packages
    'strip': False,  # 不strip以保留调试信息
    'excludes': [
        'matplotlib',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
        'pandas',
        'scipy',
        'sklearn',
        'tensorflow',
        'torch'
    ],  # 排除不需要的包
}

# 只有在图标文件存在时才添加到配置中
if os.path.exists(icon_file):
    OPTIONS['iconfile'] = icon_file

setup(
    name="智能人脸识别系统",
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
) 