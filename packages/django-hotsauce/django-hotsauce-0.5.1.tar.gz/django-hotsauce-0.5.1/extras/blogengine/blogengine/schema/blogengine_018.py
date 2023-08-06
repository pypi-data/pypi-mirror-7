# Copyright (C) 2007-2009 Etienne Robillard <robillard.etienne@gmail.com>
# All rights reserved.
#
# Please see the "LICENSE" and "NOTICE" files included in the source 
# distribution for details on licensing info.

from schevo.schema import *
from schevo.constant import UNASSIGNED
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

    def __str__(self):
        return "%s" % self.name

    def __repr__(self):
        return self.__str__()

    #def as_slug(self):
    #    if self.slug:
    #        slug = self.slug
    #    else:
    #        slug = self.name.replace(' ', '-').lower()
    #    return str(slug)

    def x_category_items(self):
        return [x for x in self.m.category_items()]
   
    def x_blogentries(self):
        from operator import attrgetter
        items = sorted([item for item in self.m.blogentries() if \
            item.reviewed is True and type(item) != UNASSIGNED], \
            key=attrgetter('pub_date'), reverse=True)
        return items
 
    def get_items_count(self):
        rv = []
        for item in self.x.blogentries():
            rv.append(item)
        return len(rv)

class CategoryItem(E.Entity):
    name = f.string()
    category = f.entity('Category')
    description = f.string(required=False)
    slug = f.string(required=False)
    _plural = "Category items"

    def __str__(self):
        return 'CategoryItem: %s' % self.name
    
    #def x_blogentries(self):
    #    from operator import attrgetter
    #    items = sorted([item for item in self.m.blogentries() if \
    #        item.published is True and type(item) != UNASSIGNED], \
    #        key=attrgetter('pub_date'), reverse=True)
    #    return items

class Comment(E.Entity):
    
    #sender_name = f.entity('Author')
    sender_name = f.string()
    sender_message = f.string(multiline=True)
    sender_email = f.string()
    sender_website = f.string(required=False, allow_empty=True)
    
    #TODO support more flexible content/object types...
    blogentry = f.entity('BlogEntry')

    reviewed = f.boolean(required=False, default=True)
    pub_date = f.datetime()

    #_key(sender_name, blogentry)
    #_key(blogentry)

    def x_is_published(self):
        return bool(self.reviewed == True)

    ### Public methods
    def convert_to_html(self, name='sender_message'):
        # convert a field value to markdown
        try:
            # Can only convert strings, not UNASSIGNED or None fields.. 
            from notmm.utils.markup import convert_to_markdown
            html = convert_to_markdown(getattr(self, name))
        except (AttributeError, MarkdownError), e:
            raise e
        else:
            return html

##XXX: Uses tm.accounts.model.UserManager
class Author(E.Entity):
    #user = f.entity
    username = f.string()
    # TODO: add a emailstring() method to support e-mail bytestrings in utf8
    email = f.string(required=False)

    homepage_url = f.string(required=False)
    blog_url = f.string(required=False)
    
    #twitter_username = f.string(required=False)

    _key(username, email)

    #def x_blogentries(self):
    #    return [casting.movie
    #            for casting in self.m.movie_castings()]
    
    def __str__(self):
        return self.username

class Tag(E.Entity):

    name = f.string()
    blogentry = f.entity('BlogEntry')
    #description = f.string(required=False)

    _key(name, blogentry)

#class Article
class BlogEntry(E.Entity):

    title = f.string()
    pub_date = f.datetime()
    author = f.entity('Author')
    
    category = f.entity('Category')
    #categoryitem = f.entity('CategoryItem', required=False)
    short_description = f.string(multiline=False, required=False, default='')
    
    # TODO: add markdown or textile support here
    body = f.string(multiline=True, required=False)
    
    # /path/to/article.md
    source = f.path(required=False)
    
    #Need a f.multiplechoices field type!
    #source_type = f.string(
    #    preferred_values=('rest', 'html', 'text'),
    #    required=False)
    
    reviewed = f.boolean(required=False, default=False)
    slug = f.string(required=True)

    _key(title)
    _plural = "BlogEntries"

    #def x_category_items(self):
    #    return [item for item in self.m.categoryitems()]

    def x_comments(self):
        return [comment for comment in self.m.comments()]

    def x_tags(self):
        return [tag for tag in self.m.tags()]

    def __str__(self):
        return '%s: %s' % (self.author, self.title)

    #### public methods

    @permalink
    def get_absolute_url(self):
        # returns the canonical URL representation for this post
        assert type(self.category) != UNASSIGNED
        category_slug = self.category.slug
        return ('blogengine.contrib.blog.views.details_for_blogentry', (), dict(
            category=category_slug, 
            slug=self.slug))
    
    def convert_to_html(self, name='body'):
        """ convert to html with markdown """
        # XXX: support other wiki-like converters
        try:
            # Can only convert strings, not _UNASSIGNED or None fields.. 
            from notmm.utils.markup import convert_to_markdown
            if getattr(self, name) is not UNASSIGNED:
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

