/**
 * 请求头拦截和存储工具类
 * 拦截页面请求，收集并存储请求头信息
 */

export interface RequestHeader {
  name: string;
  value: string;
}

export interface InterceptedRequest {
  id: string;                    // 唯一标识符
  url: string;                   // 请求URL
  method: string;                // 请求方法 (GET, POST, etc.)
  type: string;                  // 请求类型 (document, xmlhttprequest, etc.)
  headers: RequestHeader[];      // 请求头列表
  timestamp: string;             // 时间戳
  domain: string;                // 域名
  path: string;                  // 路径
}

export interface RequestFilter {
  domain?: string;               // 按域名过滤
  method?: string;               // 按请求方法过滤
  type?: string;                 // 按请求类型过滤
  headerName?: string;           // 按请求头名称过滤
  timeRange?: {                  // 按时间范围过滤
    start: number;
    end: number;
  };
}

export interface RequestStatistics {
  total: number;                 // 总请求数
  domains: string[];             // 涉及的域名
  methods: Record<string, number>; // 各种请求方法的数量
  types: Record<string, number>;   // 各种请求类型的数量
  headerNames: string[];         // 所有出现过的请求头名称
}

export class RequestInterceptor {
  private static readonly STORAGE_KEY = 'intercepted_requests';
  private static readonly MAX_REQUESTS = 1000; // 最大存储请求数量

  /**
   * 获取所有拦截的请求
   */
  static async getInterceptedRequests(): Promise<InterceptedRequest[]> {
    try {
      const result = await chrome.storage.local.get(this.STORAGE_KEY);
      const requests = result[this.STORAGE_KEY] || {};
      return Object.values(requests);
    } catch (error) {
      console.error('获取拦截的请求失败:', error);
      return [];
    }
  }

  /**
   * 保存拦截的请求
   */
  static async saveInterceptedRequest(request: InterceptedRequest): Promise<boolean> {
    try {
      const result = await chrome.storage.local.get(this.STORAGE_KEY);
      const requests = result[this.STORAGE_KEY] || {};
      
      // 添加新请求
      requests[request.id] = request;
      
      // 如果超过最大数量，删除最老的请求
      const requestArray = Object.values(requests) as InterceptedRequest[];
      if (requestArray.length > this.MAX_REQUESTS) {
        // 按时间戳排序，删除最老的
        requestArray.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
        const toDelete = requestArray.slice(0, requestArray.length - this.MAX_REQUESTS);
        toDelete.forEach(req => delete requests[req.id]);
      }
      
      await chrome.storage.local.set({
        [this.STORAGE_KEY]: requests
      });
      return true;
    } catch (error) {
      console.error('保存拦截的请求失败:', error);
      return false;
    }
  }

  /**
   * 根据ID获取特定请求
   */
  static async getRequestById(id: string): Promise<InterceptedRequest | null> {
    try {
      const result = await chrome.storage.local.get(this.STORAGE_KEY);
      const requests = result[this.STORAGE_KEY] || {};
      return requests[id] || null;
    } catch (error) {
      console.error('获取请求失败:', error);
      return null;
    }
  }

  /**
   * 根据过滤条件搜索请求
   */
  static async searchRequests(filter: RequestFilter): Promise<InterceptedRequest[]> {
    try {
      const allRequests = await this.getInterceptedRequests();
      
      return allRequests.filter(request => {
        // 域名过滤
        if (filter.domain && !request.domain.includes(filter.domain)) {
          return false;
        }
        
        // 请求方法过滤
        if (filter.method && request.method !== filter.method) {
          return false;
        }
        
        // 请求类型过滤
        if (filter.type && request.type !== filter.type) {
          return false;
        }
        
        // 请求头名称过滤
        if (filter.headerName && !request.headers.some(h => h.name.toLowerCase().includes(filter.headerName!.toLowerCase()))) {
          return false;
        }
        
        // 时间范围过滤
        if (filter.timeRange) {
          const requestTime = new Date(request.timestamp).getTime();
          if (requestTime < filter.timeRange.start || requestTime > filter.timeRange.end) {
            return false;
          }
        }
        
        return true;
      });
    } catch (error) {
      console.error('搜索请求失败:', error);
      return [];
    }
  }

