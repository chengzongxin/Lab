print(r"this is a line \n")
print("this is a line \n") #这里的 r 指 raw，即 raw string，会自动将反斜杠转义，例如：
'''
Python 中的字符串有两种索引方式，从左往右以 0 开始，从右往左以 -1 开始。
Python中的字符串不能改变（详见上一小点的引用）。
Python 没有单独的字符类型，一个字符就是长度为 1 的字符串。
字符串的截取的语法格式如下：变量 [头下标: 尾下标: 步长]
'''

word = '字符串'
sentence = "这是一个句子。"
paragraph = """这是一个段落，
可以由多行组成"""

str = 'W3Cschool'

print(str)  # 输出字符串
print(str[0:-1])  # 输出第一个到倒数第二个的所有字符
print(str[0])  # 输出字符串第一个字符
print(str[2:5])  # 输出从第三个开始到第五个的字符
print(str[2:])  # 输出从第三个开始后的所有字符
print(str[1:5:2])  # 输出从第二个开始到第五个且每隔两个的字符
print(str * 2)  # 输出字符串两次
print(str + '你好')  # 连接字符串

print('------------------------------')

print('hello\nW3Cschool')  # 使用反斜杠(\)+n转义特殊字符
print(r'hello\nW3Cschool')  # 在字符串前面添加一个 r，表示原始字符串，不会发生转义


input("这是一个简单的input信息") # 这是一个简单的input样例，他输出input信息并接受一个字符串
x=input("请输入X的值：") # 这是一个常见的input样例，他输出提示信息，然后接受一个字符串并将值传递给一个变量X
print(x) # 打印变量，可以看到输入的x的值
print(type(x)) #查看这个变量的类型

x = int(input("请输入一个数值：")) # 配合强制类型转换，可以将字符串转变为int类型（字符串类型不能参与计算）
# 也可以分步写成：
#x=input("请输入一个数值：") # 接受一个字符串
#x=int(x)   #将x转换为int型

# 这里强制转换也可以转换为其他类型，详细的转换方法请参考基本数据类型的强制转换相关内容

print(x) # 打印变量，可以看到输入的x的值
print(type(x)) #查看这个变量的类型

input("\n\n按下 enter 键后退出。")
# 其实这里并没有接受任何内容，input函数以enter作为结尾，所以只有输入回车后才会结束input函数

