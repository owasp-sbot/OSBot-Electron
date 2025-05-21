// main.js
const { app, BrowserWindow, Menu, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');


// Keep a global reference of the window object and Python process
let mainWindow;
let pythonProcess;
let debugPort;
let apiPort;

function findAvailablePort(startPort) {
  const net = require('net');
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.unref();
    server.on('error', reject);
    server.listen(startPort, () => {
      const port = server.address().port;
      server.close(() => {
        resolve(port);
      });
    });
  });
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function set_debug_port() {     // Set Chrome debugging port
  debugPort = await findAvailablePort(10000);
  console.log('Chrome Debug Port', debugPort)
  app.commandLine.appendSwitch('remote-debugging-port', debugPort.toString());
  // added remote port to connect via Playwright
  //app.commandLine.appendSwitch('remote-debugging-port', '9222');
}
// Start Python FastAPI server and set up the app
async function initialize() {
  apiPort   = await findAvailablePort(20000);

  console.log('FastApi Port', apiPort)

  // wait 1000ms   for fastapi to start (todo: remove this logic from here)
  await sleep(1000)
  // Start the Python FastAPI server
  startPythonServer();

  // Create the main window
  createWindow();
}

function startPythonServer() {
  // Determine Python executable (use 'python' or 'python3' based on your environment)
  const pythonExecutable = process.platform === 'win32' ? 'python' : 'python3';

  // Start the FastAPI server with the random port
  pythonProcess = spawn(pythonExecutable, [
    path.join(__dirname, '../../osbot_electron/server.py'),
    '--port', apiPort.toString()
  ]);

  // Log stdout from Python
  pythonProcess.stdout.on('data', (data) => {
    console.log(`Python stdout: ${data}`);
  });

  // Log stderr from Python
  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python stderr: ${data}`);
  });

  // Handle Python process exit
  pythonProcess.on('close', (code) => {
    console.log(`Python process exited with code ${code}`);
  });
}

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
  const apiUrl = `http://localhost:${apiPort}/docs`;
  console.log(`Loading API URL: ${apiUrl}`);
  mainWindow.loadURL(apiUrl);

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

function setup_icon() {
  const macIconPath = path.join(__dirname, '../assets/icons/osbot-electron.icon.icns');
  const winIconPath = path.join(__dirname, '../assets/icons/osbot-electron.icon.ico');
  const linuxIconPath = path.join(__dirname, '../assets/icons/osbot-electron.icon.png');

  if (process.platform === 'darwin') {
    app.dock.setIcon(path.join(__dirname, '../assets/icons/osbot-electron.icon.png'));

    console.log('Checking icon paths:');
    console.log('macOS icon exists:', fs.existsSync(macIconPath));
    console.log('Windows icon exists:', fs.existsSync(winIconPath));
    console.log('Linux icon exists:', fs.existsSync(linuxIconPath));
  }
}

function setup() {
  set_debug_port()      // set the chrome debug port
  setup_icon()
}

setup()                 // need this since we can use async in the top level

// This method will be called when Electron has finished initialization
app.on('ready', initialize);

// Quit when all windows are closed
app.on('window-all-closed', function() {
  // Kill Python process
  if (pythonProcess) {
    // On Windows use taskkill to ensure child processes are stopped
    if (process.platform === 'win32') {
      spawn('taskkill', ['/pid', pythonProcess.pid, '/f', '/t']);
    } else {
      pythonProcess.kill();
    }
  }

  app.quit();
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

// Expose the debug port for client.py to connect to
ipcMain.handle('get-debug-port', () => {
  return debugPort;
});

// Expose the API port for client.py to use
ipcMain.handle('get-api-port', () => {
  return apiPort;
});