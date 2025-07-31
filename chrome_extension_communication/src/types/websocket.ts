/**
 * WebSocket通信相关的类型定义
 */

// WebSocket连接状态
export type WebSocketStatus = 'CONNECTING' | 'OPEN' | 'CLOSING' | 'CLOSED' | 'UNKNOWN';

// 消息类型
export type MessageType = 'greeting' | 'calculation' | 'text' | 'response' | 'calculation_result' | 'error' | 'echo' | 'backend_command' | 'command_response';

// 基础消息接口
export interface BaseMessage {
  type: MessageType;
}

// 问候消息
export interface GreetingMessage extends BaseMessage {
  type: 'greeting';
  content: string;
}

// 计算消息
export interface CalculationMessage extends BaseMessage {
  type: 'calculation';
  num1: number;
  num2: number;
  operation: '+' | '-' | '*' | '/';
}

// 文本消息
export interface TextMessage extends BaseMessage {
  type: 'text';
  content: string;
}

// 服务器回应消息
export interface ResponseMessage extends BaseMessage {
  type: 'response';
  message: string;
}

// 计算结果消息
export interface CalculationResultMessage extends BaseMessage {
  type: 'calculation_result';
  result: number | string;
}

// 错误消息
export interface ErrorMessage extends BaseMessage {
  type: 'error';
  message: string;
}

// 回显消息
export interface EchoMessage extends BaseMessage {
  type: 'echo';
  original_message: any;
  timestamp: string;
}

// 后端命令消息接口
export interface BackendCommandMessage extends BaseMessage {
  type: 'backend_command';
  command: string;
  params: Record<string, any>;
  command_id: string;
}

// 命令响应消息接口
export interface CommandResponseMessage extends BaseMessage {
  type: 'command_response';
  command_id: string;
  data: any;
}

// 联合类型：所有可能的消息
export type WebSocketMessage = 
  | GreetingMessage 
  | CalculationMessage 
  | TextMessage 
  | ResponseMessage 
  | CalculationResultMessage 
  | ErrorMessage 
  | EchoMessage
  | BackendCommandMessage
  | CommandResponseMessage;

// Cookie相关类型 (从cookieUtils导入)
export interface CookieInfo {
  name: string;
  value: string;
  domain: string;
  path: string;
  httpOnly: boolean;
  secure: boolean;
  sameSite: chrome.cookies.SameSiteStatus;
  expirationDate?: number;
}

export interface CookieFilter {
  domain?: string;
  name?: string;
  path?: string;
  secure?: boolean;
  httpOnly?: boolean;
}

// 请求拦截相关类型 (从headersUtils导入)
export interface RequestHeader {
  name: string;
  value: string;
}

export interface InterceptedRequest {
  id: string;
  url: string;
  method: string;
  type: string;
  headers: RequestHeader[];
  timestamp: string;
  domain: string;
  path: string;
}

export interface RequestFilter {
  domain?: string;
  method?: string;
  type?: string;
  headerName?: string;
  timeRange?: {
    start: number;
    end: number;
  };
}

export interface RequestStatistics {
  total: number;
  domains: string[];
  methods: Record<string, number>;
  types: Record<string, number>;
  headerNames: string[];
}

// Background Script 操作类型 (扩展了新功能)
export type BackgroundAction = 
  | 'connect' 
  | 'disconnect' 
  | 'send_message' 
  | 'get_status'
  // Cookie操作
  | 'get_all_cookies'
  | 'get_cookies_by_domain'
  | 'get_current_tab_cookies'
  | 'get_cookies_by_domains'
  | 'clear_domain_cookies'
  // 请求拦截操作
  | 'start_interception'
  | 'stop_interception'
  | 'get_interception_status'
  | 'get_intercepted_requests'
  | 'get_recent_requests'
  | 'search_requests'
  | 'find_requests_by_header'
  | 'get_request_by_id'
  | 'get_requests_by_domain'
  | 'get_request_statistics'
  | 'export_requests'
  | 'clear_all_requests';

// Background Script 请求接口 (扩展了新参数)
export interface BackgroundRequest {
  action: BackgroundAction;
  message?: WebSocketMessage;
  // Cookie相关参数
  domain?: string;
  domains?: string[];
  cookieFilter?: CookieFilter;
  // 请求拦截相关参数
  filter?: RequestFilter;
  headerName?: string;
  headerValue?: string;
  requestId?: string;
  limit?: number;
}

// Background Script 响应接口 (扩展了新的返回数据)
export interface BackgroundResponse {
  success: boolean;
  message?: string;
  status?: WebSocketStatus;
  connected?: boolean;
  // Cookie相关响应
  cookies?: CookieInfo[];
  cookieMap?: Record<string, CookieInfo[]>;
  clearedCount?: number;
  // 请求拦截相关响应
  requests?: InterceptedRequest[];
  request?: InterceptedRequest;
  statistics?: RequestStatistics;
  exportData?: string;
  isIntercepting?: boolean;
}

// 消息记录类型
export type MessageLogType = 'sent' | 'received' | 'system' | 'error';

export interface MessageLog {
  id: string;
  content: string;
  type: MessageLogType;
  timestamp: Date;
}