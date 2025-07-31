/**
 * WebSocket通信相关的类型定义
 */

// WebSocket连接状态
export type WebSocketStatus = 'CONNECTING' | 'OPEN' | 'CLOSING' | 'CLOSED' | 'UNKNOWN';

// 消息类型
export type MessageType = 'greeting' | 'calculation' | 'text' | 'response' | 'calculation_result' | 'error' | 'echo';

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

// 联合类型：所有可能的消息
export type WebSocketMessage = 
  | GreetingMessage 
  | CalculationMessage 
  | TextMessage 
  | ResponseMessage 
  | CalculationResultMessage 
  | ErrorMessage 
  | EchoMessage;

// Background Script 操作类型
export type BackgroundAction = 'connect' | 'disconnect' | 'send_message' | 'get_status';

// Background Script 请求接口
export interface BackgroundRequest {
  action: BackgroundAction;
  message?: WebSocketMessage;
}

// Background Script 响应接口
export interface BackgroundResponse {
  success: boolean;
  message?: string;
  status?: WebSocketStatus;
  connected?: boolean;
}

// 消息记录类型
export type MessageLogType = 'sent' | 'received' | 'system' | 'error';

export interface MessageLog {
  id: string;
  content: string;
  type: MessageLogType;
  timestamp: Date;
}