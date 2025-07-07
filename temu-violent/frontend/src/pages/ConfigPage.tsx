import React, { useEffect } from "react";
import { Card, Form, Input, Button, message } from "antd";
import { useGlobalNotification } from "./GlobalNotification";

const ConfigPage: React.FC = () => {
  const [form] = Form.useForm();
  const notify = useGlobalNotification();

  // 获取配置
  useEffect(() => {
    fetch("/api/config")
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          form.setFieldsValue(data.data);
        }
      });
  }, [form]);

  // 保存配置
  const onFinish = async (values: any) => {
    const res = await fetch("/api/config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(values)
    });
    const data = await res.json();
    if (data.success) {
      notify({ type: 'success', message: "配置已保存！" });
    } else {
      notify({ type: 'error', message: data.msg || "保存失败" });
    }
  };

  // 清除配置
  const handleClearConfig = async () => {
    // 使用浏览器原生的确认对话框
    const confirmed = window.confirm('确定要清除所有配置吗？此操作不可撤销。');
    if (!confirmed) {
      return;
    }
    
    try {
      const res = await fetch("/api/config", {
        method: "DELETE"
      });
      const data = await res.json();
      if (data.success) {
        notify({ type: 'success', message: "配置已清除！" });
        // 清空表单
        form.resetFields();
      } else {
        notify({ type: 'error', message: data.msg || "清除失败" });
      }
    } catch (error) {
      notify({ type: 'error', message: "清除配置时发生错误" });
    }
  };

  // 64 Header ， 48 Card Padding
  return (
    <Card title="配置管理" style={{ height: 'calc(100vh - 64px - 48px)' }}> 
      <Form form={form} labelCol={{ span: 4 }} wrapperCol={{ span: 8 }} onFinish={onFinish}>
        <Form.Item label="商家中心Cookie" name="seller_cookie"><Input /></Form.Item>
        <Form.Item label="合规中心Cookie" name="compliance_cookie"><Input /></Form.Item>
        <Form.Item label="蓝站Cookie" name="blue_cookie"><Input /></Form.Item>
        <Form.Item label="蓝站Token" name="blue_token"><Input /></Form.Item>
        <Form.Item label="MallId" name="mallid"><Input /></Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" style={{ marginRight: 8 }}>保存配置</Button>
          <Button danger onClick={handleClearConfig}>清除配置</Button>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default ConfigPage; 