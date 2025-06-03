#!/bin/bash

# 检查虚拟环境是否存在
if [ ! -d "jpush_env" ]; then
    echo "创建虚拟环境..."
    python3 -m venv jpush_env
fi

# 激活虚拟环境
source jpush_env/bin/activate

# 安装依赖
pip install requests >/dev/null 2>&1

# 运行推送脚本，传递所有参数
python jpush_api_2.py "$@"

# 退出虚拟环境
deactivate 