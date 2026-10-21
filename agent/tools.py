import os
import requests
from dotenv import load_dotenv

load_dotenv()


def send_ticket_to_webhook(device_code: str, ai_analysis: str) -> str:
    """真实调用 Webhook，将工单发送给工程师"""
    webhook_url = os.getenv("DINGTALK_WEBHOOK_URL")

    if not webhook_url or "你的token" in webhook_url:
        print("⚠️ [Tool] 未配置真实的 Webhook URL，跳过发送。")
        return "模拟发送成功（未配置真实 Webhook）。"

    # 组装钉钉要求的消息格式
    message_content = f"【MGI设备预警】\n设备报错：{device_code}\nAI诊断摘要：{ai_analysis[:50]}...\n请原厂工程师速速联系处理！"

    payload = {
        "msgtype": "text",
        "text": {
            "content": message_content
        }
    }

    try:
        # 真实发出 HTTP POST 请求
        response = requests.post(webhook_url, json=payload, timeout=5)
        response.raise_for_status()
        print("✅ [Tool] Webhook 消息发送成功！")
        return "✅ 已真实通过 Webhook 发送至售后工程师群。"
    except Exception as e:
        print(f"❌ [Tool] Webhook 发送失败: {e}")
        return f"❌ 发送失败，请检查网络或 Webhook 配置: {e}"