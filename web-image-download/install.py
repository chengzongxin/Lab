"""
安装脚本
帮助用户快速设置图片下载工具的环境
"""

import subprocess
import sys
import os


def run_command(command, description):
    """
    运行命令并显示进度
    
    Args:
        command (list): 命令列表
        description (str): 命令描述
        
    Returns:
        bool: 成功返回True，失败返回False
    """
    print(f"\n{'='*50}")
    print(f"正在{description}...")
    print(f"命令: {' '.join(command)}")
    print('='*50)
    
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ {description}成功!")
            if result.stdout:
                print("输出:", result.stdout)
            return True
        else:
            print(f"✗ {description}失败!")
            if result.stderr:
                print("错误:", result.stderr)
            return False
            
    except Exception as e:
        print(f"✗ {description}出错: {e}")
        return False


def check_python_version():
    """
    检查Python版本
    
    Returns:
        bool: 版本符合要求返回True，否则返回False
    """
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("✗ Python版本过低，需要Python 3.7或更高版本")
        return False
    
    print("✓ Python版本符合要求")
    return True


def install_dependencies():
    """
    安装Python依赖包
    
    Returns:
        bool: 安装成功返回True，否则返回False
    """
    print("\n开始安装Python依赖包...")
    
    # 升级pip
    if not run_command([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], "升级pip"):
        print("警告: pip升级失败，继续安装依赖...")
    
    # 安装依赖
    if not run_command([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], "安装依赖包"):
        return False
    
    return True


def install_playwright_browsers():
    """
    安装Playwright浏览器
    
    Returns:
        bool: 安装成功返回True，否则返回False
    """
    print("\n开始安装Playwright浏览器...")
    
    # 安装Chromium浏览器
    if not run_command([sys.executable, '-m', 'playwright', 'install', 'chromium'], "安装Chromium浏览器"):
        return False
    
    return True


def test_installation():
    """
    测试安装是否成功
    
    Returns:
        bool: 测试成功返回True，否则返回False
    """
    print("\n开始测试安装...")
    
    # 测试导入模块
    test_modules = [
        ('requests', 'requests'),
        ('beautifulsoup4', 'bs4'),
        ('Pillow', 'PIL'),
        ('playwright', 'playwright'),
        ('lxml', 'lxml')
    ]
    
    for package_name, import_name in test_modules:
        try:
            __import__(import_name)
            print(f"✓ {package_name} 导入成功")
        except ImportError as e:
            print(f"✗ {package_name} 导入失败: {e}")
            return False
    
    # 测试Playwright浏览器
    try:
        result = subprocess.run([sys.executable, '-m', 'playwright', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Playwright版本: {result.stdout.strip()}")
        else:
            print("✗ Playwright版本检查失败")
            return False
    except Exception as e:
        print(f"✗ Playwright测试失败: {e}")
        return False
    
    return True


def main():
    """
    主安装函数
    """
    print("="*60)
    print("网页图片下载工具 - 环境安装脚本")
    print("="*60)
    
    # 检查Python版本
    if not check_python_version():
        print("\n请升级Python版本后重试")
        return
    
    # 安装依赖
    if not install_dependencies():
        print("\n依赖安装失败，请检查网络连接或手动安装")
        return
    
    # 安装Playwright浏览器
    print("\n是否安装Playwright浏览器？(y/n): ", end="")
    response = input().lower().strip()
    
    if response in ['y', 'yes', '是']:
        if not install_playwright_browsers():
            print("\n浏览器安装失败，但基本功能仍可使用")
            print("您可以稍后手动运行: playwright install")
    
    # 测试安装
    if not test_installation():
        print("\n安装测试失败，请检查错误信息")
        return
    
    print("\n" + "="*60)
    print("🎉 安装完成！")
    print("="*60)
    print("\n现在您可以运行以下命令启动程序:")
    print("python main.py")
    print("\n或者运行测试:")
    print("python test_downloader.py")
    print("\n使用说明:")
    print("1. 启动程序后，输入网站地址")
    print("2. 选择下载模式（推荐使用自动模式）")
    print("3. 设置下载路径和最大数量")
    print("4. 点击开始下载")
    print("\n对于Redbubble等现代网站，建议使用高级模式")


if __name__ == "__main__":
    main() 