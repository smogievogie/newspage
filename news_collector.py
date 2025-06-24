import requests
import feedparser
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import time
import logging
from config import NEWSAPI_KEY, NEWS_CONFIG, RSS_FEEDS
from database import NewsDatabase

class NewsCollector:
    def __init__(self):
        self.db = NewsDatabase()
        self.ai_keywords = NEWS_CONFIG['ai_keywords']
        self.max_articles = NEWS_CONFIG['max_articles_per_source']
        
        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def is_ai_related(self, text):
        """检查文本是否与AI相关"""
        if not text:
            return False
        
        text_lower = text.lower()
        for keyword in self.ai_keywords:
            if keyword.lower() in text_lower:
                return True
        return False
    
    def calculate_relevance_score(self, title, description, content=""):
        """计算文章的AI相关性分数"""
        score = 0
        text = f"{title} {description} {content}".lower()
        
        # 核心AI关键词权重更高
        high_value_keywords = ['artificial intelligence', 'machine learning', 'deep learning', 'neural network', 'gpt', 'chatgpt']
        medium_value_keywords = ['ai', 'algorithm', 'automation', 'robotics', 'nlp']
        
        for keyword in high_value_keywords:
            score += text.count(keyword.lower()) * 3
        
        for keyword in medium_value_keywords:
            score += text.count(keyword.lower()) * 2
        
        for keyword in self.ai_keywords:
            if keyword.lower() not in high_value_keywords + medium_value_keywords:
                score += text.count(keyword.lower()) * 1
        
        return min(score, 10)  # 最大分数为10
    
    def extract_keywords(self, title, description):
        """从标题和描述中提取关键词"""
        text = f"{title} {description}".lower()
        found_keywords = []
        
        for keyword in self.ai_keywords:
            if keyword.lower() in text:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def collect_from_newsapi(self):
        """从NewsAPI收集新闻"""
        if not NEWSAPI_KEY or NEWSAPI_KEY == "demo_key":
            self.logger.warning("NewsAPI密钥未配置，跳过NewsAPI收集")
            return []
        
        articles = []
        
        # AI相关查询词
        queries = [
            'artificial intelligence',
            'machine learning',
            'deep learning',
            'ChatGPT OR GPT',
            'OpenAI',
            'neural network'
        ]
        
        for query in queries:
            try:
                url = f"https://newsapi.org/v2/everything"
                params = {
                    'q': query,
                    'language': 'en',
                    'sortBy': 'publishedAt',
                    'pageSize': 20,
                    'apiKey': NEWSAPI_KEY,
                    'from': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                }
                
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if data['status'] == 'ok':
                    for article in data['articles']:
                        if self.is_ai_related(f"{article.get('title', '')} {article.get('description', '')}"):
                            processed_article = {
                                'title': article.get('title', ''),
                                'description': article.get('description', ''),
                                'content': article.get('content', ''),
                                'url': article.get('url', ''),
                                'source': f"NewsAPI - {article.get('source', {}).get('name', 'Unknown')}",
                                'author': article.get('author', ''),
                                'published_at': article.get('publishedAt', ''),
                                'image_url': article.get('urlToImage', ''),
                                'keywords': self.extract_keywords(article.get('title', ''), article.get('description', '')),
                                'relevance_score': self.calculate_relevance_score(
                                    article.get('title', ''),
                                    article.get('description', ''),
                                    article.get('content', '')
                                )
                            }
                            articles.append(processed_article)
                
                time.sleep(1)  # 避免API限制
                
            except Exception as e:
                self.logger.error(f"NewsAPI收集出错 (查询: {query}): {e}")
        
        return articles
    
    def collect_from_rss(self):
        """从RSS源收集新闻"""
        articles = []
        
        for feed_url in RSS_FEEDS:
            try:
                self.logger.info(f"正在收集RSS: {feed_url}")
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:self.max_articles]:
                    title = entry.get('title', '')
                    description = entry.get('summary', '') or entry.get('description', '')
                    
                    if self.is_ai_related(f"{title} {description}"):
                        # 解析发布时间
                        published_at = ''
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            published_at = datetime(*entry.published_parsed[:6]).isoformat()
                        elif hasattr(entry, 'published'):
                            published_at = entry.published
                        
                        processed_article = {
                            'title': title,
                            'description': description,
                            'content': entry.get('content', [{}])[0].get('value', '') if entry.get('content') else '',
                            'url': entry.get('link', ''),
                            'source': f"RSS - {feed.feed.get('title', feed_url)}",
                            'author': entry.get('author', ''),
                            'published_at': published_at,
                            'image_url': '',
                            'keywords': self.extract_keywords(title, description),
                            'relevance_score': self.calculate_relevance_score(title, description)
                        }
                        articles.append(processed_article)
                
                time.sleep(2)  # 避免过于频繁的请求
                
            except Exception as e:
                self.logger.error(f"RSS收集出错 ({feed_url}): {e}")
        
        return articles
    
    def collect_from_reddit(self):
        """从Reddit收集AI相关讨论"""
        articles = []
        
        try:
            # Reddit的AI相关subreddit
            subreddits = ['MachineLearning', 'artificial', 'deeplearning', 'ChatGPT', 'OpenAI']
            
            for subreddit in subreddits:
                url = f"https://www.reddit.com/r/{subreddit}/hot.json"
                headers = {'User-Agent': 'AI News Collector 1.0'}
                
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                for post in data['data']['children'][:10]:  # 限制每个subreddit 10篇
                    post_data = post['data']
                    title = post_data.get('title', '')
                    description = post_data.get('selftext', '')[:500]  # 限制长度
                    
                    if self.is_ai_related(f"{title} {description}"):
                        processed_article = {
                            'title': title,
                            'description': description,
                            'content': post_data.get('selftext', ''),
                            'url': f"https://reddit.com{post_data.get('permalink', '')}",
                            'source': f"Reddit - r/{subreddit}",
                            'author': post_data.get('author', ''),
                            'published_at': datetime.fromtimestamp(post_data.get('created_utc', 0)).isoformat(),
                            'image_url': post_data.get('thumbnail', '') if post_data.get('thumbnail', '').startswith('http') else '',
                            'keywords': self.extract_keywords(title, description),
                            'relevance_score': self.calculate_relevance_score(title, description)
                        }
                        articles.append(processed_article)
                
                time.sleep(2)  # Reddit API限制
                
        except Exception as e:
            self.logger.error(f"Reddit收集出错: {e}")
        
        return articles
    
    def collect_all_news(self):
        """收集所有来源的新闻"""
        self.logger.info("开始收集AI新闻...")
        
        all_articles = []
        
        # 从各个来源收集
        all_articles.extend(self.collect_from_newsapi())
        all_articles.extend(self.collect_from_rss())
        all_articles.extend(self.collect_from_reddit())
        
        # 去重并保存到数据库
        saved_count = 0
        for article in all_articles:
            if self.db.add_article(article):
                saved_count += 1
        
        self.logger.info(f"收集完成: 总共{len(all_articles)}篇文章，新增{saved_count}篇")
        return saved_count
    
    def get_latest_news(self, limit=20):
        """获取最新新闻"""
        return self.db.get_articles(limit=limit, order_by='published_at DESC')
    
    def search_news(self, keyword, limit=20):
        """搜索新闻"""
        return self.db.get_articles(limit=limit, keyword=keyword, order_by='relevance_score DESC, published_at DESC')