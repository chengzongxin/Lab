# Fibonacci series: 斐波纳契数列
# 两个元素的总和确定了下一个数
a, b = 0, 1
while a < 10:
    print(b)
    a, b = b, a + b


age = int(input("Please enter your dog age: "))
print("")
if age < 0:
    print("Age can't be negative")
elif age == 1:
    print("Your dog age in human years is 15")
elif age == 2:
    print("Your dog age in human years is 24")
elif age > 2:
    human = 24 + (age - 2) * 4
    print("Your dog age in human years is", human)

input("Press enter to exit")