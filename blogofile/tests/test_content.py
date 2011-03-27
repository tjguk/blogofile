import unittest
import tempfile
import shutil
import os
from blogofile import main


class TestContent(unittest.TestCase):

    def setUp(self):
        #Remember the current directory to preserve state
        self.previous_dir = os.getcwd()
        #Create a staging directory that we can build in
        self.build_path = tempfile.mkdtemp()
        #Change to that directory just like a user would
        os.chdir(self.build_path)
        #Reinitialize the configuration
        main.config.init()

    def tearDown(self):
        #Revert the config overridden options
        main.config.override_options = {}
        #go back to the directory we used to be in
        os.chdir(self.previous_dir)
        #Clean up the build directory
        shutil.rmtree(self.build_path)

    def testAutoPermalink(self):
        """Test to make sure post without permalink gets a good autogenerated one"""
        main.main("init blog_unit_test")

        #Write a post to the _posts dir:
        src = """---
title: This is a test post
date: 2009/08/16 00:00:00
---
This is a test post
"""
        f = open(os.path.join(self.build_path,"_posts","01. Test post.html"),"w")
        f.write(src)
        f.close()
        main.config.override_options = {
            "site.url":"http://www.yoursite.com",
            "blog.path":"/blog",
            "blog.auto_permalink.enabled": True,
            "blog.auto_permalink.path": "/blog/:year/:month/:day/:title" }
        main.main("build")
        rendered = open(os.path.join(self.build_path,"_site","blog","2009","08",
                                     "16","this-is-a-test-post","index.html"
                                     )).read()

    def testHardCodedPermalinkUpperCase(self):
        """Permalink's set by the user should appear exactly as the user enters"""
        main.main("init blog_unit_test")
        #Write a post to the _posts dir:
        permalink = "http://www.yoursite.com/bLog/2009/08/16/This-Is-A-TeSt-Post"
        src = """---
title: This is a test post
permalink: %(permalink)s
date: 2009/08/16 00:00:00
---
This is a test post
""" % {'permalink':permalink}
        f = open(os.path.join(self.build_path,"_posts","01. Test post.html"),"w")
        f.write(src)
        f.close()
        main.config.override_options = {
            "site.url":"http://www.yoursite.com",
            "blog.path":"/blog",
            "blog.auto_permalink.enabled": True,
            "blog.auto_permalink.path": "/blog/:year/:month/:day/:title" }
        main.main("build")
        rendered = open(os.path.join(self.build_path,"_site","bLog","2009","08",
                                     "16","This-Is-A-TeSt-Post","index.html"
                                     )).read()

    def testUpperCaseAutoPermalink(self):
        """Auto generated permalinks should have title and filenames lower case
        (but not the rest of the URL)"""
        main.main("init blog_unit_test")
        #Write a post to the _posts dir:
        src = """---
title: This is a test post
date: 2009/08/16 00:00:00
---
This is a test post without a permalink
"""
        f = open(os.path.join(self.build_path,"_posts","01. Test post.html"),"w")
        f.write(src)
        f.close()
        main.config.override_options = {
            "site.url":"http://www.BlogoFile.com",
            "blog.path":"/Blog",
            "blog.auto_permalink.enabled": True,
            "blog.auto_permalink.path": "/Blog/:year/:month/:day/:title" }
        main.main("build")
        rendered = open(os.path.join(self.build_path,"_site","Blog","2009","08",
                                     "16","this-is-a-test-post","index.html"
                                     )).read()
    
    def testPathOnlyPermalink(self):
        """Test to make sure path only permalinks are generated correctly"""
        main.main("init blog_unit_test")
        #Write a post to the _posts dir:
        permalink = "/blog/2009/08/16/this-is-a-test-post"
        src = """---
title: This is a test post
permalink: %(permalink)s
date: 2009/08/16 00:00:00
---
This is a test post
""" %{'permalink':permalink}
        f = open(os.path.join(self.build_path,"_posts","01. Test post.html"),"w")
        f.write(src)
        f.close()
        main.config.override_options = {
            "site.url":"http://www.yoursite.com",
            "blog.path":"/blog",
            "blog.auto_permalink.enabled": True,
            "blog.auto_permalink.path": "/blog/:year/:month/:day/:title" }
        main.main("build")
        rendered = open(os.path.join(self.build_path,"_site","blog","2009","08",
                                     "16","this-is-a-test-post","index.html"
                                     )).read()

