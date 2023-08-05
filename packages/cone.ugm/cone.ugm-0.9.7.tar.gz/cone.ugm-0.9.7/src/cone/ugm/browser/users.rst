cone.ugm.browser.users
======================

::

    >>> from cone.app import root
    >>> from cone.tile import render_tile
    
    >>> users = root['users']
    
    >>> request = layer.new_request()

Unauthenticated content tile renders login form::

    >>> expected = \
    ...     '<form action="http://example.com/users/login"'
    >>> res = render_tile(users, request, 'content')
    >>> res.find(expected) > -1
    True

Other tiles raise if unauthenticated::
    
    >>> render_tile(users, request, 'leftcolumn')
    Traceback (most recent call last):
      ...
    HTTPForbidden: Unauthorized: 
    tile <cone.ugm.browser.users.UsersLeftColumn object at ...> 
    failed permission check
    
    >>> render_tile(users, request, 'rightcolumn')
    Traceback (most recent call last):
      ...
    HTTPForbidden: Unauthorized: 
    tile <cone.ugm.browser.users.UsersRightColumn object at ...> 
    failed permission check
    
    >>> render_tile(users, request, 'columnlisting')
    Traceback (most recent call last):
      ...
    HTTPForbidden: Unauthorized: 
    tile <cone.ugm.browser.users.UsersColumnListing object at ...> 
    failed permission check

Authenticate and render tiles::

    >>> layer.login('manager')
    
    >>> res = render_tile(users, request, 'leftcolumn')
    >>> res.find('<div class="column left_column box">') > -1
    True
    
    >>> res = render_tile(users, request, 'rightcolumn')
    >>> res == u'<div class="column right_column">&nbsp;</div>'
    True
    
    >>> res = render_tile(users, request, 'columnlisting')
    >>> res.find('<div class="columnlisting leftbatchsensitiv"') > -1
    True
    
    >>> layer.logout()
