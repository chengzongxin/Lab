import React, { useState, useCallback, createContext, useContext } from 'react';

type NotificationType = 'info' | 'error' | 'success';

interface Notification {
  type: NotificationType;
  message: string;
  description?: string;
}

const NotificationContext = createContext<(n: Notification) => void>(() => {});

export const useGlobalNotification = () => useContext(NotificationContext);

export const GlobalNotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [notification, setNotification] = useState<Notification | null>(null);

  const showNotification = useCallback((n: Notification) => {
    setNotification(n);
    setTimeout(() => setNotification(null), 5000); // 5秒后自动消失
  }, []);

  return (
    <NotificationContext.Provider value={showNotification}>
      {children}
      {notification && (
        <div
          style={{
            position: 'fixed',
            top: 24,
            right: 24,
            zIndex: 9999,
            minWidth: 320,
            maxWidth: 480,
            padding: '16px 20px',
            background: '#ffffff',
            border: `1px solid ${notification.type === 'error' ? '#ff4d4f' : notification.type === 'success' ? '#52c41a' : '#1890ff'}`,
            borderRadius: 12,
            boxShadow: '0 8px 24px rgba(0,0,0,0.12), 0 2px 8px rgba(0,0,0,0.08)',
            fontSize: 14,
            lineHeight: 1.5,
            animation: 'slideInRight 0.3s ease-out',
            display: 'flex',
            alignItems: 'flex-start',
            gap: 12,
          }}
        >
          {/* 左侧图标 */}
          <div
            style={{
              width: 20,
              height: 20,
              borderRadius: '50%',
              background: notification.type === 'error' ? '#ff4d4f' : notification.type === 'success' ? '#52c41a' : '#1890ff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
              marginTop: 2,
            }}
          >
            <span style={{ color: '#fff', fontSize: 12, fontWeight: 'bold' }}>
              {notification.type === 'error' ? '!' : notification.type === 'success' ? '✓' : 'i'}
            </span>
          </div>
          
          {/* 右侧内容 */}
          <div style={{ flex: 1 }}>
            <div style={{ 
              fontWeight: 600, 
              marginBottom: notification.description ? 4 : 0,
              color: '#262626',
              fontSize: 15,
            }}>
              {notification.message}
            </div>
            {notification.description && (
              <div style={{ 
                color: '#8c8c8c',
                fontSize: 13,
                lineHeight: 1.4,
              }}>
                {notification.description}
              </div>
            )}
          </div>
          
          {/* 关闭按钮 */}
          <button
            onClick={() => setNotification(null)}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: 4,
              borderRadius: 4,
              color: '#bfbfbf',
              fontSize: 16,
              lineHeight: 1,
              marginTop: -2,
              marginRight: -4,
              transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = '#f5f5f5';
              e.currentTarget.style.color = '#8c8c8c';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'none';
              e.currentTarget.style.color = '#bfbfbf';
            }}
          >
            ×
          </button>
        </div>
      )}
      
      {/* 添加动画样式 */}
      <style>
        {`
          @keyframes slideInRight {
            from {
              transform: translateX(100%);
              opacity: 0;
            }
            to {
              transform: translateX(0);
              opacity: 1;
            }
          }
        `}
      </style>
    </NotificationContext.Provider>
  );
}; 