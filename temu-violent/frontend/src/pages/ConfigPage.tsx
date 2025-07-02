import React from "react";
import { Card, Form, Input, Button, message } from "antd";

const ConfigPage: React.FC = () => {
  const onFinish = (values: any) => {
    // 这里可以调用后端保存配置接口
    message.success("配置已保存！");
  };

  return (
    <Card title="配置管理">
      <Form labelCol={{ span: 4 }} wrapperCol={{ span: 8 }} onFinish={onFinish}>
        <Form.Item label="商家中心Cookie" name="seller_cookie" rules={[{ required: true }]}> <Input /> </Form.Item>
        <Form.Item label="合规中心Cookie" name="compliance_cookie" rules={[{ required: true }]}> <Input /> </Form.Item>
        <Form.Item label="蓝站Token" name="blue_token" rules={[{ required: true }]}> <Input /> </Form.Item>
        <Form.Item label="MallId" name="mallid" rules={[{ required: true }]}> <Input /> </Form.Item>
        <Form.Item> <Button type="primary" htmlType="submit">保存配置</Button> </Form.Item>
      </Form>
    </Card>
  );
};

export default ConfigPage; 