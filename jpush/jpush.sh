#!/bin/bash

# 极光推送配置
APP_KEY="d37d80b5de222298f23c5e47"
MASTER_SECRET="9952dea984280b67e8b6e5bf"
API_URL="https://api.jpush.cn/v3/push"

# 生成认证信息
AUTH_STRING=$(echo -n "$APP_KEY:$MASTER_SECRET" | base64)

# 推送给所有用户的函数
push_to_all() {
    local title="$1"
    local content="$2"
    
    echo "推送给所有用户："
    echo "标题：$title"
    echo "内容：$content"
    
    # 构建JSON payload
    payload=$(cat <<EOF
{
    "platform": "all",
    "audience": "all",
    "notification": {
        "android": {
            "alert": "$content",
            "title": "$title"
        },
        "ios": {
            "alert": "$content",
            "sound": "default",
            "badge": "+1"
        }
    }
}
EOF
)

    # 发送请求
    curl -X POST \
        -H "Content-Type: application/json" \
        -H "Authorization: Basic $AUTH_STRING" \
        -d "$payload" \
        $API_URL
    
    echo -e "\n"
}

# 推送给指定别名用户的函数
push_to_alias() {
    local alias="$1"
    local title="$2"
    local content="$3"
    
    echo "推送给用户 $alias："
    echo "标题：$title"
    echo "内容：$content"
    
    # 构建JSON payload
    payload=$(cat <<EOF
{
    "platform": "all",
    "audience": {
        "alias": ["$alias"]
    },
    "notification": {
        "android": {
            "alert": "$content",
            "title": "$title"
        },
        "ios": {
            "alert": "$content",
            "sound": "default",
            "badge": "+1"
        }
    },
    "options": {
        "apns_production": false
    }
}
EOF
)

    # 发送请求
    curl -X POST \
        -H "Content-Type: application/json" \
        -H "Authorization: Basic $AUTH_STRING" \
        -d "$payload" \
        $API_URL
    
    echo -e "\n"
}

# 显示使用方法
show_usage() {
    echo "使用方法："
    echo "推送给所有用户："
    echo "  $0 all '标题' '内容'"
    echo "推送给指定用户："
    echo "  $0 alias '用户别名' '标题' '内容'"
    echo
    echo "示例："
    echo "  $0 all '系统通知' '服务器将于今晚维护'"
    echo "  $0 alias user123 '个人通知' '您有一条新消息'"
}

# 主程序
case "$1" in
    "all")
        if [ $# -ne 3 ]; then
            show_usage
            exit 1
        fi
        push_to_all "$2" "$3"
        ;;
    "alias")
        if [ $# -ne 4 ]; then
            show_usage
            exit 1
        fi
        push_to_alias "$2" "$3" "$4"
        ;;
    *)
        show_usage
        exit 1
        ;;
esac 