# Copyright (C) 2007-2009 Etienne Robillard <robillard.etienne@gmail.com>
# All rights reserved.
#
# Please see the "LICENSE" and "NOTICE" files included in the source 
# distribution for details on licensing info.
"""Schema for the BlogEngine app version 5.0.

TODO:
* BlogEntry -- Can be published/hidden.
* BlogEntryImage -- A image that belongs to a attached BlogEntry.

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
* Slug -- A slug. 
* Category -- A category. (optional)
* Feed -- A RSSFeed20 (TODO)

"""

from schevo.schema import *
schevo.schema.prep(locals())

class SchevoIcon(E.Entity):

    _hidden = True

    name = f.string()
    data = f.image()

    _key(name)

class Category(E.Entity):
    
    name = f.string()
    _key(name)

class Comment(E.Entity):
    pass

class Slug(E.Entity):
    pass

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
    description = f.string(required=False)

    _key(name)

class BlogEntry(E.Entity):

    title = f.string()
    pub_date = f.date()
    author = f.entity('Author')
    category = f.entity('Category', required=False)
    short_description = f.string(required=False)
    body = f.string(multiline=True)
    published = f.boolean(False)

    _key(title, category)

    #def x_actors(self):
    #    return [casting.actor
    #            for casting in self.m.movie_castings()]

    def __unicode__(self):
        return u'%s (%i)' % (self.title, self.pub_date.year)

#E.BlogEntry._sample = [
#    ('This is a test using notmm-schevo', '2009-05-04', 
#    ('Etienne Robillard', ), 'Just a test', 'Long description here'),
#    ('2nd post!', '2009-05-04',
#    ('Etienne Robillard', ), '2nd test with notmm-schevo', 'so far so good :)')]

