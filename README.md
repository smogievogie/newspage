# AI新闻收集器 (AI News Collector)

一个自动收集AI领域最新资讯的应用程序，专为AI科技博主设计。

## 功能特性

- 🤖 自动收集多个来源的AI相关新闻
- 📱 现代化Web界面，支持移动端
- 🔍 智能关键词过滤和分类
- ⏰ 定时自动更新
- 📊 新闻趋势分析
- 💾 本地数据存储
- 🌐 支持多个新闻源API

## 技术栈

- **后端**: Python Flask
- **前端**: HTML5, CSS3, JavaScript
- **数据库**: SQLite
- **新闻源**: NewsAPI, Reddit API, RSS订阅
- **部署**: 支持本地运行和云部署

## 快速开始

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 配置API密钥
```bash
cp config.example.py config.py
# 编辑config.py添加您的API密钥
```

3. 运行应用
```bash
python app.py
```

4. 访问 http://localhost:5000

## 配置说明

在 `config.py` 中配置以下API密钥：
- NewsAPI密钥 (免费获取: https://newsapi.org/)
- Reddit API密钥 (可选)

## 使用方法

1. 启动应用后，系统会自动开始收集AI相关新闻
2. 在Web界面查看最新资讯
3. 可以设置关键词过滤器来精确匹配您感兴趣的内容
4. 支持按时间、热度、相关性排序

## 许可证

MIT License