from fastapi import APIRouter, Query, Body
from utils.scraper import search_temu
from utils.craw import ViolationListCrawler
from utils.request import NetworkRequest
import os
import time
import json
from typing import Optional, List, Dict, Any

router = APIRouter()


@router.get("/compliance/list")
def get_compliance_list(
    page: int = Query(1, description="页码"),
    page_size: int = Query(20, description="每页数量")
):
    crawler = ViolationListCrawler(config_type="compliance")
    data = crawler.get_page_data(page, page_size)
    if data is not None:
        return {"success": True, "data": data}
    else:
        return {"success": False, "msg": "获取数据失败"}

@router.post("/seller/product")
def get_product(
    productIds: Optional[List[int]] = Body(None, embed=True),
    productName: Optional[str] = Body(None, embed=True),
    page: int = Body(1, embed=True),
    pageSize: int = Body(20, embed=True)
):
    req = NetworkRequest(config_type="seller")
    url = "https://seller.kuajingmaihuo.com/bg-visage-mms/product/skc/pageQuery"
    payload: Dict[str, Any] = {"page": page, "pageSize": pageSize}
    if productIds is not None:
        payload["productIds"] = productIds
    if productName is not None:
        payload["productName"] = productName
    result = req.post(url, data=payload)
    if not result or not result.get("success"):
        return {"success": False, "msg": "查询失败"}
    items = result.get("result", {}).get("pageItems", [])
    if not items:
        return {"success": False, "msg": "未找到商品"}
    # 返回所有商品列表
    return {
        "success": True,
        "data": items
    }

