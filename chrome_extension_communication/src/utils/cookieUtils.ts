/**
 * Cookie管理工具类
 * 提供获取、过滤、格式化Cookie的功能
 */

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

export class CookieUtils {
  /**
   * 获取所有Cookie
   */
  static async getAllCookies(): Promise<CookieInfo[]> {
    try {
      const cookies = await chrome.cookies.getAll({});
      return cookies.map(this.formatCookieInfo);
    } catch (error) {
      console.error('获取所有Cookie失败:', error);
      return [];
    }
  }

  /**
   * 根据域名获取Cookie
   */
  static async getCookiesByDomain(domain: string): Promise<CookieInfo[]> {
    try {
      // 处理域名格式
      const url = domain.startsWith('http') ? domain : `https://${domain}`;
      const cookies = await chrome.cookies.getAll({ url });
      return cookies.map(this.formatCookieInfo);
    } catch (error) {
      console.error(`获取域名 ${domain} 的Cookie失败:`, error);
      return [];
    }
  }

  /**
   * 根据Cookie名称获取指定Cookie
   */
  static async getCookieByName(url: string, name: string): Promise<CookieInfo | null> {
    try {
      const cookie = await chrome.cookies.get({ url, name });
      return cookie ? this.formatCookieInfo(cookie) : null;
    } catch (error) {
      console.error(`获取Cookie ${name} 失败:`, error);
      return null;
    }
  }

  /**
   * 获取当前活动标签页的Cookie
   */
  static async getCurrentTabCookies(): Promise<CookieInfo[]> {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab.url) {
        console.warn('无法获取当前标签页URL');
        return [];
      }
      
      const cookies = await chrome.cookies.getAll({ url: tab.url });
      return cookies.map(this.formatCookieInfo);
    } catch (error) {
      console.error('获取当前标签页Cookie失败:', error);
      return [];
    }
  }

  /**
   * 根据多个域名批量获取Cookie
   */
  static async getCookiesByDomains(domains: string[]): Promise<Map<string, CookieInfo[]>> {
    const results = new Map<string, CookieInfo[]>();
    
    for (const domain of domains) {
      const cookies = await this.getCookiesByDomain(domain);
      results.set(domain, cookies);
    }
    
    return results;
  }

  /**
   * 过滤Cookie
   */
  static filterCookies(cookies: CookieInfo[], filter: CookieFilter): CookieInfo[] {
    return cookies.filter(cookie => {
      if (filter.domain && !cookie.domain.includes(filter.domain)) {
        return false;
      }
      if (filter.name && !cookie.name.includes(filter.name)) {
        return false;
      }
      if (filter.path && cookie.path !== filter.path) {
        return false;
      }
      if (filter.secure !== undefined && cookie.secure !== filter.secure) {
        return false;
      }
      if (filter.httpOnly !== undefined && cookie.httpOnly !== filter.httpOnly) {
        return false;
      }
      return true;
    });
  }

  /**
   * 将Cookie格式化为字符串 (用于HTTP请求头)
   */
  static cookiesToString(cookies: CookieInfo[]): string {
    return cookies
      .map(cookie => `${cookie.name}=${cookie.value}`)
      .join('; ');
  }

  /**
   * 将Cookie转换为对象形式
   */
  static cookiesToObject(cookies: CookieInfo[]): Record<string, string> {
    const result: Record<string, string> = {};
    cookies.forEach(cookie => {
      result[cookie.name] = cookie.value;
    });
    return result;
  }

  /**
   * 检查Cookie是否过期
   */
  static isCookieExpired(cookie: CookieInfo): boolean {
    if (!cookie.expirationDate) {
      return false; // 会话Cookie不会过期
    }
    return cookie.expirationDate * 1000 < Date.now();
  }

  /**
   * 获取Cookie的过期时间（人类可读格式）
   */
  static getCookieExpirationText(cookie: CookieInfo): string {
    if (!cookie.expirationDate) {
      return '会话结束时';
    }
    
    const expirationDate = new Date(cookie.expirationDate * 1000);
    return expirationDate.toLocaleString('zh-CN');
  }

  /**
   * 统计Cookie信息
   */
  static getCookieStatistics(cookies: CookieInfo[]) {
    const stats = {
      total: cookies.length,
      httpOnly: 0,
      secure: 0,
      expired: 0,
      domains: new Set<string>(),
      sameSite: {
        strict: 0,
        lax: 0,
        none: 0,
        no_restriction: 0
      }
    };

    cookies.forEach(cookie => {
      if (cookie.httpOnly) stats.httpOnly++;
      if (cookie.secure) stats.secure++;
      if (this.isCookieExpired(cookie)) stats.expired++;
      
      stats.domains.add(cookie.domain);
      
      switch (cookie.sameSite) {
        case 'strict':
          stats.sameSite.strict++;
          break;
        case 'lax':
          stats.sameSite.lax++;
          break;
        case 'no_restriction':
          stats.sameSite.no_restriction++;
          break;
      }
    });

    return {
      ...stats,
      uniqueDomains: stats.domains.size
    };
  }

  /**
   * 删除指定Cookie
   */
  static async deleteCookie(url: string, name: string): Promise<boolean> {
    try {
      const result = await chrome.cookies.remove({ url, name });
      return result !== null;
    } catch (error) {
      console.error(`删除Cookie ${name} 失败:`, error);
      return false;
    }
  }

  /**
   * 清除域名下的所有Cookie
   */
  static async clearDomainCookies(domain: string): Promise<number> {
    try {
      const cookies = await this.getCookiesByDomain(domain);
      let cleared = 0;
      
      for (const cookie of cookies) {
        const url = `${cookie.secure ? 'https' : 'http'}://${cookie.domain}${cookie.path}`;
        const success = await this.deleteCookie(url, cookie.name);
        if (success) cleared++;
      }
      
      return cleared;
    } catch (error) {
      console.error(`清除域名 ${domain} 的Cookie失败:`, error);
      return 0;
    }
  }

  /**
   * 格式化Chrome Cookie对象
   */
  private static formatCookieInfo(cookie: chrome.cookies.Cookie): CookieInfo {
    return {
      name: cookie.name,
      value: cookie.value,
      domain: cookie.domain,
      path: cookie.path,
      httpOnly: cookie.httpOnly,
      secure: cookie.secure,
      sameSite: cookie.sameSite,
      expirationDate: cookie.expirationDate
    };
  }

  /**
   * 预定义的常用域名
   */
  static readonly COMMON_DOMAINS = [
    'google.com',
    'baidu.com',
    'github.com',
    'stackoverflow.com',
    'facebook.com',
    'twitter.com',
    'linkedin.com',
    'youtube.com',
    'amazon.com',
    'temu.com',
    'taobao.com',
    'tmall.com'
  ];
}