from fastapi import APIRouter, Query, Body
from utils.scraper import search_temu
from utils.craw import ViolationListCrawler
from utils.request import NetworkRequest
import os
import time
import json
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, List, Dict, Any

router = APIRouter()


def process_single_product(product_id: int, parent_msg_id: str, tool_id: str, req: NetworkRequest) -> Dict[str, Any]:
    """
    处理单个商品的下架
    
    Args:
        product_id: 商品ID
        parent_msg_id: 父消息ID
        tool_id: 工具ID
        req: 网络请求对象
    
    Returns:
        处理结果字典
    """
    result_info = {
        "productId": product_id,
        "success": False,
        "message": "",
        "details": {}
    }
    
    try:
        # 1. 查询商品基础信息
        product_info_url = "https://seller.kuajingmaihuo.com/marvel-supplier/api/ultraman/chat/reception/queryProductSkcBasicInfo"
        product_info_payload = {"productSkcId": product_id}
        
        product_info_result = req.post(product_info_url, data=product_info_payload)
        if not product_info_result or not product_info_result.get("success"):
            result_info["message"] = "查询商品信息失败"
            return result_info
        
        product_info = product_info_result.get("result", {})
        product_name = product_info.get("productName", "")
        product_img = product_info.get("productPicture", "")
        
        # 2. 预检查是否可以下架
        precheck_url = "https://seller.kuajingmaihuo.com/marvel-supplier/api/ultraman/chat/reception/queryPreInterceptForToolSubmit"
        precheck_payload = {
            "toolId": tool_id,
            "dataId": str(product_id)
        }
        
        precheck_result = req.post(precheck_url, data=precheck_payload)
        if not precheck_result or not precheck_result.get("success"):
            result_info["message"] = "预检查失败"
            return result_info
        
        intercept_code = precheck_result.get("result", {}).get("interceptCode", -1)
        if intercept_code != 0:
            intercept_msg = precheck_result.get("result", {}).get("interceptMsg", "未知错误")
            result_info["message"] = f"无法下架：{intercept_msg}"
            return result_info
        
        # 3. 发送商品信息进行下架
        offline_content = {
            "name": product_name,
            "img": product_img,
            "dataType": 1,
            "dataId": str(product_id),
            "toolId": tool_id
        }
        
        init_url = "https://seller.kuajingmaihuo.com/bg/cute/api/merchantService/chat/sendMessage"
        offline_payload = {
            "parentMsgId": parent_msg_id,
            "contentType": 7,
            "content": json.dumps(offline_content)
        }
        
        offline_result = req.post(init_url, data=offline_payload)
        if not offline_result or not offline_result.get("success"):
            result_info["message"] = "发送下架请求失败"
            return result_info
        
        offline_msg_id = offline_result.get("result", {}).get("msgId")
        
                # 4. 轮询查询下架结果
        query_url = "https://seller.kuajingmaihuo.com/bg/cute/api/merchantService/chat/queryMessage"
        max_retries = 10
        retry_count = 0
        offline_success = False
        
        while retry_count < max_retries:
            # 动态等待时间：前几次等待较短，后面逐渐增加
            time.sleep(1)
            
            # 查询下架结果
            result_query_payload = {
                "msgId": offline_msg_id,
                "direction": 2,
                "limit": 20
            }
            
            result_query = req.post(query_url, data=result_query_payload)
            if result_query and result_query.get("success"):
                result_messages = result_query.get("result", {}).get("messageList", [])
                
                # 查找当前商品的下架结果
                current_product_result = None
                for msg in result_messages:
                    content = msg.get("content", "")
                    if "【商品下架】咨询结果已更新" in content:
                        # 检查是否包含当前商品ID（支持多种格式）
                        if (f"SKC ID：{product_id}" in content or 
                            f"SKC ID:{product_id}" in content or
                            f"【SKC ID：{product_id}】" in content):
                            current_product_result = content
                            break
                
                # 如果找到了当前商品的结果
                if current_product_result:
                    print(f"商品 {product_id} 找到下架结果: {current_product_result[:100]}...")
                    if "已下架" in current_product_result:
                        offline_success = True
                        result_info["message"] = "下架成功"
                    elif "暂时无法操作下架" in current_product_result:
                        result_info["message"] = "商品未发布到站点，无法下架"
                    elif "已在您的上次咨询后处理成功" in current_product_result:
                        result_info["message"] = "商品已在之前处理成功"
                        offline_success = True  # 视为成功
                    else:
                        result_info["message"] = f"下架结果：{current_product_result}"
                    break
                else:
                    # 调试信息：显示找到的所有下架结果
                    offline_results = []
                    for msg in result_messages:
                        content = msg.get("content", "")
                        if "【商品下架】咨询结果已更新" in content:
                            offline_results.append(content[:100] + "...")
                    
                    if offline_results:
                        print(f"商品 {product_id} 轮询第 {retry_count + 1} 次，找到 {len(offline_results)} 个下架结果，但不包含当前商品")
                        print(f"找到的结果: {offline_results}")
                
                retry_count += 1
            
            if retry_count >= max_retries:
                # 轮询超时，尝试从所有消息中查找结果
                print(f"商品 {product_id} 轮询超时，尝试从所有消息中查找结果")
                
                # 扩大查询范围，获取更多消息
                extended_query_payload = {
                    "msgId": offline_msg_id,
                    "direction": 2,
                    "limit": 50  # 增加查询数量
                }
                
                extended_result = req.post(query_url, data=extended_query_payload)
                if extended_result and extended_result.get("success"):
                    extended_messages = extended_result.get("result", {}).get("messageList", [])
                    
                    # 在所有消息中查找当前商品的结果
                    for msg in extended_messages:
                        content = msg.get("content", "")
                        if "【商品下架】咨询结果已更新" in content:
                            if (f"SKC ID：{product_id}" in content or 
                                f"SKC ID:{product_id}" in content or
                                f"【SKC ID：{product_id}】" in content):
                                
                                if "已下架" in content:
                                    offline_success = True
                                    result_info["message"] = "下架成功（延迟确认）"
                                elif "暂时无法操作下架" in content:
                                    result_info["message"] = "商品未发布到站点，无法下架（延迟确认）"
                                elif "已在您的上次咨询后处理成功" in content:
                                    result_info["message"] = "商品已在之前处理成功（延迟确认）"
                                    offline_success = True
                                else:
                                    result_info["message"] = f"下架结果（延迟确认）：{content}"
                                break
                
                if not result_info["message"] or result_info["message"] == "查询下架结果超时":
                    result_info["message"] = "查询下架结果超时"
        
        result_info["success"] = offline_success
        result_info["details"] = {
            "productName": product_name,
            "productImg": product_img,
            "offlineMsgId": offline_msg_id,
            "retryCount": retry_count
        }
        
    except Exception as e:
        result_info["message"] = f"处理异常：{str(e)}"
    
    return result_info


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

