你记得加下面两个命令解除限制
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
或者
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

运行程序：
.\venv\Scripts\activate
python.py