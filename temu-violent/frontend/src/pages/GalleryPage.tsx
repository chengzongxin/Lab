import React from "react";
import { Card, Input, Button, Table, Image } from "antd";

const GalleryPage: React.FC = () => {
  return (
    <Card title="图库图片管理">
      <Input.Search
        placeholder="输入图片名"
        enterButton="搜索"
        style={{ width: 300, marginBottom: 16 }}
        onSearch={() => {}}
      />
      <Button type="primary" style={{ marginBottom: 16 }}>批量删除</Button>
      <Table
        rowKey="id"
        columns={[
          { title: "图片", dataIndex: "file_path", render: (url: string) => <Image width={60} src={url} /> },
          { title: "文件名", dataIndex: "file_name" },
          { title: "操作", render: () => <Button danger>删除</Button> }
        ]}
        dataSource={[]}
      />
    </Card>
  );
};

export default GalleryPage; 