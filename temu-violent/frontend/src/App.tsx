import { Layout, Menu } from 'antd';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
  useLocation
} from 'react-router-dom';
import {
  SettingOutlined,
  TableOutlined,
  SearchOutlined,
  PictureOutlined
} from '@ant-design/icons';
import './App.css';
import ProductList from './pages/ProductList';
import ProductDetail from './pages/ProductDetail';
import ProductForm from './pages/ProductForm';
import ConfigPage from './pages/ConfigPage';
import ProductPage from './pages/ProductPage';
import GalleryPage from './pages/GalleryPage';
import { ProductListProvider } from './pages/ProductListContext';
import { GlobalNotificationProvider } from './pages/GlobalNotification';

const { Header, Sider, Content } = Layout;

const menuItems = [
  { key: 'config', icon: <SettingOutlined />, label: <Link to="/config">配置管理</Link> },
  { key: 'compliance', icon: <TableOutlined />, label: <Link to="/compliance">违规商品</Link> },
  { key: 'product', icon: <SearchOutlined />, label: <Link to="/product">商品搜索</Link> },
  { key: 'gallery', icon: <PictureOutlined />, label: <Link to="/gallery">图库管理</Link> },
];

function AppLayout() {
  const location = useLocation();
  const selectedKey = menuItems.find(item => location.pathname.startsWith(`/${item.key}`))?.key || 'compliance';
  return (
    <Layout style={{ minHeight: '100vh', width: '100vw' }}>
      <Sider width={200} style={{ background: '#fff' }}>
        <div style={{ height: 32, margin: 16, color: '#1890ff', fontWeight: 'bold', fontSize: 18 }}>TEMU工具箱</div>
        <Menu mode="inline" selectedKeys={[selectedKey]} style={{ height: '100%', borderRight: 0 }} items={menuItems} />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', padding: 0, fontSize: 20, fontWeight: 'bold', textAlign: 'center' }}>
          TEMU 违规商品&图库管理平台
        </Header>
        <Content style={{
          margin: '0',
          background: '#fff',
          padding: 24,
          minHeight: '100%',
          flex: 1,
        }}>
          <Routes>
            <Route path="/config" element={<ConfigPage />} />
            <Route path="/compliance" element={<ProductList />} />
            <Route path="/compliance/new" element={<ProductForm />} />
            <Route path="/compliance/:spu_id" element={<ProductDetail />} />
            <Route path="/product" element={<ProductPage />} />
            <Route path="/gallery" element={<GalleryPage />} />
            <Route path="*" element={<ProductList />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
}

function App() {
  return (
    <Router>
      <GlobalNotificationProvider>
        <ProductListProvider>
          <AppLayout />
        </ProductListProvider>
      </GlobalNotificationProvider>
    </Router>
  );
}

export default App;
