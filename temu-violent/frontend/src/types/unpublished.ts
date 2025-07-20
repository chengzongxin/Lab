export interface UnpublishedSkcRecord {
  skcId: string;
  productId: string;
  productName: string;
  mainImageUrl?: string;
  collectTime: string;
  source: string;
}

export interface CategoryRecord {
  catId: number;
  catName: string;
  skcRecords: UnpublishedSkcRecord[];
  lastUpdated: string;
  totalCount: number;
}

export interface UnpublishedStorageData {
  categories: { [catId: string]: CategoryRecord };
  globalStats: {
    totalSkcCount: number;
    totalCategoryCount: number;
    lastUpdated: string;
    collectHistory: Array<{
      time: string;
      action: string;
      count: number;
      source: string;
    }>;
  };
  version: string;
} 