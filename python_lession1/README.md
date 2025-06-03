source myenv/bin/activate  # 激活虚拟环境
python main1.py  # 使用虚拟环境的 Python 和库
python main2.py  # 同一虚拟环境可用于多个脚本
deactivate  # 退出虚拟环境（可选）

虚拟环境与文件位置无关：无论 .py 文件放在项目目录的哪个位置，只要在激活虚拟环境后运行，就会使用虚拟环境的 Python。
必须先激活环境：每次打开新终端窗口后，需要重新激活虚拟环境才能使用其中的库。
多个脚本共享环境：同一虚拟环境可以用于项目目录下的所有脚本。


### 启动项目
source myenv/bin/activate
python main2.py  
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug


### 打包