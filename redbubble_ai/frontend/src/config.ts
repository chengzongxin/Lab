// 动态获取API地址
// 如果是本地开发(localhost)，或者局域网访问(IP)，都使用当前访问的hostname + 8000端口
export const API_BASE_URL = `http://${window.location.hostname}:8000`;
