const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use the ipcRenderer
contextBridge.exposeInMainWorld(
  'electronAPI', {
    changeApiUrl: (url) => ipcRenderer.send('change-api-url', url),
    getDebugPort: () => ipcRenderer.invoke('get-debug-port'),
    getApiPort: () => ipcRenderer.invoke('get-api-port')
  }
);