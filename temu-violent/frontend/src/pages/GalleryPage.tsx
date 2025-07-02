import React, { useState } from "react";
import { Card, Input, Button, Table, Image, message } from "antd";

interface GalleryItem {
  id: string;
  file_name: string;
  file_path: string;
}

const GalleryPage: React.FC = () => {
  const [search, setSearch] = useState("");
  const [list, setList] = useState<GalleryItem[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (value: string) => {
    setLoading(true);
    const res = await fetch("/api/blue/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ picture_name: value }),
    });
    const data = await res.json();
    if (data.success) {
      setList(data.list);
    } else {
      message.error(data.msg || "查询失败");
    }
    setLoading(false);
  };

  return (
    <Card title="图库图片管理">
      <Input.Search
        placeholder="输入图片名"
        enterButton="搜索"
        style={{ width: 300, marginBottom: 16 }}
        onSearch={handleSearch}
        loading={loading}
      />
      <Button type="primary" style={{ marginBottom: 16 }}>批量删除</Button>
      <Table
        rowKey="id"
        columns={[
          { title: "图片", dataIndex: "file_path", render: (url: string) => <Image width={60} src={url} /> },
          { title: "文件名", dataIndex: "file_name" },
          { title: "操作", render: () => <Button danger>删除</Button> }
        ]}
        dataSource={list}
        loading={loading}
      />
    </Card>
  );
};

export default GalleryPage; 