  /**
   * 根据key-value查找请求头
   */
  static async findRequestsByHeader(headerName: string, headerValue?: string): Promise<InterceptedRequest[]> {
    try {
      const allRequests = await this.getInterceptedRequests();
      
      return allRequests.filter(request => {
        return request.headers.some(header => {
          const nameMatch = header.name.toLowerCase() === headerName.toLowerCase();
          if (!headerValue) return nameMatch;
          return nameMatch && header.value.includes(headerValue);
        });
      });
    } catch (error) {
      console.error('查找请求头失败:', error);
      return [];
    }
  }

  /**
   * 获取请求统计信息
   */
  static async getRequestStatistics(): Promise<RequestStatistics> {
    try {
      const allRequests = await this.getInterceptedRequests();
      
      const domains = new Set<string>();
      const methods: Record<string, number> = {};
      const types: Record<string, number> = {};
      const headerNames = new Set<string>();
      
      allRequests.forEach(request => {
        domains.add(request.domain);
        methods[request.method] = (methods[request.method] || 0) + 1;
        types[request.type] = (types[request.type] || 0) + 1;
        request.headers.forEach(header => headerNames.add(header.name));
      });
      
      return {
        total: allRequests.length,
        domains: Array.from(domains),
        methods,
        types,
        headerNames: Array.from(headerNames)
      };
    } catch (error) {
      console.error('获取统计信息失败:', error);
      return {
        total: 0,
        domains: [],
        methods: {},
        types: {},
        headerNames: []
      };
    }
  }

  /**
   * 根据域名获取请求
   */
  static async getRequestsByDomain(domain: string): Promise<InterceptedRequest[]> {
    return await this.searchRequests({ domain });
  }

  /**
   * 将请求头转换为对象格式
   */
  static headersToObject(headers: RequestHeader[]): Record<string, string> {
    const result: Record<string, string> = {};
    headers.forEach(header => {
      result[header.name] = header.value;
    });
    return result;
  }

  /**
   * 清除所有拦截的请求数据
   */
  static async clearAllRequests(): Promise<boolean> {
    try {
      await chrome.storage.local.set({
        [this.STORAGE_KEY]: {}
      });
      return true;
    } catch (error) {
      console.error('清除请求数据失败:', error);
      return false;
    }
  }

  /**
   * 导出拦截的请求数据
   */
  static async exportRequests(): Promise<string> {
    try {
      const requests = await this.getInterceptedRequests();
      const statistics = await this.getRequestStatistics();
      
      const exportData = {
        requests,
        statistics,
        exportTime: new Date().toISOString(),
        version: '1.0'
      };
      
      return JSON.stringify(exportData, null, 2);
    } catch (error) {
      console.error('导出请求数据失败:', error);
      return '';
    }
  }

  /**
   * 创建请求的唯一ID
   */
  static createRequestId(url: string, timestamp: string): string {
    return `${new URL(url).hostname}_${timestamp}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * 解析URL获取域名和路径
   */
  static parseUrl(url: string): { domain: string; path: string } {
    try {
      const urlObj = new URL(url);
      return {
        domain: urlObj.hostname,
        path: urlObj.pathname + urlObj.search
      };
    } catch (error) {
      return {
        domain: 'unknown',
        path: url
      };
    }
  }

  /**
   * 获取最近的请求
   */
  static async getRecentRequests(limit: number = 50): Promise<InterceptedRequest[]> {
    try {
      const allRequests = await this.getInterceptedRequests();
      return allRequests
        .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
        .slice(0, limit);
    } catch (error) {
      console.error('获取最近请求失败:', error);
      return [];
    }
  }
}