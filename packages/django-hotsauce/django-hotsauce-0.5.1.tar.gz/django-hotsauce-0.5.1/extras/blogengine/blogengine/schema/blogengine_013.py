# Copyright (C) 2007-2009 Etienne Robillard <robillard.etienne@gmail.com>
# All rights reserved.
#
# Please see the "LICENSE" and "NOTICE" files included in the source 
# distribution for details on licensing info.
"""Schema for the BlogEngine app version 7.

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
* Rating -- A rating. (TODO)
* Pingback -- ???

* ContentType -- Basic content types. (optional)
* Tag -- A tag.

* TaggedItem -- TODO! 
* Status -- A status.
* Slug -- A slug. 
* Category -- A category. (optional)
* CategoryItem -- A subcategory item 
* Feed -- A RSSFeed20 (TODO)

"""

from schevo.schema import *
schevo.schema.prep(locals())

from notmm.utils.decorators import permalink
from markdown2 import markdown, MarkdownError

class SchevoIcon(E.Entity):

    _hidden = True

    name = f.string()
    data = f.image()

    _key(name)

#class Event(E.Entity):
#    title = f.string()
#    _plural = "Events"

class Category(E.Entity):
    name = f.string()
    description = f.string(required=False)
    slug = f.string(required=False)

    _key(name)
    _plural = "Categories"

    def x_as_slug(self):
        if self.slug:
            slug = self.slug
        else:
            slug = self.name.replace(' ', '-').lower()
        return unicode(slug)

class CategoryItem(E.Entity):
    name = f.string()
    category = f.entity('Category')
    description = f.string(required=False)
    slug = f.string(required=False)
    
    def __unicode__(self):
        return u'CategoryItem: %s' % self.name

class Comment(E.Entity):
    
    #sender_name = f.entity('Author')
    sender_name = f.string()
    sender_message = f.string(multiline=True)
    sender_email = f.string()
    sender_website = f.string(required=False)
    
    #TODO support more flexible content/object types...
    blogentry = f.entity('BlogEntry')

    published = f.boolean(required=False, default=False)
    pub_date = f.datetime()

    #_key(sender_name, blogentry)
    #_key(blogentry)

    def x_is_published(self):
        return (self.published == True)

    ### Public methods

    def convert_to_html(self, name='sender_message'):
        
        try:
            # Can only convert strings, not _UNASSIGNED or None fields.. 
            from notmm.utils.html import convert_to_markdown
            html = convert_to_markdown(getattr(self, name))
        except AttributeError, e:
            raise e
        else:
            return html

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
    
    #category = f.entity('Category')
    categoryitem = f.entity('CategoryItem', required=False)
    
    short_description = f.string(multiline=False, required=False, default='')
    
    # TODO: add markdown or textile support here
    body = f.string(multiline=True)
    
    # /path/to/filename.rst 
    source = f.path(required=False)
    
    #Need a f.multiplechoices field type!
    #source_type = f.string(
    #    preferred_values=('rest', 'html', 'text'),
    #    required=False)
    
    published = f.boolean(required=False, default=False)
    slug = f.string(required=False)

    _key(title)
    _plural = "Blog Entries"

    #def x_category_items(self):
    #    return [item for item in self.m.categoryitems()]

    def x_comments(self):
        return [comment for comment in self.m.comments()]

    def x_tags(self):
        return [tag for tag in self.m.tags()]

    def __unicode__(self):
        return u'%s: %s' % (self.author, self.title)

    #### public methods

    @permalink
    def get_absolute_url(self):
        # returns the canonical URL representation for this post
        
        category_slug = self.categoryitem.category.x.as_slug()
        return ('blogengine.views.details_for_blogentry', (), dict(
            category=category_slug, 
            slug=self.slug))
    
    def convert_to_html(self, name='body'):
        """ convert to html with markdown """
        # XXX: support other wiki-like converters
        try:
            # Can only convert strings, not _UNASSIGNED or None fields.. 
            from notmm.utils.html import convert_to_markdown
            html = convert_to_markdown(getattr(self, name))
        except AttributeError, e:
            raise e
        else:
            return html

#E.Comment._sample = [
#    (('Etienne Robillard',), ('Pepe is not a pony!',), 
#      'this is a test comment!', True, '2009-05-17 12:54'),
#]
#E.Tag._sample = [
#    ('notmm', ('Pepe is not a pony!',)),
#] 
#E.BlogEntry._sample = [
#    ('This is a test using notmm-schevo', '2009-05-04', 
#    ('Etienne Robillard', ), 'Just a test', 'Long description here'),
#    ('2nd post!', '2009-05-04',
#    ('Etienne Robillard', ), '2nd test with notmm-schevo', 'so far so good :)')]

