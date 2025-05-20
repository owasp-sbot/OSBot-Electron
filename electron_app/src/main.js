// main.js
const { app, BrowserWindow, Menu, ipcMain } = require('electron');
const path = require('path');
const url = require('url');

// Keep a global reference of the window object to prevent garbage collection
let mainWindow;

// FastAPI server URL - this should be configurable in the final app
const DEFAULT_API_URL = 'http://localhost:8000/docs';

function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  // Load the FastAPI Swagger UI
  mainWindow.loadURL(DEFAULT_API_URL);

  // Open DevTools in development
  if (process.env.NODE_ENV === 'development') {
    mainWindow.webContents.openDevTools();
  }

  // Emitted when the window is closed
  mainWindow.on('closed', function() {
    // Dereference the window object
    mainWindow = null;
  });

  // Create menu
  const menu = Menu.buildFromTemplate([
    {
      label: 'File',
      submenu: [
        {
          label: 'Change API URL',
          click: () => {
            // Create a window to input a new API URL
            createUrlWindow();
          }
        },
        { type: 'separator' },
        {
          label: 'Exit',
          accelerator: process.platform === 'darwin' ? 'Command+Q' : 'Ctrl+Q',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: 'View',
      submenu: [
        {
          label: 'Reload',
          accelerator: 'CmdOrCtrl+R',
          click: (item, focusedWindow) => {
            if (focusedWindow) focusedWindow.reload();
          }
        },
        {
          label: 'Toggle Developer Tools',
          accelerator: process.platform === 'darwin' ? 'Alt+Command+I' : 'Ctrl+Shift+I',
          click: (item, focusedWindow) => {
            if (focusedWindow) focusedWindow.webContents.toggleDevTools();
          }
        },
        { type: 'separator' },
        { role: 'resetzoom' },
        { role: 'zoomin' },
        { role: 'zoomout' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    }
  ]);

  Menu.setApplicationMenu(menu);
}

// Function to create a window for changing the API URL
function createUrlWindow() {
  const urlWindow = new BrowserWindow({
    width: 400,
    height: 200,
    parent: mainWindow,
    modal: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  urlWindow.loadFile('src/url-change.html');
}

// This method will be called when Electron has finished initialization
app.on('ready', createWindow);

// Quit when all windows are closed
app.on('window-all-closed', function() {
  // On macOS applications commonly stay open until explicitly quit
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', function() {
  // On macOS it's common to re-create a window when the dock icon is clicked
  if (mainWindow === null) createWindow();
});

// Handle the URL change from the URL change window
ipcMain.on('change-api-url', (event, newUrl) => {
  if (mainWindow && newUrl) {
    mainWindow.loadURL(newUrl);
  }
});