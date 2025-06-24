import sqlite3
import json
from datetime import datetime
from config import DATABASE_PATH

class NewsDatabase:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建新闻表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                content TEXT,
                url TEXT UNIQUE NOT NULL,
                source TEXT NOT NULL,
                author TEXT,
                published_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                category TEXT DEFAULT 'AI',
                keywords TEXT,
                image_url TEXT,
                is_read BOOLEAN DEFAULT 0,
                relevance_score REAL DEFAULT 0.0
            )
        ''')
        
        # 创建关键词表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT UNIQUE NOT NULL,
                count INTEGER DEFAULT 1,
                last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建来源表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                url TEXT,
                type TEXT,
                is_active BOOLEAN DEFAULT 1,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_article(self, article_data):
        """添加新闻文章"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO news 
                (title, description, content, url, source, author, published_at, 
                 keywords, image_url, relevance_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                article_data.get('title'),
                article_data.get('description'),
                article_data.get('content'),
                article_data.get('url'),
                article_data.get('source'),
                article_data.get('author'),
                article_data.get('published_at'),
                json.dumps(article_data.get('keywords', [])),
                article_data.get('image_url'),
                article_data.get('relevance_score', 0.0)
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # 文章已存在
            return False
        except Exception as e:
            print(f"添加文章时出错: {e}")
            return False
        finally:
            conn.close()
    
    def get_articles(self, limit=50, offset=0, source=None, keyword=None, order_by='published_at DESC'):
        """获取新闻文章"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM news WHERE 1=1"
        params = []
        
        if source:
            query += " AND source = ?"
            params.append(source)
        
        if keyword:
            query += " AND (title LIKE ? OR description LIKE ? OR keywords LIKE ?)"
            keyword_pattern = f"%{keyword}%"
            params.extend([keyword_pattern, keyword_pattern, keyword_pattern])
        
        query += f" ORDER BY {order_by} LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        articles = cursor.fetchall()
        
        # 转换为字典格式
        columns = [description[0] for description in cursor.description]
        result = []
        for article in articles:
            article_dict = dict(zip(columns, article))
            # 解析keywords JSON
            if article_dict['keywords']:
                try:
                    article_dict['keywords'] = json.loads(article_dict['keywords'])
                except:
                    article_dict['keywords'] = []
            result.append(article_dict)
        
        conn.close()
        return result
    
    def get_article_count(self, source=None, keyword=None):
        """获取文章总数"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT COUNT(*) FROM news WHERE 1=1"
        params = []
        
        if source:
            query += " AND source = ?"
            params.append(source)
        
        if keyword:
            query += " AND (title LIKE ? OR description LIKE ? OR keywords LIKE ?)"
            keyword_pattern = f"%{keyword}%"
            params.extend([keyword_pattern, keyword_pattern, keyword_pattern])
        
        cursor.execute(query, params)
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def mark_as_read(self, article_id):
        """标记文章为已读"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE news SET is_read = 1 WHERE id = ?", (article_id,))
        conn.commit()
        conn.close()
    
    def get_sources(self):
        """获取所有新闻源"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT source FROM news ORDER BY source")
        sources = [row[0] for row in cursor.fetchall()]
        conn.close()
        return sources
    
    def get_trending_keywords(self, limit=20):
        """获取热门关键词"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 从最近的文章中提取关键词
        cursor.execute('''
            SELECT keywords FROM news 
            WHERE created_at >= datetime('now', '-7 days')
            AND keywords IS NOT NULL
        ''')
        
        keyword_count = {}
        for row in cursor.fetchall():
            try:
                keywords = json.loads(row[0])
                for keyword in keywords:
                    keyword_count[keyword] = keyword_count.get(keyword, 0) + 1
            except:
                continue
        
        # 按频率排序
        trending = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)[:limit]
        conn.close()
        return trending
    
    def cleanup_old_articles(self, days=30):
        """清理旧文章"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM news 
            WHERE created_at < datetime('now', '-{} days')
        '''.format(days))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted_count