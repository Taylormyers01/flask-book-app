const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let pythonProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1000,
    height: 800,
    webPreferences: {
      contextIsolation: true,
    },
  });

  mainWindow.loadURL('http://127.0.0.1:5000/hello');
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function startPythonServer() {
  const script = path.join(__dirname, 'flask_server', 'app');
  pythonProcess = spawn(script);

  pythonProcess.stdout.on('data', (data) => {
    const msg = data.toString();
    console.log(msg);
    if (msg.includes('Running on')) {
      createWindow();
    }
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
    const msg = data.toString();
    console.log(msg);
    if (msg.includes('Running on')) {
      createWindow();
    }
  });

  pythonProcess.on('close', (code) => {
    console.log(`Python server exited with code ${code}`);
  });
}

app.whenReady().then(startPythonServer);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('quit', () => {
  if (pythonProcess) pythonProcess.kill();
});
