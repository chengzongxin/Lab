import React, { createContext, useContext, useState } from "react";

interface Product {
  productId: string;
  productName: string;
  mainImageUrl?: string;
  productSkcId?: string;
  skcStatus?: number;
  skcSiteStatus?: number;
  leafCat?: { catId: number; catName: string };
  productSkuSummaries?: any[];
  createdAt?: string;
  price?: number;
  virtualStock?: number;
  categories?: any;
}

interface ProductSearchState {
  searchName: string;
  setSearchName: React.Dispatch<React.SetStateAction<string>>;
  searchIds: string;
  setSearchIds: React.Dispatch<React.SetStateAction<string>>;
  products: Product[];
  setProducts: React.Dispatch<React.SetStateAction<Product[]>>;
  selectedRowKeys: React.Key[];
  setSelectedRowKeys: React.Dispatch<React.SetStateAction<React.Key[]>>;
}

const ProductSearchContext = createContext<ProductSearchState | undefined>(undefined);

export const useProductSearchContext = () => {
  const ctx = useContext(ProductSearchContext);
  if (!ctx) throw new Error("useProductSearchContext 必须在 ProductSearchProvider 内使用");
  return ctx;
};

export const ProductSearchProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [searchName, setSearchName] = useState("");
  const [searchIds, setSearchIds] = useState("");
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);

  return (
    <ProductSearchContext.Provider value={{
      searchName, setSearchName, searchIds, setSearchIds, products, setProducts, selectedRowKeys, setSelectedRowKeys
    }}>
      {children}
    </ProductSearchContext.Provider>
  );
}; 