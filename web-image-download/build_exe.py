"""
exe打包脚本
将图片下载工具打包成可执行文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_pyinstaller():
    """
    检查PyInstaller是否已安装
    
    Returns:
        bool: 已安装返回True，否则返回False
    """
    try:
        import PyInstaller
        return True
    except ImportError:
        return False


def install_pyinstaller():
    """
    安装PyInstaller
    
    Returns:
        bool: 安装成功返回True，否则返回False
    """
    try:
        print("正在安装PyInstaller...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
        print("PyInstaller安装成功!")
        return True
    except Exception as e:
        print(f"PyInstaller安装失败: {e}")
        return False


def create_spec_file():
    """
    创建PyInstaller的spec文件
    
    Returns:
        str: spec文件路径
    """
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'playwright.async_api',
        'playwright.sync_api',
        'playwright._impl._browser_type',
        'playwright._impl._browser',
        'playwright._impl._page',
        'playwright._impl._context',
        'playwright._impl._connection',
        'playwright._impl._transport',
        'playwright._impl._driver',
        'playwright._impl._playwright',
        'playwright._impl._browser_context',
        'playwright._impl._frame',
        'playwright._impl._element_handle',
        'playwright._impl._js_handle',
        'playwright._impl._network',
        'playwright._impl._cdp_session',
        'playwright._impl._api_types',
        'playwright._impl._api_structures',
        'playwright._impl._errors',
        'playwright._impl._event_context_manager',
        'playwright._impl._helper',
        'playwright._impl._impl_to_api_mapping',
        'playwright._impl._local_utils',
        'playwright._impl._object_factory',
        'playwright._impl._process',
        'playwright._impl._selectors',
        'playwright._impl._timeout_settings',
        'playwright._impl._types',
        'playwright._impl._utils',
        'playwright._impl._wait_helper',
        'playwright._impl._ws',
        'playwright._impl._ws_server',
        'playwright._impl._browser_type_context_manager',
        'playwright._impl._browser_context_context_manager',
        'playwright._impl._page_context_manager',
        'playwright._impl._frame_context_manager',
        'playwright._impl._element_handle_context_manager',
        'playwright._impl._js_handle_context_manager',
        'playwright._impl._cdp_session_context_manager',
        'playwright._impl._network_context_manager',
        'playwright._impl._browser_context_context_manager',
        'playwright._impl._page_context_manager',
        'playwright._impl._frame_context_manager',
        'playwright._impl._element_handle_context_manager',
        'playwright._impl._js_handle_context_manager',
        'playwright._impl._cdp_session_context_manager',
        'playwright._impl._network_context_manager',
        'requests',
        'bs4',
        'PIL',
        'PIL._tkinter_finder',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'asyncio',
        'threading',
        'urllib.parse',
        'pathlib',
        'subprocess',
        'shutil',
        're',
        'io',
        'time',
        'json',
        'base64',
        'hashlib',
        'zlib',
        'gzip',
        'bz2',
        'lzma',
        'zipfile',
        'tarfile',
        'tempfile',
        'glob',
        'fnmatch',
        'os.path',
        'sys',
        'traceback',
        'logging',
        'warnings',
        'weakref',
        'functools',
        'itertools',
        'collections',
        'copy',
        'pickle',
        'shelve',
        'marshal',
        'struct',
        'array',
        'math',
        'random',
        'statistics',
        'decimal',
        'fractions',
        'numbers',
        'datetime',
        'calendar',
        'time',
        'locale',
        'gettext',
        'unicodedata',
        'string',
        're',
        'difflib',
        'textwrap',
        'unicodedata',
        'stringprep',
        'readline',
        'rlcompleter',
        'code',
        'codeop',
        'keyword',
        'token',
        'tokenize',
        'tabnanny',
        'py_compile',
        'pyclbr',
        'py_compile',
        'compileall',
        'dis',
        'pickletools',
        'formatter',
        'msilib',
        'msvcrt',
        'winsound',
        'winreg',
        'win32api',
        'win32con',
        'win32gui',
        'win32process',
        'win32security',
        'win32service',
        'win32serviceutil',
        'win32timezone',
        'pythoncom',
        'pywintypes',
        'win32com',
        'win32com.client',
        'win32com.server',
        'win32com.universal',
        'win32com.client.gencache',
        'win32com.client.util',
        'win32com.client.dynamic',
        'win32com.client.genpy',
        'win32com.client.build',
        'win32com.client.scripting',
        'win32com.client.makepy',
        'win32com.client.selecttlb',
        'win32com.client.CLSIDToClass',
        'win32com.client.Dispatch',
        'win32com.client.DispatchEx',
        'win32com.client.GetObject',
        'win32com.client.GetActiveObject',
        'win32com.client.CoCreateInstance',
        'win32com.client.CoGetClassObject',
        'win32com.client.CoGetObject',
        'win32com.client.CoCreateInstanceEx',
        'win32com.client.CoGetClassObjectEx',
        'win32com.client.CoGetObjectEx',
        'win32com.client.CoCreateInstanceFromFile',
        'win32com.client.CoGetClassObjectFromFile',
        'win32com.client.CoGetObjectFromFile',
        'win32com.client.CoCreateInstanceFromString',
        'win32com.client.CoGetClassObjectFromString',
        'win32com.client.CoGetObjectFromString',
        'win32com.client.CoCreateInstanceFromURL',
        'win32com.client.CoGetClassObjectFromURL',
        'win32com.client.CoGetObjectFromURL',
        'win32com.client.CoCreateInstanceFromMoniker',
        'win32com.client.CoGetClassObjectFromMoniker',
        'win32com.client.CoGetObjectFromMoniker',
        'win32com.client.CoCreateInstanceFromProgID',
        'win32com.client.CoGetClassObjectFromProgID',
        'win32com.client.CoGetObjectFromProgID',
        'win32com.client.CoCreateInstanceFromCLSID',
        'win32com.client.CoGetClassObjectFromCLSID',
        'win32com.client.CoGetObjectFromCLSID',
        'win32com.client.CoCreateInstanceFromIID',
        'win32com.client.CoGetClassObjectFromIID',
        'win32com.client.CoGetObjectFromIID',
        'win32com.client.CoCreateInstanceFromInterface',
        'win32com.client.CoGetClassObjectFromInterface',
        'win32com.client.CoGetObjectFromInterface',
        'win32com.client.CoCreateInstanceFromType',
        'win32com.client.CoGetClassObjectFromType',
        'win32com.client.CoGetObjectFromType',
        'win32com.client.CoCreateInstanceFromTypeLib',
        'win32com.client.CoGetClassObjectFromTypeLib',
        'win32com.client.CoGetObjectFromTypeLib',
        'win32com.client.CoCreateInstanceFromTypeInfo',
        'win32com.client.CoGetClassObjectFromTypeInfo',
        'win32com.client.CoGetObjectFromTypeInfo',
        'win32com.client.CoCreateInstanceFromTypeLibInfo',
        'win32com.client.CoGetClassObjectFromTypeLibInfo',
        'win32com.client.CoGetObjectFromTypeLibInfo',
        'win32com.client.CoCreateInstanceFromTypeInfoEx',
        'win32com.client.CoGetClassObjectFromTypeInfoEx',
        'win32com.client.CoGetObjectFromTypeInfoEx',
        'win32com.client.CoCreateInstanceFromTypeLibInfoEx',
        'win32com.client.CoGetClassObjectFromTypeLibInfoEx',
        'win32com.client.CoGetObjectFromTypeLibInfoEx',
        'win32com.client.CoCreateInstanceFromTypeLibInfoEx2',
        'win32com.client.CoGetClassObjectFromTypeLibInfoEx2',
        'win32com.client.CoGetObjectFromTypeLibInfoEx2',
        'win32com.client.CoCreateInstanceFromTypeLibInfoEx3',
        'win32com.client.CoGetClassObjectFromTypeLibInfoEx3',
        'win32com.client.CoGetObjectFromTypeLibInfoEx3',
        'win32com.client.CoCreateInstanceFromTypeLibInfoEx4',
        'win32com.client.CoGetClassObjectFromTypeLibInfoEx4',
        'win32com.client.CoGetObjectFromTypeLibInfoEx4',
        'win32com.client.CoCreateInstanceFromTypeLibInfoEx5',
        'win32com.client.CoGetClassObjectFromTypeLibInfoEx5',
        'win32com.client.CoGetObjectFromTypeLibInfoEx5',
        'win32com.client.CoCreateInstanceFromTypeLibInfoEx6',
        'win32com.client.CoGetClassObjectFromTypeLibInfoEx6',
        'win32com.client.CoGetObjectFromTypeLibInfoEx6',
        'win32com.client.CoCreateInstanceFromTypeLibInfoEx7',
        'win32com.client.CoGetClassObjectFromTypeLibInfoEx7',
        'win32com.client.CoGetObjectFromTypeLibInfoEx7',
        'win32com.client.CoCreateInstanceFromTypeLibInfoEx8',
        'win32com.client.CoGetClassObjectFromTypeLibInfoEx8',
        'win32com.client.CoGetObjectFromTypeLibInfoEx8',
        'win32com.client.CoCreateInstanceFromTypeLibInfoEx9',
        'win32com.client.CoGetClassObjectFromTypeLibInfoEx9',
        'win32com.client.CoGetObjectFromTypeLibInfoEx9',
        'win32com.client.CoCreateInstanceFromTypeLibInfoEx10',
        'win32com.client.CoGetClassObjectFromTypeLibInfoEx10',
        'win32com.client.CoGetObjectFromTypeLibInfoEx10',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='网页图片下载工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
'''
    
    spec_file = 'image_downloader.spec'
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    return spec_file


def build_exe():
    """
    构建exe文件
    
    Returns:
        bool: 构建成功返回True，否则返回False
    """
    try:
        print("=" * 60)
        print("开始构建exe文件...")
        print("=" * 60)
        
        # 检查PyInstaller
        if not check_pyinstaller():
            print("PyInstaller未安装，正在安装...")
            if not install_pyinstaller():
                return False
        
        # 创建spec文件
        spec_file = create_spec_file()
        print(f"创建spec文件: {spec_file}")
        
        # 构建exe
        print("正在构建exe文件，这可能需要几分钟...")
        cmd = [sys.executable, '-m', 'PyInstaller', '--clean', spec_file]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ exe文件构建成功!")
            
            # 检查输出文件
            exe_path = Path('dist/网页图片下载工具.exe')
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"exe文件位置: {exe_path.absolute()}")
                print(f"文件大小: {size_mb:.1f} MB")
                
                # 创建发布包
                create_release_package()
                
                return True
            else:
                print("❌ exe文件未找到")
                return False
        else:
            print("❌ exe文件构建失败!")
            print("错误信息:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 构建过程出错: {e}")
        return False


def create_release_package():
    """
    创建发布包
    """
    try:
        print("\n正在创建发布包...")
        
        # 创建发布目录
        release_dir = Path('release')
        release_dir.mkdir(exist_ok=True)
        
        # 复制exe文件
        exe_source = Path('dist/网页图片下载工具.exe')
        exe_dest = release_dir / '网页图片下载工具.exe'
        
        if exe_source.exists():
            shutil.copy2(exe_source, exe_dest)
            print(f"✅ 复制exe文件到: {exe_dest}")
        
        # 创建说明文件
        readme_content = '''网页图片下载工具 - 使用说明

1. 首次运行
   - 双击"网页图片下载工具.exe"启动程序
   - 首次启动可能需要几分钟时间，请耐心等待
   - 程序会自动下载必要的浏览器组件

2. 使用说明
   - 输入要下载图片的网站地址
   - 选择下载模式（推荐使用自动模式）
   - 设置下载路径和最大数量
   - 点击开始下载

3. 注意事项
   - 确保网络连接稳定
   - 某些网站可能有访问限制
   - 下载速度取决于网络状况

4. 故障排除
   - 如果程序无法启动，请检查杀毒软件设置
   - 如果下载失败，请尝试使用不同的下载模式
   - 确保有足够的磁盘空间

5. 技术支持
   - 如有问题，请查看程序内的错误信息
   - 可以尝试重新下载程序

版本: 1.0
构建时间: {build_time}
'''.format(build_time=__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        readme_file = release_dir / '使用说明.txt'
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"✅ 创建说明文件: {readme_file}")
        
        # 创建安装脚本
        install_script = release_dir / 'install_browser.bat'
        install_content = '''@echo off
echo 正在安装浏览器组件...
echo 这可能需要几分钟时间，请耐心等待...
echo.

REM 检查是否以管理员身份运行
net session >nul 2>&1
if %errorLevel% == 0 (
    echo 检测到管理员权限
) else (
    echo 警告: 建议以管理员身份运行此脚本
    pause
)

REM 运行exe文件，让它自动安装浏览器组件
echo 启动程序进行自动安装...
"网页图片下载工具.exe"

echo.
echo 安装完成！
pause
'''
        
        with open(install_script, 'w', encoding='gbk') as f:
            f.write(install_content)
        
        print(f"✅ 创建安装脚本: {install_script}")
        
        print(f"\n🎉 发布包创建完成!")
        print(f"发布目录: {release_dir.absolute()}")
        print(f"包含文件:")
        print(f"  - 网页图片下载工具.exe")
        print(f"  - 使用说明.txt")
        print(f"  - install_browser.bat")
        
    except Exception as e:
        print(f"❌ 创建发布包失败: {e}")


def main():
    """
    主函数
    """
    print("网页图片下载工具 - exe打包脚本")
    print("=" * 60)
    
    # 检查必要文件
    required_files = ['main.py', 'gui.py', 'downloader.py', 'playwright_downloader.py']
    missing_files = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少必要文件: {', '.join(missing_files)}")
        return
    
    print("✅ 所有必要文件检查通过")
    
    # 构建exe
    if build_exe():
        print("\n🎉 打包完成!")
        print("\n使用说明:")
        print("1. 发布包位于 'release' 目录")
        print("2. 将整个 'release' 目录分发给用户")
        print("3. 用户双击 exe 文件即可运行")
        print("4. 首次运行会自动安装浏览器组件")
    else:
        print("\n❌ 打包失败，请检查错误信息")


if __name__ == "__main__":
    main() 