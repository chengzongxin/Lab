import React from "react";
import { Card, Table, Button } from "antd";

const ProductList: React.FC = () => {
  return (
    <Card title="违规商品列表">
      <Button type="primary" style={{ marginBottom: 16 }}>批量下架</Button>
      <Table
        rowKey="spu_id"
        columns={[
          { title: "商品ID", dataIndex: "spu_id" },
          { title: "商品名称", dataIndex: "goods_name" },
          { title: "操作", render: () => <Button>下架</Button> }
        ]}
        dataSource={[]}
      />
    </Card>
  );
};

export default ProductList; 