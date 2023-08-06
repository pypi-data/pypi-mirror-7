# Copyright (C) 2007-2009 Etienne Robillard <robillard.etienne@gmail.com>
# All rights reserved.
#
# Please see the "LICENSE" and "NOTICE" files included in the source 
# distribution for details on licensing info.
"""Schema for the BlogEngine app.

TODO:
* BlogEntry -- Can be published/hidden.
* BlogEntryImage -- A image that belongs to a attached BlogEntry.

General stuff:
* Author -- The author of the BlogEntry.
* Comment -- A comment. 
* Tag -- A tag.

"""

from schevo.schema import *
schevo.schema.prep(locals())

class Author(E.Entity):
    
    name = f.string()
    # TODO: add a emailstring() method to support e-mail bytestrings in utf8
    #email = f.string()

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
    
    short_description = f.string(required=False)
    body = f.string(multiline=True)

    _key(title)

    #def x_actors(self):
    #    return [casting.actor
    #            for casting in self.m.movie_castings()]

    def __unicode__(self):
        return u'%s (%i)' % (self.title, self.pub_date.year)

#class MovieCasting(E.Entity):
#
#    movie = f.entity('Movie', CASCADE)
#    actor = f.entity('Actor')
#
#    _key(movie, actor)


E.Author._sample = [
    ('Etienne Robillard', ),
    ('Winona Ryder', ),
    ]

E.Tag._sample = [
    #('schevo',),
    ('python',),
    ('botryococcus braunii',),
    ]

E.BlogEntry._sample = [
    (('This is a test using notmm-schevo', '2009-05-04', 
      'Etienne Robillard', 'Just a test', 'Long description here'),
     ('2nd post!', '2009-05-04',
      'Etienne Robillard', '2nd test with notmm-schevo', 'so far so good :)'))]

#E.MovieCasting._sample = [
#    (('A Scanner Darkly', ), ('Keanu Reeves', )),
#    (('A Scanner Darkly', ), ('Winona Ryder', )),
#    (("Bill & Ted's Excellent Adventure", ), ('Keanu Reeves', )),
#    (('Edward Scissorhands', ), ('Winona Ryder', )),
#    ]
