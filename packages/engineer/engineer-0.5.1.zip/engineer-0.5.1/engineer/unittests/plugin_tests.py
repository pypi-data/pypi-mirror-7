# coding=utf-8

from path import path

from engineer.unittests.config_tests import BaseTestCase

__author__ = 'Tyler Butler <tyler@tylerbutler.com>'


class PostRenamerTestCase(BaseTestCase):
    def test_settings(self):
        from engineer.conf import settings

        settings.reload('config.yaml')
        self.assertTrue(hasattr(settings, 'POST_RENAME_ENABLED'))
        self.assertTrue(hasattr(settings, 'POST_RENAME_CONFIG'))
        self.assertTrue(settings.POST_RENAME_ENABLED)

    def test_disabled(self):
        from engineer.conf import settings

        settings.reload('renamer_off.yaml')
        self.assertFalse(settings.POST_RENAME_ENABLED)

    def test_post_renamer_default_config(self):
        from engineer.conf import settings
        from engineer.models import Post

        settings.reload('config.yaml')

        post = Post('posts/draft_post.md')
        self.assertEqual(post.source.name, '(draft) a-draft-post.md')
        self.assertTrue(post.source.exists())
        self.assertFalse(path('posts/draft_post.md').exists())

        post = Post('posts/review_post.md')
        self.assertEqual(post.source.name, '(review) 2012-11-02 a-post-in-review.md')
        self.assertTrue(post.source.exists())
        self.assertFalse(path('posts/review_post.md').exists())

        post = Post('posts/published_post_with_timestamp.md')
        self.assertEqual(post.source.name, '(p) 2012-11-02 a-published-post.md')
        self.assertTrue(post.source.exists())
        self.assertFalse(path('posts/published_post_with_timestamp.md').exists())

    def test_post_renamer_custom_config(self):
        from engineer.conf import settings
        from engineer.models import Post

        settings.reload('custom_renames.yaml')

        post = Post('posts/draft_post.md')
        self.assertEqual(post.source.name, 'draft_post.md')
        self.assertTrue(post.source.exists())

        post = Post('posts/review_post.md')
        self.assertEqual(post.source.name, '2012-11-02-a-post-in-review.md')
        self.assertTrue(post.source.exists())
        self.assertFalse(path('posts/review_post.md').exists())

        post = Post('posts/published_post_with_timestamp.md')
        self.assertEqual(post.source.name, '(p) 2012-11-02 a-published-post.md')
        self.assertTrue(post.source.exists())
        self.assertFalse(path('posts/published_post_with_timestamp.md').exists())


class LazyMarkdownLinksTestCase(BaseTestCase):
    _expected_metadata = """title: Lazy Markdown Links
status: draft
slug: lazy-markdown-links

---

"""

    _expected_output = """This is my text and [this is my link][4]. I'll define
the url for that link under the paragraph.

[4]: http://brettterpstra.com

I can use [multiple][5] lazy links in [a paragraph][6],
and then just define them in order below it.

[5]: https://gist.github.com/ttscoff/7059952
[6]: http://blog.bignerdranch.com/4044-rock-heads/

I can also use lazy links when there are already [existing
numbered links][1] in [the text][3].

[1]: http://www.tylerbutler.com
[3]: http://www.xkcd2.com
"""

    _expected_output2 = """[Lazy links][1] can come in handy. But sometimes you have links
already defined and you also want to add [some lazy ones][3].

[1]: http://www.tylerbutler.com/
[3]: http://www.xkcd2.com/

Luckily the [Engineer][2] Lazy Markdown Link plugin [handles this
case][4] automatically.

[4]: http://www.tylerbutler.com/
[2]: https://github.com/tylerbutler/engineer/
"""

    def test_lazy_links(self):
        from engineer.conf import settings
        from engineer.models import Post

        settings.reload('config.yaml')

        post = Post('posts/lazy_markdown_links.md')
        self.assertEqual(post.content_preprocessed.strip(), self._expected_output.strip())

        post = Post('posts/lazy_markdown_links2.md')
        self.assertEqual(post.content_preprocessed.strip(), self._expected_output2.strip())

    def test_lazy_links_persist(self):
        from engineer.conf import settings
        from engineer.models import Post

        settings.reload('lazy_links_persist.yaml')

        post = Post('posts/lazy_markdown_links.md')
        self.assertEqual(post.content_preprocessed.strip(), self._expected_output.strip())

        with open(post.source, mode='rb') as post_file:
            content = post_file.read()
        self.assertEqual(content.strip(), self._expected_metadata + self._expected_output.strip())
