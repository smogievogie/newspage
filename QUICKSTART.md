# 🤖 AI新闻收集器 - 快速启动指南

## 📋 系统要求

- Python 3.7 或更高版本
- Windows/macOS/Linux 操作系统
- 网络连接（用于获取新闻）

## 🚀 快速启动

### 方法一：使用启动脚本（推荐）

**Windows用户：**
```bash
# 双击运行
start.bat

# 或在命令行中运行
start.bat
```

**所有平台：**
```bash
python run.py
```

### 方法二：手动启动

1. **安装依赖包**
```bash
pip install -r requirements.txt
```

2. **配置API密钥（可选）**
```bash
# 复制配置文件
cp config.example.py config.py

# 编辑config.py，添加您的API密钥
# - NewsAPI: https://newsapi.org/
# - Reddit API: https://www.reddit.com/prefs/apps
```

3. **启动应用**
```bash
python app.py
```

## 🌐 访问应用

启动成功后，在浏览器中访问：
- **本地访问：** http://localhost:5000
- **局域网访问：** http://你的IP地址:5000

## 📱 功能说明

### 主要功能
- 🔄 **自动收集**：定时从多个源收集AI相关新闻
- 🎯 **智能过滤**：基于关键词和相关性自动筛选
- 📊 **数据分析**：统计热门关键词和新闻源
- 🔍 **搜索功能**：支持标题、内容、关键词搜索
- 📖 **阅读管理**：标记已读/未读状态

### 页面导航
- **首页**：浏览最新AI新闻
- **仪表板**：查看统计数据和分析
- **设置**：配置收集参数和API密钥

## ⚙️ 配置选项

### API配置（可选）
```python
# NewsAPI (免费额度：1000次/天)
NEWSAPI_KEY = 'your_newsapi_key_here'

# Reddit API (免费)
REDDIT_CLIENT_ID = 'your_reddit_client_id'
REDDIT_CLIENT_SECRET = 'your_reddit_client_secret'
REDDIT_USER_AGENT = 'AI News Collector 1.0'
```

### 收集配置
```python
# 更新间隔（分钟）
NEWS_UPDATE_INTERVAL = 30

# 最大文章数
MAX_ARTICLES_PER_SOURCE = 50

# AI关键词
AI_KEYWORDS = [
    'artificial intelligence', 'machine learning', 'deep learning',
    'neural network', 'AI', 'ML', 'DL', 'GPT', 'ChatGPT',
    '人工智能', '机器学习', '深度学习', '神经网络'
]
```

## 🔧 故障排除

### 常见问题

**1. 依赖包安装失败**
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

**2. 端口被占用**
```bash
# 修改app.py中的端口号
app.run(host='0.0.0.0', port=5001)  # 改为5001或其他端口
```

**3. 数据库错误**
```bash
# 删除数据库文件重新初始化
rm news.db
python run.py
```

**4. 新闻收集失败**
- 检查网络连接
- 验证API密钥是否正确
- 查看控制台错误信息

### 日志查看
应用运行时会在控制台显示详细日志，包括：
- 新闻收集状态
- API调用结果
- 错误信息

## 📁 项目结构

```
news101/
├── app.py              # Flask主应用
├── database.py         # 数据库操作
├── news_collector.py   # 新闻收集器
├── config.py          # 配置文件
├── requirements.txt   # 依赖包列表
├── run.py            # 启动脚本
├── start.bat         # Windows启动脚本
├── test_app.py       # 测试脚本
├── templates/        # HTML模板
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   └── settings.html
└── static/          # 静态资源
    ├── css/style.css
    └── js/app.js
```

## 🔄 更新和维护

### 数据清理
```bash
# 清理7天前的旧新闻
python -c "from database import NewsDatabase; db = NewsDatabase(); db.cleanup_old_articles(7)"
```

### 备份数据
```bash
# 备份数据库
cp news.db news_backup_$(date +%Y%m%d).db
```

### 重置应用
```bash
# 删除数据库和配置
rm news.db config.py

# 重新启动
python run.py
```

## 📞 技术支持

如果遇到问题：
1. 查看控制台错误信息
2. 检查配置文件是否正确
3. 确认网络连接正常
4. 运行测试脚本：`python test_app.py`

## 🎯 使用建议

1. **首次使用**：建议先不配置API密钥，使用RSS源测试
2. **API配置**：NewsAPI有免费额度限制，建议合理设置更新间隔
3. **关键词优化**：根据需要调整AI_KEYWORDS列表
4. **定期清理**：定期清理旧新闻以保持数据库性能

---

🎉 **恭喜！您的AI新闻收集器已准备就绪！**

开始收集最新的AI资讯，保持对人工智能领域的敏锐洞察！