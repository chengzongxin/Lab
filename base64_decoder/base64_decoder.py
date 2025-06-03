import base64
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sys

class Base64Decoder:
    def __init__(self):
        # 创建主窗口
        self.window = tk.Tk()
        self.window.title("Base64解码工具")
        self.window.geometry("800x500")  # 增加窗口高度
        
        # 设置窗口图标（如果有的话）
        if getattr(sys, 'frozen', False):
            # 打包后的路径
            application_path = sys._MEIPASS
        else:
            # 开发环境路径
            application_path = os.path.dirname(os.path.abspath(__file__))
            
        # 创建主框架
        main_frame = tk.Frame(self.window)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # 创建按钮框架
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        # 创建单个文件按钮
        self.select_button = tk.Button(
            button_frame, 
            text="选择单个文件", 
            command=self.select_file,
            width=20,
            height=2
        )
        self.select_button.pack(side=tk.LEFT, padx=5)
        
        # 创建批量处理按钮
        self.batch_button = tk.Button(
            button_frame,
            text="批量处理文件夹",
            command=self.select_directory,
            width=20,
            height=2
        )
        self.batch_button.pack(side=tk.LEFT, padx=5)
        
        # 创建进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.pack(fill=tk.X, pady=10)
        
        # 创建状态标签
        self.status_label = tk.Label(
            main_frame, 
            text="请选择要解码的文件或文件夹",
            wraplength=700  # 文本自动换行
        )
        self.status_label.pack(pady=10)
        
        # 创建日志文本框
        self.log_text = tk.Text(main_frame, height=10, width=70)
        self.log_text.pack(pady=10)
        
        # 添加版本信息
        version_label = tk.Label(
            main_frame,
            text="v1.1.0",
            fg="gray"
        )
        version_label.pack(side='bottom', pady=10)
        
    def log_message(self, message):
        """添加日志信息到文本框"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        
    def select_file(self):
        """处理单个文件"""
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                self.decode_file(file_path)
            except Exception as e:
                self.status_label.config(text=f"错误: {str(e)}")
                messagebox.showerror("错误", f"解码失败: {str(e)}")
                
    def select_directory(self):
        """选择文件夹进行批量处理"""
        directory = filedialog.askdirectory()
        if directory:
            try:
                self.batch_decode_directory(directory)
            except Exception as e:
                self.status_label.config(text=f"错误: {str(e)}")
                messagebox.showerror("错误", f"批量处理失败: {str(e)}")
                
    def decode_file(self, file_path):
        """解码单个文件"""
        try:
            # 读取文件内容
            with open(file_path, 'r') as file:
                base64_content = file.read().strip()
            
            # 解码Base64内容
            decoded_content = base64.b64decode(base64_content)
            
            # 创建输出文件名
            output_path = os.path.splitext(file_path)[0] + "_decoded" + os.path.splitext(file_path)[1]
            
            # 写入解码后的内容
            with open(output_path, 'wb') as file:
                file.write(decoded_content)
            
            self.log_message(f"成功解码: {os.path.basename(file_path)}")
            return True
        except Exception as e:
            self.log_message(f"解码失败 {os.path.basename(file_path)}: {str(e)}")
            return False
            
    def batch_decode_directory(self, directory):
        """批量处理文件夹中的文件"""
        # 清空日志
        self.log_text.delete(1.0, tk.END)
        self.log_message(f"开始处理文件夹: {directory}")
        
        # 获取所有文件
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        total_files = len(files)
        
        if total_files == 0:
            self.log_message("文件夹为空")
            return
            
        success_count = 0
        fail_count = 0
        
        # 处理每个文件
        for index, file in enumerate(files, 1):
            file_path = os.path.join(directory, file)
            
            # 更新进度条
            progress = (index / total_files) * 100
            self.progress_var.set(progress)
            self.window.update()
            
            # 解码文件
            if self.decode_file(file_path):
                success_count += 1
            else:
                fail_count += 1
                
        # 显示处理结果
        result_message = f"处理完成！成功: {success_count}, 失败: {fail_count}"
        self.status_label.config(text=result_message)
        self.log_message(result_message)
        messagebox.showinfo("完成", result_message)
    
    def run(self):
        # 设置窗口在屏幕中央
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # 运行主程序
        self.window.mainloop()

def main():
    app = Base64Decoder()
    app.run()

if __name__ == "__main__":
    main() 