@router.get("/compliance/total")
def get_compliance_total(
    page: int = Query(1, description="页码"),
    page_size: int = Query(20, description="每页数量")
):
    crawler = ViolationListCrawler(config_type="compliance")
    total = crawler.get_total_data(page, page_size)
    if total is not None:
        return {"success": True, "total": total}
    else:
        return {"success": False, "msg": "获取数据失败"}

@router.post("/seller/product")
def get_product(
    productIds: Optional[List[int]] = Body(None, embed=True),
    productName: Optional[str] = Body(None, embed=True),
    page: int = Body(1, embed=True),
    pageSize: int = Body(500, embed=True)
):
    req = NetworkRequest(config_type="compliance")
    url = "https://agentseller.temu.com/visage-agent-seller/product/skc/pageQuery"
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
        return {"success": True, "data": [], "msg": "未找到商品"}
    # 返回所有商品列表
    return {
        "success": True,
        "data": items
    }

@router.post("/seller/offline")
def offline_products(
    productIds: List[int] = Body(..., embed=True),
    max_threads: int = Body(8, embed=True)
):
    """
    批量下架商品功能 - 完整流程（带缓存优化）
    
    步骤：
    1. 检查缓存中是否有有效的parentMsgId和toolId
    2. 如果没有缓存或缓存无效，重新获取
    3. 对每个商品：
       - 查询商品基础信息
       - 使用缓存的工具ID（如果没有则重新获取）
       - 预检查是否可以下架
       - 发送商品信息进行下架
       - 轮询查询下架结果
    """
    req = NetworkRequest(config_type="seller")
    results = []
    
    # 读取配置和缓存
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    config = {}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    
    # 检查缓存是否有效
    cached_parent_msg_id = config.get("parent_msg_id")
    cached_tool_id = config.get("tool_id")
    cached_timestamp = config.get("parent_msg_timestamp")
    
    # 检查缓存是否过期（24小时）
    cache_valid = False
    if cached_parent_msg_id and cached_tool_id and cached_timestamp:
        try:
            cache_time = int(cached_timestamp)
            current_time = int(time.time() * 1000)  # 毫秒时间戳
            if current_time - cache_time < 24 * 60 * 60 * 1000:  # 24小时
                cache_valid = True
        except:
            pass
    
    parent_msg_id = None
    tool_id = None
    
    # 定义URL常量
    init_url = "https://seller.kuajingmaihuo.com/bg/cute/api/merchantService/chat/sendMessage"
    query_url = "https://seller.kuajingmaihuo.com/bg/cute/api/merchantService/chat/queryMessage"
    
    if cache_valid:
        print(f"使用缓存的parentMsgId: {cached_parent_msg_id}, toolId: {cached_tool_id}")
        parent_msg_id = cached_parent_msg_id
        tool_id = cached_tool_id
    else:
        print("缓存无效或过期，重新获取parentMsgId和toolId")
        
        # 第一步：发送"商品下架"消息初始化对话
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
                            tool_id = content_data.get("toolId")
                            break
                    except json.JSONDecodeError:
                        # 如果不是JSON，检查是否包含关键词
                        if "toolId" in content and ("发商品" in content or "btnText" in content):
                            parent_msg_id = msg.get("msgId")
                            # 尝试从内容中提取toolId
                            tool_match = re.search(r'"toolId":(\d+)', content)
                            if tool_match:
                                tool_id = tool_match.group(1)
                            break
            
            if parent_msg_id and tool_id:
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
        
        # 如果还没有tool_id，重新获取工具列表
        if not tool_id:
            tool_list_url = "https://seller.kuajingmaihuo.com/marvel-supplier/api/ultraman/chat/reception/querySelfServiceTools"
            tool_list_resp = req.post(tool_list_url, data={})
            
            if tool_list_resp and tool_list_resp.get("success"):
                tools = tool_list_resp.get("result", {}).get("list", [])
                for tool in tools:
                    if tool.get("toolName") == "商品下架":
                        tool_id = tool.get("toolId")
                        break
        
        # 更新缓存
        if parent_msg_id and tool_id:
            current_timestamp = str(int(time.time() * 1000))
            config["parent_msg_id"] = parent_msg_id
            config["tool_id"] = tool_id
            config["parent_msg_timestamp"] = current_timestamp
            
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            print(f"已更新缓存：parentMsgId={parent_msg_id}, toolId={tool_id}")
    
    if not parent_msg_id or not tool_id:
        return {"success": False, "msg": "无法获取下架所需的parentMsgId或toolId"}
    
    # 第三步：使用多线程批量处理商品
    print(f"开始多线程处理 {len(productIds)} 个商品...")
    
    # 确定线程数（根据商品数量和用户设置动态调整）
    max_workers = min(max_threads, len(productIds))
    print(f"使用 {max_workers} 个线程进行处理（最大设置：{max_threads}）")
    
    # 使用线程池处理
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_product = {
            executor.submit(process_single_product, product_id, parent_msg_id, tool_id, req): product_id 
            for product_id in productIds
        }
        
        # 收集结果
        for future in as_completed(future_to_product):
            product_id = future_to_product[future]
            try:
                result = future.result()
                results.append(result)
                print(f"商品 {product_id} 处理完成: {result['success']} - {result['message']}")
            except Exception as e:
                results.append({
                    "productId": product_id,
                    "success": False,
                    "message": f"线程处理异常：{str(e)}",
                    "details": {}
                })
                print(f"商品 {product_id} 处理异常: {str(e)}")
    
    print(f"多线程处理完成，共处理 {len(results)} 个商品")
    
    # 统计结果
    success_count = sum(1 for r in results if r["success"])
    total_count = len(results)
    
    return {
        "success": True,
        "message": f"批量下架完成，共处理 {total_count} 个商品，{success_count} 个下架成功",
        "parentMsgId": parent_msg_id,
        "toolId": tool_id,
        "cacheUsed": cache_valid,
        "threadInfo": {
            "maxThreads": max_threads,
            "actualThreads": max_workers,
            "productCount": len(productIds)
        },
        "results": results,
        "summary": {
            "total": total_count,
            "success": success_count,
            "failed": total_count - success_count
        }
    }


