import unittest
from monitor import canonical_url, parse_articles, build_message

HTML = '''<div class="news_list"><ul>
<li><a href="/2026/1023/c68657a587358/page.htm">第六周课外研学讲座预告</a><span>2026-10-23</span></li>
<li><a href="/2026/1016/c68657a586327/page.htm" title="第五周课外研学讲座预告">第五周课外研学讲座预告</a><span>2026-10-16</span></li>
</ul></div>'''

class SiteParserTests(unittest.TestCase):
    def test_parse_article_list(self):
        posts = parse_articles(HTML, 'https://jwc.seu.edu.cn/kwyxjz/list.htm')
        self.assertEqual(len(posts), 2)
        self.assertEqual(posts[0]['title'], '第六周课外研学讲座预告')
        self.assertEqual(posts[0]['date'], '2026-10-23')

    def test_normalize_template_links(self):
        self.assertEqual(
            canonical_url('https://jwc.seu.edu.cn/_t3454/2026/1023/c68657a587358/page.psp'),
            'https://jwc.seu.edu.cn/2026/1023/c68657a587358/page.htm',
        )

    def test_message_contains_clickable_url(self):
        post = parse_articles(HTML, 'https://jwc.seu.edu.cn/kwyxjz/list.htm')[0]
        message = build_message([('课外研学讲座', '新增', post)])
        self.assertIn(post['url'], message)
        self.assertIn('新增', message)

if __name__ == '__main__':
    unittest.main()
