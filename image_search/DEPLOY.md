Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
.\venv\Scripts\activate
python.py

如果运行“.\venv\Scripts\activate”报错
在当前 PowerShell 会话中允许执行脚本：
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
允许当前用户执行本地脚本：
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned