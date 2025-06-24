from flask import Flask, render_template, jsonify, request, redirect, url_for
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import atexit
import logging
from config import APP_CONFIG, NEWS_CONFIG
from news_collector import NewsCollector
from database import NewsDatabase

app = Flask(__name__)
app.config.update(APP_CONFIG)

# 初始化组件
news_collector = NewsCollector()
db = NewsDatabase()

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 定时任务调度器
scheduler = BackgroundScheduler()
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

# 定时收集新闻
def scheduled_news_collection():
    """定时新闻收集任务"""
    try:
        logger.info("开始定时新闻收集...")
        count = news_collector.collect_all_news()
        logger.info(f"定时收集完成，新增 {count} 篇文章")
    except Exception as e:
        logger.error(f"定时收集出错: {e}")

# 添加定时任务
scheduler.add_job(
    func=scheduled_news_collection,
    trigger="interval",
    seconds=NEWS_CONFIG['update_interval'],
    id='news_collection_job',
    name='定时收集AI新闻',
    replace_existing=True
)

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/news')
def api_news():
    """获取新闻API"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    source = request.args.get('source', None)
    keyword = request.args.get('keyword', None)
    order_by = request.args.get('order_by', 'published_at DESC')
    
    offset = (page - 1) * limit
    
    articles = db.get_articles(
        limit=limit,
        offset=offset,
        source=source,
        keyword=keyword,
        order_by=order_by
    )
    
    total_count = db.get_article_count(source=source, keyword=keyword)
    
    return jsonify({
        'articles': articles,
        'total': total_count,
        'page': page,
        'limit': limit,
        'total_pages': (total_count + limit - 1) // limit
    })

@app.route('/api/sources')
def api_sources():
    """获取新闻源列表"""
    sources = db.get_sources()
    return jsonify({'sources': sources})

@app.route('/api/trending')
def api_trending():
    """获取热门关键词"""
    trending = db.get_trending_keywords(limit=20)
    return jsonify({'trending': trending})

@app.route('/api/collect', methods=['POST'])
def api_collect():
    """手动触发新闻收集"""
    try:
        count = news_collector.collect_all_news()
        return jsonify({
            'success': True,
            'message': f'收集完成，新增 {count} 篇文章',
            'count': count
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'收集失败: {str(e)}'
        }), 500

@app.route('/api/article/<int:article_id>/read', methods=['POST'])
def api_mark_read(article_id):
    """标记文章为已读"""
    try:
        db.mark_as_read(article_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/search')
def api_search():
    """搜索新闻"""
    keyword = request.args.get('q', '')
    limit = request.args.get('limit', 20, type=int)
    
    if not keyword:
        return jsonify({'articles': [], 'total': 0})
    
    articles = news_collector.search_news(keyword, limit=limit)
    return jsonify({
        'articles': articles,
        'total': len(articles),
        'keyword': keyword
    })

@app.route('/api/stats')
def api_stats():
    """获取统计信息"""
    total_articles = db.get_article_count()
    sources = db.get_sources()
    trending = db.get_trending_keywords(limit=10)
    
    # 获取今日新增文章数
    today_articles = db.get_article_count()
    
    return jsonify({
        'total_articles': total_articles,
        'total_sources': len(sources),
        'trending_keywords': len(trending),
        'last_updated': datetime.now().isoformat()
    })

@app.route('/dashboard')
def dashboard():
    """仪表板页面"""
    return render_template('dashboard.html')

@app.route('/settings')
def settings():
    """设置页面"""
    return render_template('settings.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # 启动时收集一次新闻
    try:
        logger.info("应用启动，开始初始新闻收集...")
        initial_count = news_collector.collect_all_news()
        logger.info(f"初始收集完成，获得 {initial_count} 篇文章")
    except Exception as e:
        logger.error(f"初始收集失败: {e}")
    
    # 启动Flask应用
    app.run(
        host=APP_CONFIG['HOST'],
        port=APP_CONFIG['PORT'],
        debug=APP_CONFIG['DEBUG']
    )