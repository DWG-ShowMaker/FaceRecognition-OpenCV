#!/bin/bash

# 安装 create-dmg
brew install create-dmg

# 创建 DMG
create-dmg \
  --volname "人脸识别系统" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --icon "FaceRecognition.app" 200 190 \
  --hide-extension "FaceRecognition.app" \
  --app-drop-link 600 185 \
  "FaceRecognition.dmg" \
  "dist/" 