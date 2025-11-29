#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import sys
import os
import json
import re
from datetime import datetime

# 添加UTF-8编码处理
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

class SMZDMCrawler:
    def __init__(self):
        self.base_url = "https://www.smzdm.com/fenlei/wangluocunchu/post/#feed-main"
        self.articles = []
    
    async def fetch_articles(self):
        """使用Crawl4AI获取页面内容，然后用正则表达式解析文章"""
        try:
            print("开始爬取什么值得买内容...")
            
            # 配置浏览器
            browser_config = BrowserConfig(
                headless=True,
                verbose=True,
                java_script_enabled=True
            )
            
            # 配置爬取参数
            crawl_config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                page_timeout=30000
            )
            
            # 使用Crawl4AI进行爬取
            async with AsyncWebCrawler(config=browser_config) as crawler:
                result = await crawler.arun(
                    url=self.base_url,
                    config=crawl_config
                )
                
                if result.success:
                    print(f"成功爬取页面，内容长度: {len(result.cleaned_html)}")
                    
                    # 使用正则表达式提取文章
                    html_content = result.cleaned_html
                    
                    # 查找所有文章链接和标题
                    link_pattern = r'<a[^>]+href="(https://post\.smzdm\.com/[^"]+)"[^>]*>([^<]+)</a>'
                    matches = re.findall(link_pattern, html_content)
                    
                    # 去重并构建文章列表
                    seen_urls = set()
                    for url, title in matches:
                        if url not in seen_urls and len(title.strip()) > 5:
                            seen_urls.add(url)
                            self.articles.append({
                                'title': title.strip(),
                                'url': url,
                                'description': title.strip(),  # 暂时用标题作为描述
                                'pub_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'author': '什么值得买',
                                'price': '',
                                'image': ''
                            })
                    
                    # 只取前15条
                    self.articles = self.articles[:15]
                    
                    print(f"总共提取到 {len(self.articles)} 篇文章")
                    for i, article in enumerate(self.articles, 1):
                        print(f"{i}. {article['title']}")
                    
                    return True
                else:
                    print(f"爬取失败: {result.error_message}")
                    return False
                    
        except Exception as e:
            print(f"爬取过程中出错: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_html(self):
        """生成静态HTML页面"""
        template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>什么值得买 - 最新文章</title>
    <meta name="generator" content="SMZDM Crawler (Crawl4AI)">
    <meta name="updated" content="{update_time}">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #ff6700; padding-bottom: 10px; }}
        .update-time {{ color: #666; font-size: 14px; margin-bottom: 20px; }}
        .articles {{ display: grid; gap: 20px; }}
        .article {{ border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; background: #fafafa; transition: box-shadow 0.3s; }}
        .article:hover {{ box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
        .article-title {{ font-size: 18px; font-weight: bold; margin: 0 0 10px 0; }}
        .article-title a {{ color: #333; text-decoration: none; }}
        .article-title a:hover {{ color: #ff6700; }}
        .article-meta {{ font-size: 12px; color: #666; margin-bottom: 10px; }}
        .article-desc {{ color: #555; margin-bottom: 10px; }}
        .article-price {{ color: #ff6700; font-weight: bold; font-size: 16px; }}
        .article-image {{ max-width: 100px; height: auto; border-radius: 4px; float: right; margin-left: 10px; }}
        .no-articles {{ text-align: center; color: #666; padding: 40px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>什么值得买 - 最新文章</h1>
        <div class="update-time">更新时间: {update_time}</div>
        <div class="articles">
            {articles}
        </div>
    </div>
</body>
</html>"""
        
        if not self.articles:
            articles_html = '<div class="no-articles">暂无文章数据，请检查爬虫配置或稍后重试。</div>'
        else:
            articles_html = ""
            for article in self.articles:
                # 安全获取字段值
                title = article.get('title', '未知标题')
                url = article.get('url', '#')
                description = article.get('description', title)
                pub_date = article.get('pub_date', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                author = article.get('author', '什么值得买')
                price = article.get('price', '')
                image = article.get('image', '')
                
                # 处理图片
                image_html = f'<img class="article-image" src="{image}" alt="{title}" onerror="this.style.display=\'none\'">' if image else ''
                
                # 处理价格
                price_html = f'<div class="article-price">{price}</div>' if price and price.strip() else ''
                
                articles_html += f"""
                <article class="article" data-title="{title}" data-url="{url}" data-date="{pub_date}" data-author="{author}">
                    {image_html}
                    <h2 class="article-title">
                        <a href="{url}" target="_blank">{title}</a>
                    </h2>
                    <div class="article-meta">
                        发布时间: {pub_date} | 作者: {author}
                    </div>
                    <div class="article-desc">{description}</div>
                    {price_html}
                </article>"""
        
        html_content = template.format(
            update_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            articles=articles_html
        )
        
        return html_content
    
    def save_html(self, filename="index.html"):
        """保存HTML文件"""
        try:
            html_content = self.generate_html()
            
            # 确保目录存在
            os.makedirs('docs', exist_ok=True)
            
            filepath = os.path.join('docs', filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"HTML页面已保存到: {filepath}")
            return True
            
        except Exception as e:
            print(f"保存HTML文件时出错: {e}")
            return False
    
    def save_json(self, filename="articles.json"):
        """保存JSON数据供调试使用"""
        try:
            os.makedirs('docs', exist_ok=True)
            filepath = os.path.join('docs', filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.articles, f, ensure_ascii=False, indent=2)
            
            print(f"JSON数据已保存到: {filepath}")
            return True
            
        except Exception as e:
            print(f"保存JSON文件时出错: {e}")
            return False

async def main():
    """主函数"""
    crawler = SMZDMCrawler()
    
    # 爬取文章
    if await crawler.fetch_articles():
        # 生成HTML
        if crawler.save_html():
            # 保存JSON（可选）
            crawler.save_json()
            print("爬取任务完成！")
            return 0
        else:
            print("生成HTML失败！")
            return 1
    else:
        print("爬取文章失败！")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
