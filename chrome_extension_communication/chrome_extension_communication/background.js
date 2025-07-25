chrome.action.onClicked.addListener((tab) => {
  const port = chrome.runtime.connectNative('com.demo.native_messaging');
  port.postMessage({ text: "你好，Python！" });
  port.onMessage.addListener((msg) => {
    console.log("收到Python回应：", msg);
    alert("收到Python回应：" + JSON.stringify(msg));
  });
  port.onDisconnect.addListener(() => {
    console.log("与Python断开连接");
  });
}); 