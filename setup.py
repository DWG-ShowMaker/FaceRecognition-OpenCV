from setuptools import setup

APP = ['face_detector.py']
DATA_FILES = [
    ('', ['face_model.yml']),  # 包含模型文件
    ('face_data', []),  # 创建空的face_data目录
]
OPTIONS = {
    'argv_emulation': True,
    'packages': ['cv2', 'numpy', 'PIL'],
    'iconfile': 'app_icon.icns',  # 如果你有应用图标的话
    'plist': {
        'CFBundleName': "人脸识别系统",
        'CFBundleShortVersionString': "1.0.0",
        'CFBundleVersion': "1.0.0",
        'CFBundleIdentifier': "com.yourcompany.facerecognition",
        'NSCameraUsageDescription': '需要访问摄像头以进行人脸识别',
        'NSHighResolutionCapable': True
    }
}

setup(
    name="FaceRecognition",
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
) 