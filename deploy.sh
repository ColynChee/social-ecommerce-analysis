#!/bin/bash

# 构建项目
npm run build

# 进入dist目录
cd dist

# 初始化git（如果还没有）
git init
git add -A
git commit -m "Deploy to GitHub Pages"

# 推送到gh-pages分支
git push -f https://github.com/YOUR_USERNAME/YOUR_REPO.git master:gh-pages

cd ..
echo "部署完成！访问 https://YOUR_USERNAME.github.io/YOUR_REPO/"
