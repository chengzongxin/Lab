import React, { createContext, useContext, useState } from "react";

// 商品类型定义
interface Product {
  spu_id: string;
  goods_name: string;
  goods_img_url?: string;
  site_num: number;
  punish_detail_list: any[];
}

// Context 状态类型
interface ProductListState {
  products: Product[];
  setProducts: React.Dispatch<React.SetStateAction<Product[]>>;
  page: number;
  setPage: React.Dispatch<React.SetStateAction<number>>;
  pageSize: number;
  setPageSize: React.Dispatch<React.SetStateAction<number>>;
  total: number;
  setTotal: React.Dispatch<React.SetStateAction<number>>;
}

// 创建 Context
const ProductListContext = createContext<ProductListState | undefined>(undefined);

// 自定义 Hook，便于在组件中使用 Context
export const useProductListContext = () => {
  const ctx = useContext(ProductListContext);
  if (!ctx) throw new Error("useProductListContext 必须在 ProductListProvider 内使用");
  return ctx;
};

// Provider 组件，包裹在 App 顶层
export const ProductListProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [products, setProducts] = useState<Product[]>([]);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [total, setTotal] = useState(0);

  return (
    <ProductListContext.Provider value={{
      products, setProducts, page, setPage, pageSize, setPageSize, total, setTotal
    }}>
      {children}
    </ProductListContext.Provider>
  );
}; 