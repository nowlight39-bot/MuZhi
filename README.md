# 高考择校助手 - A2A 后端服务

## 本地启动

```bash
pip install flask
python server.py
```

访问 http://localhost:5000/health 验证

## 部署到 Vercel

1. 将代码 push 到 GitHub 仓库
2. 在 Vercel 中导入该仓库
3. 设置环境变量：
   - `A2A_ACCESS_KEY`：你的 Access Key
   - `A2A_SECRET_KEY`：你的 Secret Key
4. 部署后获得 URL，如 `https://xxx.vercel.app`

## 在小艺开放平台配置

1. 进入智能体编排 → A2A 基础配置
2. API URL 填：`https://你的域名/agent/message`
3. 认证方式：AK/SK
4. Access Key 和 Secret Key 与上面保持一致
