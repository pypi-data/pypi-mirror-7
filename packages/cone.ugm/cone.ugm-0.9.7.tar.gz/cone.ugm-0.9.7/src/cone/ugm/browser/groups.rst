cone.ugm.browser.groups
=======================

::

    >>> from cone.app import root
    >>> from cone.tile import render_tile
    
    >>> groups = root['groups']
    
    >>> request = layer.new_request()

Unauthenticated content tile renders login form::

    >>> expected = \
    ...     '<form action="http://example.com/groups/login"'
    >>> res = render_tile(groups, request, 'content')
    >>> res.find(expected) > -1
    True

Other tiles raise if unauthenticated::
    
    >>> render_tile(groups, request, 'leftcolumn')
    Traceback (most recent call last):
      ...
    HTTPForbidden: Unauthorized: 
    tile <cone.ugm.browser.groups.GroupsLeftColumn object at ...> 
    failed permission check
    
    >>> render_tile(groups, request, 'rightcolumn')
    Traceback (most recent call last):
      ...
    HTTPForbidden: Unauthorized: 
    tile <cone.ugm.browser.groups.GroupsRightColumn object at ...> 
    failed permission check
    
    >>> render_tile(groups, request, 'columnlisting')
    Traceback (most recent call last):
      ...
    HTTPForbidden: Unauthorized: 
    tile <cone.ugm.browser.groups.GroupsColumnListing object at ...> 
    failed permission check

Authenticate and render tiles::

    >>> layer.login('manager')
    
    >>> res = render_tile(groups, request, 'leftcolumn')
    >>> res.find('<div class="column left_column box">') > -1
    True
    
    >>> res = render_tile(groups, request, 'rightcolumn')
    >>> res == u'<div class="column right_column">&nbsp;</div>'
    True
    
    >>> res = render_tile(groups, request, 'columnlisting')
    >>> res.find('<div class="columnlisting leftbatchsensitiv"') > -1
    True
    
    >>> layer.logout()