@router.post("/seller/offline")
def offline_products(productIds: List[int] = Body(..., embed=True)):
    """
    批量下架商品功能 - 完整流程
    
    步骤：
    1. 发送"商品下架"消息初始化对话
    2. 获取客服回复和parentMsgId
    3. 对每个商品：
       - 查询商品基础信息
       - 获取商品下架工具ID
       - 预检查是否可以下架
       - 发送商品信息进行下架
       - 轮询查询下架结果
    """
    req = NetworkRequest(config_type="seller")
    results = []
    
    # 第一步：发送"商品下架"消息初始化对话
    init_url = "https://seller.kuajingmaihuo.com/bg/cute/api/merchantService/chat/sendMessage"
    init_payload = {
        "contentType": 1,
        "content": "商品下架"
    }
    
    init_result = req.post(init_url, data=init_payload)
    if not init_result or not init_result.get("success"):
        return {"success": False, "msg": "初始化下架对话失败"}
    
    init_msg_id = init_result.get("result", {}).get("msgId")
    if not init_msg_id:
        return {"success": False, "msg": "获取初始消息ID失败"}
    
    # 第二步：查询消息获取客服回复（带重试机制）
    query_url = "https://seller.kuajingmaihuo.com/bg/cute/api/merchantService/chat/queryMessage"
    parent_msg_id = None
    max_retries = 5
    
    for retry in range(max_retries):
        query_payload = {
            "msgId": init_msg_id,
            "direction": 2,
            "limit": 20
        }
        
        query_result = req.post(query_url, data=query_payload)
        if not query_result or not query_result.get("success"):
            if retry == max_retries - 1:
                return {"success": False, "msg": "查询客服回复失败"}
            time.sleep(1)
            continue
        
        # 查找包含"发商品"按钮的消息
        message_list = query_result.get("result", {}).get("messageList", [])
        for msg in message_list:
            content = msg.get("content", "")
            content_type = msg.get("contentType")
            
            # 检查是否是客服回复的消息（senderType=1001）
            if msg.get("senderType") == 1001 and content_type == 6:
                try:
                    # 尝试解析JSON内容
                    content_data = json.loads(content)
                    if "toolId" in content_data and "btnText" in content_data:
                        parent_msg_id = msg.get("msgId")
                        break
                except json.JSONDecodeError:
                    # 如果不是JSON，检查是否包含关键词
                    if "toolId" in content and ("发商品" in content or "btnText" in content):
                        parent_msg_id = msg.get("msgId")
                        break
        
        if parent_msg_id:
            break
        
        # 如果没找到，等待后重试
        if retry < max_retries - 1:
            time.sleep(2)
    
    if not parent_msg_id:
        # 返回调试信息，帮助诊断问题
        debug_info = {
            "initMsgId": init_msg_id,
            "messageCount": len(message_list) if 'message_list' in locals() else 0,
            "messages": []
        }
        
        if 'message_list' in locals():
            for msg in message_list:
                debug_info["messages"].append({
                    "msgId": msg.get("msgId"),
                    "senderType": msg.get("senderType"),
                    "contentType": msg.get("contentType"),
                    "content": msg.get("content", "")[:100] + "..." if len(msg.get("content", "")) > 100 else msg.get("content", "")
                })
        
        # 如果找不到按钮消息，尝试使用初始消息ID作为备用方案
        print(f"警告：未找到商品下架按钮消息，使用初始消息ID作为备用方案")
        parent_msg_id = init_msg_id
    
    # 第三步：批量处理每个商品
    for product_id in productIds:
        try:
            result_info = {
                "productId": product_id,
                "success": False,
                "message": "",
                "details": {}
            }
            
            # 3.1 查询商品基础信息
            product_info_url = "https://seller.kuajingmaihuo.com/marvel-supplier/api/ultraman/chat/reception/queryProductSkcBasicInfo"
            product_info_payload = {"productSkcId": product_id}
            
            product_info_result = req.post(product_info_url, data=product_info_payload)
            if not product_info_result or not product_info_result.get("success"):
                result_info["message"] = "查询商品信息失败"
                results.append(result_info)
                continue
            
            product_info = product_info_result.get("result", {})
            product_name = product_info.get("productName", "")
            product_img = product_info.get("productPicture", "")
            
            # 3.2 获取商品下架工具ID
            tool_list_url = "https://seller.kuajingmaihuo.com/marvel-supplier/api/ultraman/chat/reception/querySelfServiceTools"
            tool_list_resp = req.post(tool_list_url, data={})
            
            if not tool_list_resp or not tool_list_resp.get("success"):
                result_info["message"] = "获取工具列表失败"
                results.append(result_info)
                continue
            
            # 查找商品下架工具
            tool_id = None
            tools = tool_list_resp.get("result", {}).get("list", [])
            for tool in tools:
                if tool.get("toolName") == "商品下架":
                    tool_id = tool.get("toolId")
                    break
            
            if not tool_id:
                result_info["message"] = "未找到商品下架工具ID"
                results.append(result_info)
                continue
            
            # 3.3 预检查是否可以下架
            precheck_url = "https://seller.kuajingmaihuo.com/marvel-supplier/api/ultraman/chat/reception/queryPreInterceptForToolSubmit"
            precheck_payload = {
                "toolId": tool_id,
                "dataId": str(product_id)
            }
            
            precheck_result = req.post(precheck_url, data=precheck_payload)
            if not precheck_result or not precheck_result.get("success"):
                result_info["message"] = "预检查失败"
                results.append(result_info)
                continue
            
            intercept_code = precheck_result.get("result", {}).get("interceptCode", -1)
            if intercept_code != 0:
                intercept_msg = precheck_result.get("result", {}).get("interceptMsg", "未知错误")
                result_info["message"] = f"无法下架：{intercept_msg}"
                results.append(result_info)
                continue
            
            # 3.4 发送商品信息进行下架
            offline_content = {
                "name": product_name,
                "img": product_img,
                "dataType": 1,
                "dataId": str(product_id),
                "toolId": tool_id
            }
            
            offline_payload = {
                "parentMsgId": parent_msg_id,
                "contentType": 7,
                "content": json.dumps(offline_content)
            }
            
            offline_result = req.post(init_url, data=offline_payload)
            if not offline_result or not offline_result.get("success"):
                result_info["message"] = "发送下架请求失败"
                results.append(result_info)
                continue
            
            offline_msg_id = offline_result.get("result", {}).get("msgId")
            
            # 3.5 轮询查询下架结果
            max_retries = 10
            retry_count = 0
            offline_success = False
            
            while retry_count < max_retries:
                time.sleep(2)  # 等待2秒
                
                # 查询下架结果
                result_query_payload = {
                    "msgId": offline_msg_id,
                    "direction": 2,
                    "limit": 20
                }
                
                result_query = req.post(query_url, data=result_query_payload)
                if result_query and result_query.get("success"):
                    result_messages = result_query.get("result", {}).get("messageList", [])
                    
                    for msg in result_messages:
                        content = msg.get("content", "")
                        if "【商品下架】咨询结果已更新" in content:
                            if "已下架" in content:
                                offline_success = True
                                result_info["message"] = "下架成功"
                            elif "暂时无法操作下架" in content:
                                result_info["message"] = "商品未发布到站点，无法下架"
                            else:
                                result_info["message"] = f"下架结果：{content}"
                            break
                
                if offline_success or "暂时无法操作下架" in result_info["message"]:
                    break
                
                retry_count += 1
            
            if retry_count >= max_retries:
                result_info["message"] = "查询下架结果超时"
            
            result_info["success"] = offline_success
            result_info["details"] = {
                "productName": product_name,
                "productImg": product_img,
                "offlineMsgId": offline_msg_id,
                "retryCount": retry_count
            }
            
            results.append(result_info)
            
            # 添加延迟避免请求过快
            time.sleep(1)
            
        except Exception as e:
            results.append({
                "productId": product_id,
                "success": False,
                "message": f"处理异常：{str(e)}",
                "details": {}
            })
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    total_count = len(results)
    
    return {
        "success": True,
        "message": f"批量下架完成，共处理 {total_count} 个商品，{success_count} 个下架成功",
        "initMsgId": init_msg_id,
        "parentMsgId": parent_msg_id,
        "results": results,
        "summary": {
            "total": total_count,
            "success": success_count,
            "failed": total_count - success_count
        }
    }


