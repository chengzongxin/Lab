import type { UnpublishedStorageData, CategoryRecord } from '../types/unpublished';

const STORAGE_KEY = 'temu_unpublished_skc_records';
const STORAGE_VERSION = '1.0';

class UnpublishedStorageService {
  getData(): UnpublishedStorageData {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      if (!data) return this.getDefaultData();
      
      const parsed = JSON.parse(data);
      if (parsed.version !== STORAGE_VERSION) {
        return this.migrateData(parsed);
      }
      return parsed;
    } catch (error) {
      console.error('获取存储数据失败:', error);
      return this.getDefaultData();
    }
  }

  saveData(data: UnpublishedStorageData): boolean {
    try {
      data.globalStats.lastUpdated = new Date().toISOString();
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
      return true;
    } catch (error) {
      console.error('保存数据失败:', error);
      return false;
    }
  }

  addSkcRecords(records: Array<{
    skcId: string;
    productId: string;
    productName: string;
    mainImageUrl?: string;
    category: { catId: number; catName: string };
    source: string;
  }>): boolean {
    const data = this.getData();
    const now = new Date().toISOString();
    
    records.forEach(record => {
      const catKey = record.category.catId.toString();
      
      if (!data.categories[catKey]) {
        data.categories[catKey] = {
          catId: record.category.catId,
          catName: record.category.catName,
          skcRecords: [],
          lastUpdated: now,
          totalCount: 0
        };
      }
      
      const exists = data.categories[catKey].skcRecords.some(
        existing => existing.skcId === record.skcId
      );
      
      if (!exists) {
        data.categories[catKey].skcRecords.push({
          skcId: record.skcId,
          productId: record.productId,
          productName: record.productName,
          mainImageUrl: record.mainImageUrl,
          collectTime: now,
          source: record.source
        });
        data.categories[catKey].totalCount++;
        data.categories[catKey].lastUpdated = now;
      }
    });

    this.updateGlobalStats(data);
    
    data.globalStats.collectHistory.unshift({
      time: now,
      action: '批量收集',
      count: records.length,
      source: records[0]?.source || 'unknown'
    });
    
    if (data.globalStats.collectHistory.length > 100) {
      data.globalStats.collectHistory = data.globalStats.collectHistory.slice(0, 100);
    }

    return this.saveData(data);
  }

  deleteCategory(catId: number): boolean {
    const data = this.getData();
    const catKey = catId.toString();
    
    if (data.categories[catKey]) {
      delete data.categories[catKey];
      this.updateGlobalStats(data);
      return this.saveData(data);
    }
    return false;
  }

  clearAllData(): boolean {
    try {
      localStorage.removeItem(STORAGE_KEY);
      return true;
    } catch (error) {
      console.error('清空数据失败:', error);
      return false;
    }
  }

  private getDefaultData(): UnpublishedStorageData {
    return {
      categories: {},
      globalStats: {
        totalSkcCount: 0,
        totalCategoryCount: 0,
        lastUpdated: new Date().toISOString(),
        collectHistory: []
      },
      version: STORAGE_VERSION
    };
  }

  private updateGlobalStats(data: UnpublishedStorageData): void {
    const categories = Object.values(data.categories);
    data.globalStats.totalCategoryCount = categories.length;
    data.globalStats.totalSkcCount = categories.reduce(
      (sum, cat) => sum + cat.totalCount, 0
    );
  }

  private migrateData(oldData: any): UnpublishedStorageData {
    console.log('执行数据迁移...');
    return this.getDefaultData();
  }
}

export const unpublishedStorage = new UnpublishedStorageService(); 