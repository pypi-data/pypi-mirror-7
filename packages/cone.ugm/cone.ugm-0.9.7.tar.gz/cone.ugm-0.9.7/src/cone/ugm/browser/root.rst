cone.ugm.browser.root
=====================

::

    >>> from cone.app import root
    >>> from cone.tile import render_tile
    
    >>> request = layer.new_request()

Unauthenticated content tile renders login form::

    >>> expected = \
    ...     '<form action="http://example.com/login"'
    >>> res = render_tile(root, request, 'content')
    >>> res.find(expected) > -1
    True

Other tiles raise if unauthenticated::
    
    >>> render_tile(root, request, 'leftcolumn')
    Traceback (most recent call last):
      ...
    HTTPForbidden: Unauthorized: tile 
    <cone.ugm.browser.root.RootLeftColumn object at ...> 
    failed permission check
    
    >>> render_tile(root, request, 'rightcolumn')
    Traceback (most recent call last):
      ...
    HTTPForbidden: Unauthorized: tile 
    <cone.ugm.browser.root.RootRightColumn object at ...> 
    failed permission check

Authenticate and render tiles::

    >>> layer.login('editor')
    
    >>> res = render_tile(root, request, 'leftcolumn')
    >>> res.find('<div class="column left_column box">') > -1
    True
    
    >>> res = render_tile(root, request, 'rightcolumn')
    >>> res == u'<div class="column right_column">&nbsp;</div>'
    True

Site name tile::

    >>> render_tile(root, request, 'site')
    'SITENAME'
    
    >>> layer.logout()
