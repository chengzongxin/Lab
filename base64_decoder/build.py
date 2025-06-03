import PyInstaller.__main__
import sys
import os

# 确定应用图标路径（可选）
# icon_path = os.path.join('assets', 'icon.icns')  # Mac图标文件

PyInstaller.__main__.run([
    'base64_decoder.py',
    '--name=Base64Decoder',
    '--windowed',  # 不显示终端窗口
    '--onefile',   # 打包成单个文件
    '--clean',     # 清理临时文件
    # '--icon=' + icon_path,  # 如果有图标的话
    '--add-data=README.md:.',  # 包含README文件
    '--noconfirm',  # 不询问确认
]) 