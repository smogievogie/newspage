# 配置文件示例
# 复制此文件为 config.py 并填入您的API密钥

# NewsAPI配置 (免费获取: https://newsapi.org/)
NEWSAPI_KEY = "your_newsapi_key_here"

# Reddit API配置 (可选)
REDDIT_CLIENT_ID = "your_reddit_client_id"
REDDIT_CLIENT_SECRET = "your_reddit_client_secret"
REDDIT_USER_AGENT = "AI News Collector 1.0"

# 应用配置
APP_CONFIG = {
    'SECRET_KEY': 'your_secret_key_here',
    'DEBUG': True,
    'HOST': '0.0.0.0',
    'PORT': 5000
}

# 数据库配置
DATABASE_PATH = 'news.db'

# 新闻收集配置
NEWS_CONFIG = {
    'update_interval': 3600,  # 更新间隔(秒) - 1小时
    'max_articles_per_source': 50,  # 每个来源最大文章数
    'ai_keywords': [
        'artificial intelligence', 'AI', 'machine learning', 'deep learning',
        'neural network', 'GPT', 'ChatGPT', 'OpenAI', 'Google AI', 'DeepMind',
        'computer vision', 'natural language processing', 'NLP', 'robotics',
        'automation', 'algorithm', 'data science', 'big data', 'LLM',
        '人工智能', '机器学习', '深度学习', '神经网络', '算法', '自动化'
    ]
}

# RSS订阅源
RSS_FEEDS = [
    'https://feeds.feedburner.com/oreilly/radar',
    'https://machinelearningmastery.com/feed/',
    'https://towardsdatascience.com/feed',
    'https://www.artificialintelligence-news.com/feed/',
    'https://venturebeat.com/ai/feed/'
]