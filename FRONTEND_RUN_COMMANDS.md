# 前端项目运行指令

## ⚠️ 重要提示

所有前端项目都使用 **Vite 7.2.2**，需要 **Node.js 20.19+ 或 22.12+**。

**运行前端前，请先切换 Node.js 版本：**
```powershell
nvm use 22.12.0
```

---

## 1. 展示前端 (mmiiot_frontend)
**端口**: `10061`

```powershell
cd E:\code\IIOT_code\mmiiot_frontend
nvm use 22.12.0
npm run dev
```

**访问地址**: http://localhost:10061

---

## 2. 管理前端 (admin_frontend)
**端口**: `10062`

```powershell
cd E:\code\IIOT_code\admin_frontend
nvm use 22.12.0
npm run dev
```

**访问地址**: http://localhost:10062

---

## 3. LenovoFMS
**端口**: `10063`

```powershell
cd E:\code\IIOT_code\LenovoFMS
nvm use 22.12.0
npm run dev
```

**访问地址**: http://localhost:10063

---

## 4. LenovoPLM
**端口**: `10064`

```powershell
cd E:\code\IIOT_code\LenovoPLM
nvm use 22.12.0
npm run dev
```

**访问地址**: http://localhost:10064

---

## 5. TellhowTraffic
**端口**: `10065`

```powershell
cd E:\code\IIOT_code\TellhowTraffic
nvm use 22.12.0
npm run dev
```

**访问地址**: http://localhost:10065

---

## 停止服务

在运行服务的终端窗口中按 `Ctrl + C` 即可停止。

---

## 快速切换 Node.js 版本

```powershell
# 切换到 Node.js 22（用于前端项目）
nvm use 22.12.0

# 切换回 Node.js 18（如果需要）
nvm use 18.18.2

# 查看当前版本
node --version
```

---

## 注意事项

1. **每次运行前端前**，确保已切换到 Node.js 22.12.0
2. **如果依赖未安装**，先运行 `npm install`
3. **不同终端窗口**需要分别执行 `nvm use 22.12.0`

