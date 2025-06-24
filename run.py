#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI新闻收集器启动脚本

这个脚本用于启动AI新闻收集器应用，包括：
1. 检查依赖
2. 初始化数据库
3. 启动Flask应用
4. 启动后台新闻收集任务
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 7):
        print("错误: 需要Python 3.7或更高版本")
        print(f"当前版本: {sys.version}")
        sys.exit(1)
    print(f"✓ Python版本检查通过: {sys.version.split()[0]}")

def check_dependencies():
    """检查依赖包"""
    print("检查依赖包...")
    
    required_packages = [
        'flask',
        'requests',
        'beautifulsoup4',
        'feedparser',
        'praw',
        'apscheduler',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} (缺失)")
    
    if missing_packages:
        print(f"\n缺失 {len(missing_packages)} 个依赖包")
        install = input("是否自动安装缺失的依赖包? (y/n): ")
        if install.lower() in ['y', 'yes', '是']:
            install_dependencies(missing_packages)
        else:
            print("请手动安装依赖包:")
            print(f"pip install {' '.join(missing_packages)}")
            sys.exit(1)
    else:
        print("✓ 所有依赖包已安装")

def install_dependencies(packages):
    """安装依赖包"""
    print(f"\n正在安装依赖包: {', '.join(packages)}")
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install'
        ] + packages)
        print("✓ 依赖包安装完成")
    except subprocess.CalledProcessError as e:
        print(f"✗ 依赖包安装失败: {e}")
        print("请手动安装依赖包:")
        print(f"pip install {' '.join(packages)}")
        sys.exit(1)

def check_config():
    """检查配置文件"""
    print("\n检查配置文件...")
    
    config_file = Path('config.py')
    if not config_file.exists():
        print("✗ config.py 不存在")
        
        example_file = Path('config.example.py')
        if example_file.exists():
            print("发现 config.example.py，正在复制为 config.py")
            import shutil
            shutil.copy('config.example.py', 'config.py')
            print("✓ 配置文件已创建")
            print("\n⚠️  请编辑 config.py 文件，配置您的API密钥")
        else:
            print("✗ 配置文件模板也不存在")
            sys.exit(1)
    else:
        print("✓ 配置文件存在")
    
    # 检查配置内容
    try:
        import config
        
        warnings = []
        
        if not config.NEWSAPI_KEY or config.NEWSAPI_KEY == 'your_newsapi_key_here':
            warnings.append("NewsAPI密钥未配置")
        
        if not config.REDDIT_CLIENT_ID or config.REDDIT_CLIENT_ID == 'your_reddit_client_id':
            warnings.append("Reddit API未配置")
        
        if warnings:
            print("\n⚠️  配置警告:")
            for warning in warnings:
                print(f"   - {warning}")
            print("\n应用仍可运行，但某些功能可能受限")
        else:
            print("✓ 配置检查通过")
            
    except Exception as e:
        print(f"✗ 配置文件有错误: {e}")
        sys.exit(1)

def init_database():
    """初始化数据库"""
    print("\n初始化数据库...")
    try:
        from database import NewsDatabase
        db = NewsDatabase()
        db.init_db()
        print("✓ 数据库初始化完成")
    except Exception as e:
        print(f"✗ 数据库初始化失败: {e}")
        sys.exit(1)

def start_app():
    """启动应用"""
    print("\n启动AI新闻收集器...")
    print("="*50)
    print("🤖 AI新闻收集器")
    print("📰 自动收集最新AI相关新闻")
    print("🌐 Web界面: http://localhost:5000")
    print("="*50)
    
    try:
        from app import app
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n\n👋 应用已停止")
    except Exception as e:
        print(f"\n✗ 应用启动失败: {e}")
        sys.exit(1)

def main():
    """主函数"""
    print("🤖 AI新闻收集器启动检查")
    print("="*40)
    
    # 检查Python版本
    check_python_version()
    
    # 检查依赖
    check_dependencies()
    
    # 检查配置
    check_config()
    
    # 初始化数据库
    init_database()
    
    # 启动应用
    start_app()

if __name__ == '__main__':
    main()