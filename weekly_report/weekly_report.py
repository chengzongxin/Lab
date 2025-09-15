import subprocess
import datetime

def get_git_log(author: str, since: str, until: str):
    """获取指定作者在时间范围内的 git 提交记录"""
    cmd = [
        "git", "log",
        f'--author={author}',
        f'--since={since}',
        f'--until={until}',
        "--pretty=format:%ad %s",
        "--date=short"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip().split("\n") if result.stdout else []

def generate_weekly_report(author: str, days: int = 7):
    today = datetime.date.today()
    since = (today - datetime.timedelta(days=days)).strftime("%Y-%m-%d")
    until = today.strftime("%Y-%m-%d")

    logs = get_git_log(author, since, until)

    report = []
    report.append(f"# 周报（{since} ~ {until}）\n")
    
    report.append("## 本周完成工作")
    if logs:
        for log in logs:
            report.append(f"- {log}")
    else:
        report.append("- 本周无提交记录")

    report.append("\n## 下周计划")
    report.append("- 继续推进未完成的功能开发")
    report.append("- 优化代码结构与性能")
    
    report.append("\n## 存在问题与需协调事项")
    report.append("- 暂无")

    return "\n".join(report)

if __name__ == "__main__":
    # 修改为你的 git 用户名/邮箱（和提交时保持一致）
    author = "你的名字"
    report = generate_weekly_report(author)
    print(report)
