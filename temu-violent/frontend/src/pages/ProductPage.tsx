import React from "react";
import { Card, Input, Button, Table } from "antd";

const ProductPage: React.FC = () => {
  return (
    <Card title="商品搜索">
      <Input.Search
        placeholder="输入商品ID或名称"
        enterButton="搜索"
        style={{ width: 300, marginBottom: 16 }}
        onSearch={() => {}}
      />
      <Table
        rowKey="productId"
        columns={[
          { title: "商品ID", dataIndex: "productId" },
          { title: "商品名称", dataIndex: "productName" },
          { title: "操作", render: () => <Button>下架</Button> }
        ]}
        dataSource={[]}
      />
    </Card>
  );
};

export default ProductPage; 