# Copyright (C) 2007-2009 Etienne Robillard <robillard.etienne@gmail.com>
# All rights reserved.
#
# Please see the "LICENSE" and "NOTICE" files included in the source 
# distribution for details on licensing info.
"""Schema for the BlogEngine app version 5.0.

TODO:
* BlogEntry -- Can be published/hidden.
* BlogEntryImage -- A image that belongs to a attached BlogEntry.
* BlogEntry

queries:
* LatestBlogsByDate -- A Feed subclass
* LatestBlogsByAuthor -- etc...
* LatestBlogsByCategory 

General stuff:
* Author -- The author of the BlogEntry.

* Comment -- A comment. 

* ContentType -- Basic content types. (optional)
* Tag -- A tag.

* TaggedItem -- TODO! 
* Status -- A status.
* Slug -- A slug. 
* Category -- A category. (optional)
* Feed -- A RSSFeed20 (TODO)

"""

from schevo.schema import *
schevo.schema.prep(locals())

from notmm.utils.decorators import permalink

class SchevoIcon(E.Entity):

    _hidden = True

    name = f.string()
    data = f.image()

    _key(name)

class Category(E.Entity):
    name = f.string()
    description = f.string(required=False)

    _key(name)
    _plural = "Categories"

class Comment(E.Entity):
    author = f.entity('Author')
    #TODO support more flexible content/object types...
    blogentry = f.entity('BlogEntry')
    message = f.string(multiline=True)
    published = f.boolean(default=True)
    pub_date = f.datetime()

    _key(author, blogentry)

class Author(E.Entity):
    
    name = f.string()
    # TODO: add a emailstring() method to support e-mail bytestrings in utf8
    email = f.string(required=False)
    homepage = f.string(required=False)
    twitter_username = f.string(required=False)

    _key(name)

    #def x_blogentries(self):
    #    return [casting.movie
    #            for casting in self.m.movie_castings()]

class Tag(E.Entity):

    name = f.string()
    blogentry = f.entity('BlogEntry')
    #description = f.string(required=False)

    _key(name, blogentry)

class BlogEntry(E.Entity):

    title = f.string()
    pub_date = f.datetime()
    author = f.entity('Author')
    category = f.entity('Category', required=False)
    short_description = f.string(required=False)
    body = f.string(multiline=True)
    published = f.boolean(False)
    slug = f.string(required=False)

    _key(title)
    _plural = "Blog Entries"

    def x_comments(self):
        return [(comment.author, 
        comment.message) for comment in self.m.comments()]

    def x_tags(self):
        return [tag for tag in self.m.tags()]

    def __unicode__(self):
        return u'%s: %s' % (self.author, self.title)

    #### public methods

    @permalink
    def get_absolute_url(self):
        # returns the canonical URL representation for this post
        #s = "%s/%s/" % (self.category, self.slug)
        #return unicode(s)
        return ('blogengine.views.details', (), dict(
            category=self.category.name, 
            slug=self.slug))

E.Comment._sample = [
    (('Etienne Robillard',), ('Pepe is not a pony!',), 
      'this is a test comment!', True, '2009-05-17 12:54'),
]

#E.Tag._sample = [
#    ('notmm', ('Pepe is not a pony!',)),
#] 

#E.BlogEntry._sample = [
#    ('This is a test using notmm-schevo', '2009-05-04', 
#    ('Etienne Robillard', ), 'Just a test', 'Long description here'),
#    ('2nd post!', '2009-05-04',
#    ('Etienne Robillard', ), '2nd test with notmm-schevo', 'so far so good :)')]

