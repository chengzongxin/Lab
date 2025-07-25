#!/usr/bin/env python3
import sys
import struct
import json

def get_message():
    raw_length = sys.stdin.buffer.read(4)
    if len(raw_length) == 0:
        print("未收到长度头，退出", file=sys.stderr)
        sys.exit(0)
    message_length = struct.unpack('I', raw_length)[0]
    message = sys.stdin.buffer.read(message_length).decode('utf-8')
    print(f"收到原始消息: {message}", file=sys.stderr)
    return json.loads(message)

def send_message(message_content):
    encoded_content = json.dumps(message_content).encode('utf-8')
    sys.stdout.buffer.write(struct.pack('I', len(encoded_content)))
    sys.stdout.buffer.write(encoded_content)
    sys.stdout.buffer.flush()
    print(f"已发送消息: {message_content}", file=sys.stderr)

if __name__ == "__main__":
    while True:
        try:
            received_message = get_message()
            print("收到消息：", received_message, file=sys.stderr)
            send_message({"reply": "你好，来自Python的回应！"})
        except Exception as e:
            print("发生错误：", e, file=sys.stderr)
            sys.exit(1)