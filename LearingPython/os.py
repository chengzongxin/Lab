import os
# os.mkdir('./test')

print(os.listdir('./test'))
f = open( "./test/a.txt", 'w', encoding='utf-8')
f.write("abcdef")
f.close()
x = open("./test/a.txt", 'r', encoding='utf-8')
print(x.read())