#TODO: Replace BeautifulSoup with lxml or use Selenium:
#     def testFeedLinksAreURLs(self):
#         """Make sure feed links are full URLs and not just paths"""
#         main.main("init blog_unit_test")
#         #Write a post to the _posts dir:
#         permalink = "/blog/2009/08/16/test-post"
#         src = """---
# title: This is a test post
# permalink: %(permalink)s
# date: 2009/08/16 00:00:00
# ---
# This is a test post
# """ %{'permalink':permalink}
#         f = open(os.path.join(self.build_path,"_posts","01. Test post.html"),"w")
#         f.write(src)
#         f.close()
#         main.config.override_options = {
#             "site.url":"http://www.yoursite.com",
#             "blog.path":"/blog",
#             "blog.auto_permalink.enabled": True,
#             "blog.auto_permalink.path": "/blog/:year/:month/:day/:title" }
#         main.main("build")
#         feed = open(os.path.join(self.build_path,"_site","blog","feed",
#                                  "index.xml")).read()
#         soup = BeautifulSoup.BeautifulStoneSoup(feed)
#         for link in soup.findAll("link"):
#             assert(link.contents[0].startswith("http://"))


#TODO: Replace BeautifulSoup with lxml or use Selenium:        
#     def testCategoryLinksInPosts(self):
#         """Make sure category links in posts are correct"""
#         main.main("init blog_unit_test")
#         main.config.override_options = {
#             "site.url":"http://www.yoursite.com",
#             "blog.path":"/blog"
#             }
#         #Write a blog post with categories:
#         src = """---
# title: This is a test post
# categories: Category 1, Category 2
# date: 2009/08/16 00:00:00
# ---
# This is a test post
# """
#         f = open(os.path.join(self.build_path,"_posts","01. Test post.html"),"w")
#         f.write(src)
#         f.close()
#         main.main("build")
#         #Open up one of the permapages:
#         page = open(os.path.join(self.build_path,"_site","blog","2009",
#                                  "08","16","this-is-a-test-post","index.html")).read()
#         soup = BeautifulSoup.BeautifulStoneSoup(page)
#         print(soup.findAll("a"))
#         assert soup.find("a",attrs={'href':'/blog/category/category-1'})
#         assert soup.find("a",attrs={'href':'/blog/category/category-2'})

    def testReStructuredFilter(self):
        """Test to make sure reStructuredTest work well"""

        main.main("init blog_unit_test")
        #Write a post to the _posts dir:
        src = """---
title: This is a test post
date: 2010/03/27 00:00:00
---

This is a reStructured post
===========================

Plain text :

::

    $ echo "hello"
    hello

"""
        f = open(os.path.join(self.build_path,"_posts","01. Test post.rst"),"w")
        f.write(src)
        f.close()
        main.config.override_options = {
            "site.url":"http://www.yoursite.com",
            "blog.path":"/blog",
            "blog.auto_permalink.enabled": True,
            "blog.auto_permalink.path": "/blog/:year/:month/:day/:title" }
        main.main("build")
        rendered = open(os.path.join(self.build_path,"_site","blog","2010","03",
                                     "27","this-is-a-test-post","index.html"
                                     )).read()
        assert """<h1 class="title">This is a reStructured post</h1>
<p>Plain text :</p>
<pre class="literal-block">
$ echo &quot;hello&quot;
hello
</pre>""" in rendered


    def testUnpublishedPost(self):
        """A post marked 'draft: True' should never show up in
        archives, categories, chronological listings, or feeds. It
        should generate a single permapage and that's all."""
        main.main("init blog_unit_test")
        main.main("build")
        #Make sure the permapage was written
        rendered = open(os.path.join(
                self.build_path,"_site","blog","2099","08",
                "01","this-post-is-unpublished","index.html"
                )).read()
        #Make sure the archive was not written
        assert not os.path.exists(os.path.join(
                self.build_path,"_site","blog","archive",
                "2099"))
        #Make sure the category was not written
        assert not os.path.exists(os.path.join(
                self.build_path,"_site","blog","category",
                "drafts"))
