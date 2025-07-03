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
    setTimeout(() => setNotification(null), 3000); // 3秒后自动消失
  }, []);

  return (
    <NotificationContext.Provider value={showNotification}>
      {children}
      {notification && (
        <div
          style={{
            position: 'fixed',
            top: 40,
            right: 40,
            zIndex: 9999,
            minWidth: 240,
            padding: 16,
            background: notification.type === 'error' ? '#fff1f0' : notification.type === 'success' ? '#f6ffed' : '#e6f4ff',
            color: notification.type === 'error' ? '#cf1322' : notification.type === 'success' ? '#389e0d' : '#1677ff',
            border: `1px solid ${notification.type === 'error' ? '#ffa39e' : notification.type === 'success' ? '#b7eb8f' : '#91caff'}`,
            borderRadius: 8,
            boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
            fontSize: 16,
          }}
        >
          <div style={{ fontWeight: 'bold', marginBottom: 4 }}>{notification.message}</div>
          <div>{notification.description}</div>
        </div>
      )}
    </NotificationContext.Provider>
  );
}; 