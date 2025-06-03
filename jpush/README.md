# 极光推送脚本使用说明

本项目包含两个极光推送应用的推送脚本，分别用于不同的应用场景。

## 目录结构

.
├── README.md
├── jpush_api.py          # 应用1



# 推送给所有用户
./run_jpush.sh all --title "测试标题" --content "这是测试内容"

# 推送给指定用户
./run_jpush.sh alias --alias "test" --title "个人通知" --content "这是个人消息"


# 推送给所有用户
./run_jpush_2.sh all --title "测试标题" --content "这是测试内容"

# 推送给指定用户
./run_jpush_2.sh alias --alias "test" --title "个人通知" --content "这是个人消息"

# 推送给标签用户
./run_jpush_2.sh tag --tag "vip" --title "VIP通知" --content "这是VIP消息"


# 带自定义参数的推送示例（应用1）
./run_jpush.sh alias \
    --alias "test" \
    --title "测试通知" \
    --content "这是测试内容" \
    --routerUrl "/(order)/detail?orderNo=123" \
    --audioUrl "new.mp3" \
    --extra customKey1 value1 \
    --extra customKey2 value2

# 带自定义参数的推送示例（应用2）
./run_jpush_2.sh tag \
    --tag "vip" \
    --title "VIP通知" \
    --content "VIP专享内容" \
    --routerUrl "/(order)/detail?orderNo=456" \
    --audioUrl "https://example.com/vip.mp3" \
    --extra type "vip-only" \
    --extra priority "high"


# 应用1的推送示例 - 单行方式
./run_jpush.sh alias --alias "3000012_t" --title "测试通知" --content "这是测试内容" --router-url "/(order)/detail?orderNo=DD20241128000012" --audio-url "new.mp3" --extra customKey1 value1 --extra customKey2 value2




# 应用1的推送示例 - 多行方式（确保每行末尾有 \，且 \ 后面没有空格）
./run_jpush.sh alias \
--alias "test" \
--title "测试通知" \
--content "这是测试内容" \
--router-url "/(order)/detail?orderNo=123" \
--audio-url "new.mp3" \
--extra customKey1 value1 \
--extra customKey2 value2

# 应用2的推送示例
./run_jpush_2.sh tag \
--tag "vip" \
--title "VIP通知" \
--content "VIP专享内容" \
--router-url "/(order)/detail?orderNo=456" \
--audio-url "new.mp3" \
--extra type "vip-only" \
--extra priority "high"


./run_jpush.sh alias --alias "3000012_t" --title "测试通知" --content "这是测试内容" --router-url "/(order)/detail?orderNo=DD20241128000012" --audio-url "new.mp3" --extra customKey1 value1 --extra customKey2 value2

./run_jpush.sh alias --alias "3000012_t" --title "测试通知" --content "这是测试内容" --router-url "/(order)/detail?orderNo=DD20241128000012" --audio-url "timeout.mp3" --extra customKey1 value1 --extra customKey2 value2


./run_jpush_2.sh alias --alias "YH20241212002_t" --title "测试通知" --content "这是测试内容" --router-url "/(order)/detail?orderNo=DD20241128000012" --audio-url "timeout.mp3" --extra customKey1 value1 --extra customKey2 value2


./run_jpush.sh alias --alias "3000031_p" --title "测试通知" --content "这是测试内容" --router-url "/(order)/detail?orderNo=DD20241128000012" --audio-url "new.mp3" --extra customKey1 value1 --extra customKey2 value2