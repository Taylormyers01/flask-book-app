const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let pythonProcess;
const startupLog = 'App served on port: '

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1000,
    height: 800,
    webPreferences: {
      contextIsolation: true,
    },
  });

  mainWindow.loadURL('http://127.0.0.1:5000/');
  mainWindow.on('closed', () => {
    if (pythonProcess) pythonProcess.kill();
  });
}

function startPythonServer() {
  const backendPath = process.platform === "win32"
      ? path.join(__dirname, "/book_flask/src/dist/app.exe")
      : path.join(__dirname, "/book_flask/src/dist/app");
  // const script = path.join(__dirname, 'flask_server', 'app');
  pythonProcess = spawn(backendPath);
  // pythonProcess = spawn('python3', [backendPath]);

  pythonProcess.stdout.on('data', (data) => {
    const msg = data.toString();
    console.log(msg);
    if (msg.includes(startupLog)) {
      createWindow();
    }
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
    const msg = data.toString();
    console.log(msg);
    if (msg.includes(startupLog)) {
      createWindow();
    }
  });

  pythonProcess.on('close', (code) => {
    console.log(`Python server exited with code ${code}`);
  });

}

app.whenReady().then(startPythonServer);

app.on('window-all-closed', () => {
  app.quit();
});

app.on('before-quit', () => {
  if (pythonProcess) pythonProcess.kill('SIGINT');
});

app.on('quit', () => {
  if (pythonProcess) pythonProcess.kill();
});
