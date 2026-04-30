# 部署指南

## GitHub Pages 部署步骤

### 1. 创建GitHub仓库

在GitHub上创建一个新仓库，命名为 `社交电商用户行为分析` 或其他名称。

### 2. 添加远程仓库

```bash
cd "d:\大数据可视化与可视分析\社交电商用户行为分析"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### 3. 配置GitHub Pages

在GitHub仓库设置中：
1. 进入 **Settings** → **Pages**
2. 选择 **Deploy from a branch**
3. 选择分支为 `main`，目录为 `/root`（或 `/docs`）

### 4. 构建并部署

```bash
npm run build
```

将 `dist/` 目录的内容复制到仓库根目录或 `docs/` 目录，然后推送：

```bash
git add .
git commit -m "Deploy to GitHub Pages"
git push
```

### 5. 访问网站

等待几分钟后，访问：
```
https://YOUR_USERNAME.github.io/YOUR_REPO/
```

## 本地测试

部署前可以本地测试：

```bash
npm run dev
```

访问 `http://localhost:5173` 查看效果。

## 常见问题

**Q: 资源加载失败？**
A: 检查 `vite.config.js` 中的 `base` 路径是否正确。应该是 `/YOUR_REPO/`

**Q: 数据文件加载失败？**
A: 确保 `data/` 目录在 `public/` 或 `dist/` 中，或者在构建时复制过去。

**Q: 样式不显示？**
A: 检查浏览器控制台是否有CORS错误，确保所有资源路径正确。
