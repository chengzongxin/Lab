import React, { createContext, useContext, useState, useCallback } from 'react';
import { message } from 'antd';
import { unpublishedStorage } from '../utils/unpublishedStorage';
import type { UnpublishedStorageData } from '../types/unpublished';

interface UnpublishedRecordsContextType {
  data: UnpublishedStorageData;
  addRecords: (records: any[]) => void;
  deleteCategory: (catId: number) => void;
  clearAll: () => void;
  refresh: () => void;
  clearAllData: () => void; // 新增：直接清空数据的方法
}

const UnpublishedRecordsContext = createContext<UnpublishedRecordsContextType>({} as any);

export const useUnpublishedRecords = () => useContext(UnpublishedRecordsContext);

export const UnpublishedRecordsProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [data, setData] = useState<UnpublishedStorageData>(() => unpublishedStorage.getData());

  const addRecords = useCallback((records: any[]) => {
    if (unpublishedStorage.addSkcRecords(records)) {
      setData(unpublishedStorage.getData());
      message.success(`成功添加 ${records.length} 条SKC记录`);
    } else {
      message.error('添加记录失败');
    }
  }, []);

  const deleteCategory = useCallback((catId: number) => {
    if (unpublishedStorage.deleteCategory(catId)) {
      setData(unpublishedStorage.getData());
      message.success('删除类目成功');
    } else {
      message.error('删除类目失败');
    }
  }, []);

  const clearAll = useCallback(() => {
    // 这个方法现在只用于显示确认提示，实际清空操作在页面组件中处理
    message.info('请点击"清空记录"按钮进行确认');
  }, []);

  const clearAllData = useCallback(() => {
    try {
      if (unpublishedStorage.clearAllData()) {
        setData(unpublishedStorage.getData());
        message.success('已清空所有数据');
      } else {
        message.error('清空数据失败');
      }
    } catch (error) {
      console.error('清空数据时出错:', error);
      message.error('清空数据失败，请重试');
    }
  }, []);

  const refresh = useCallback(() => {
    setData(unpublishedStorage.getData());
  }, []);

  return (
    <UnpublishedRecordsContext.Provider value={{
      data,
      addRecords,
      deleteCategory,
      clearAll,
      refresh,
      clearAllData
    }}>
      {children}
    </UnpublishedRecordsContext.Provider>
  );
}; 