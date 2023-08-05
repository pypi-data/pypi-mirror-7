cone.ugm.browser.user
=====================

::

    >>> from cone.app import root
    >>> from cone.tile import render_tile
    
    >>> users = root['users']
    >>> user = users['uid2']
    
    >>> request = layer.new_request()

Unauthenticated content tile renders login form::

    >>> expected = \
    ...     '<form action="http://example.com/users/uid2/login"'
    >>> res = render_tile(user, request, 'content')
    >>> res.find(expected) > -1
    True

Other tiles raise if unauthenticated::
    
    >>> render_tile(user, request, 'leftcolumn')
    Traceback (most recent call last):
      ...
    HTTPForbidden: Unauthorized: 
    tile <cone.ugm.browser.user.UserLeftColumn object at ...> 
    failed permission check
    
    >>> render_tile(user, request, 'rightcolumn')
    Traceback (most recent call last):
      ...
    HTTPForbidden: Unauthorized: 
    tile <cone.ugm.browser.user.UserRightColumn object at ...> 
    failed permission check
    
    >>> render_tile(user, request, 'columnlisting')
    Traceback (most recent call last):
      ...
    HTTPForbidden: Unauthorized: 
    tile <cone.ugm.browser.user.GroupsOfUserColumnListing object at ...> 
    failed permission check
    
    >>> render_tile(user, request, 'allcolumnlisting')
    Traceback (most recent call last):
      ...
    HTTPForbidden: Unauthorized: 
    tile <cone.ugm.browser.user.AllGroupsColumnListing object at ...> 
    failed permission check

Authenticate and render tiles::

    >>> layer.login('manager')
    
    >>> res = render_tile(user, request, 'leftcolumn')
    >>> res.find('<div class="column left_column box">') > -1
    True
    
    >>> res = render_tile(user, request, 'rightcolumn')
    >>> res.find('<div class="column right_column">') > -1
    True
    
    >>> res = render_tile(user, request, 'columnlisting')
    >>> expected = \
    ...     '<li ajax:target="http://example.com/groups/group2"'
    >>> res.find(expected) > -1
    True
    
    >>> res = render_tile(user, request, 'allcolumnlisting')
    >>> expected = \
    ...     '<li ajax:target="http://example.com/groups/group1"'
    >>> res.find(expected) > -1
    True
    
    >>> layer.logout()

Add::
    
    >>> layer.login('viewer')
    
    >>> request = layer.new_request()
    >>> request.params['factory'] = 'user'
    
    >>> res = render_tile(users, request, 'add')
    Traceback (most recent call last):
      ...
    HTTPForbidden: Unauthorized: tile 
    <cone.app.browser.authoring.AddTile object at ...> 
    failed permission check
    
    >>> layer.login('manager')
    >>> res = render_tile(users, request, 'add')
    >>> expected = '<form action="http://example.com/users/add"'
    >>> res.find(expected) > -1
    True
    
    >>> request.params['userform.id'] = ''
    >>> request.params['userform.cn'] = 'cn99'
    >>> request.params['userform.sn'] = 'sn99'
    >>> request.params['userform.mail'] = 'uid99@example.com'
    >>> request.params['userform.userPassword'] = 'secret99'
    >>> request.params['userform.principal_roles'] = []
    >>> request.params['action.userform.save'] = '1'
    
    >>> res = render_tile(users, request, 'add')
    >>> res.find('class="errormessage">No Id defined') > -1
    True
    
    >>> request.params['userform.id'] = 'uid99'
    
    >>> res = render_tile(users, request, 'add')
    >>> res
    u''
    
    >>> request.environ['redirect']
    <HTTPFound at ... 302 Found>
    
    >>> users.keys()
    [u'uid0', u'uid1', u'uid2', u'uid3', u'uid4', u'uid5', u'uid6', u'uid7', 
    u'uid8', u'uid9', u'viewer', u'editor', u'admin', u'manager', u'max', 
    u'sepp', u'localmanager_1', u'localmanager_2', u'uid99']
    
    >>> user = users['uid99']
    >>> sorted(user.attrs.items())
    [('cn', u'cn99'), 
    ('mail', u'uid99@example.com'), 
    ('rdn', u'uid99'), 
    ('sn', u'sn99')]

Edit::

    >>> request = layer.new_request()
    >>> res = render_tile(user, request, 'edit')
    >>> expected = '<form action="http://example.com/users/uid99/edit"'
    >>> res.find(expected) > -1
    True
    
    >>> request.params['userform.cn'] = 'cn99'
    >>> request.params['userform.sn'] = 'sn changed'
    >>> request.params['userform.mail'] = 'changed@example.com'
    >>> request.params['userform.userPassword'] = '_NOCHANGE_'
    >>> request.params['userform.principal_roles'] = []
    >>> request.params['action.userform.save'] = '1'
    >>> res = render_tile(user, request, 'edit')
    >>> res
    u''
    
    >>> sorted(user.attrs.items())
    [('cn', u'cn99'), 
    ('mail', u'changed@example.com'), 
    ('rdn', u'uid99'), 
    ('sn', u'sn changed')]
    
    >>> user.attrs['login']
    u'cn99'
    
    >>> layer.logout()
