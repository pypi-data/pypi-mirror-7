import os
from lxml import etree
from plumber import (
    Behavior,
    plumber,
    plumb,
    default,
    finalize,
)
from node.behaviors import (
    Nodify,
    DictStorage,
)
from pyramid.security import (
    Allow,
    authenticated_userid,
)
from pyramid.threadlocal import get_current_request
from cone.app import security


class LocalManagerConfig(DictStorage):
    """Local Management configuration storage.
    """

    @finalize
    def load(self):
        path = self.file_path
        if not path or not os.path.exists(path):
            return
        with open(path, 'r') as handle:
            tree = etree.parse(handle)
        root = tree.getroot()
        for rule in root.getchildren():
            new_rule = self.storage[rule.tag] = dict()
            for prop in rule.getchildren():
                for tag_name in ['target', 'default']:
                    if prop.tag == tag_name:
                        new_rule[tag_name] = list()
                        for group in prop.getchildren():
                            new_rule[tag_name].append(group.text)

    @finalize
    def __call__(self):
        root = etree.Element('localmanager')
        for gid, rule in self.storage.items():
            group = etree.SubElement(root, gid)
            for tag_name in ['target', 'default']:
                elem = etree.SubElement(group, tag_name)
                for gid in rule[tag_name]:
                    item = etree.SubElement(elem, 'item')
                    item.text = gid
        with open(self.file_path, 'w') as handle:
            handle.write(etree.tostring(root, pretty_print=True))


class LocalManagerConfigAttributes(object):
    __metaclass__ = plumber
    __plumbing__ = (
        Nodify,
        LocalManagerConfig,
    )

    def __init__(self, path):
        self.file_path = path
        self.load()


class LocalManager(Behavior):
    """Behavior providing local manager information for authenticated user.
    """

    @finalize
    @property
    def local_management_enabled(self):
        """Flag whether local management is enabled.
        """
        general_settings = self.root['settings']['ugm_general']
        return general_settings.attrs.users_local_management_enabled == 'True'

    @finalize
    @property
    def local_manager_consider_for_user(self):
        """Flag whether local manager ACL should be considered for current
        authenticated user.
        """
        if not self.local_management_enabled:
            return False
        request = get_current_request()
        if authenticated_userid(request) == security.ADMIN_USER:
            return False
        roles = security.authenticated_user(request).roles
        if 'admin' in roles or 'manager' in roles:
            return False
        return True

    @finalize
    @property
    def local_manager_gid(self):
        """Group id of local manager group of current authenticated member.

        Currently a user can be assigned only to one local manager group. If
        mode than one local manager group is configured, an error is raised.
        """
        config = self.root['settings']['ugm_localmanager'].attrs
        user = security.authenticated_user(get_current_request())
        if not user:
            return None
        gids = user.group_ids
        adm_gids = list()
        for gid in gids:
            rule = config.get(gid)
            if rule:
                adm_gids.append(gid)
        if len(adm_gids) == 0:
            return None
        if len(adm_gids) > 1:
            msg = (u"Authenticated member defined in local manager "
                   u"groups %s but only one management group allowed for "
                   u"each user. Please contact System Administrator in "
                   u"order to fix this problem.")
            exc = msg % ', '.join(["'%s'" % gid for gid in adm_gids])
            raise Exception(exc)
        return adm_gids[0]

    @finalize
    @property
    def local_manager_rule(self):
        """Return rule for local manager.
        """
        adm_gid = self.local_manager_gid
        if not adm_gid:
            return None
        config = self.root['settings']['ugm_localmanager'].attrs
        return config[adm_gid]

    @finalize
    @property
    def local_manager_default_gids(self):
        """Return default group id's for local manager.
        """
        rule = self.local_manager_rule
        if not rule:
            return list()
        return rule['default']

    @finalize
    @property
    def local_manager_target_gids(self):
        """Target group id's for local manager.
        """
        rule = self.local_manager_rule
        if not rule:
            return list()
        return rule['target']

    @finalize
    @property
    def local_manager_target_uids(self):
        """Target uid's for local manager.
        """
        groups = self.root['groups'].backend
        managed_uids = set()
        for gid in self.local_manager_target_gids:
            group = groups.get(gid)
            if group:
                managed_uids.update(group.member_ids)
        return list(managed_uids)

    @finalize
    def local_manager_is_default(self, adm_gid, gid):
        """Check whether gid is default group for local manager group.
        """
        config = self.root['settings']['ugm_localmanager'].attrs
        rule = config[adm_gid]
        if not gid in rule['target']:
            raise Exception(u"group '%s' not managed by '%s'" % (gid, adm_gid))
        return gid in rule['default']


class LocalManagerACL(LocalManager):
    """Behavior providing ACL's by local manager configuration.
    """

    @default
    @property
    def local_manager_acl(self):
        raise NotImplementedError(u"Abstract ``LocalManagerACL`` does not "
                                  u"implement ``local_manager_acl``")

    @plumb
    @property
    def __acl__(_next, self):
        acl = _next(self)
        if not self.local_manager_consider_for_user:
            return acl
        return self.local_manager_acl + acl


class LocalManagerUsersACL(LocalManagerACL):

    @finalize
    @property
    def local_manager_acl(self):
        if not self.local_manager_target_gids:
            return []
        permissions = ['view', 'add', 'add_user', 'edit', 'edit_user',
                       'manage_expiration', 'manage_membership']
        return [(Allow,
                 authenticated_userid(get_current_request()),
                 permissions)]


class LocalManagerUserACL(LocalManagerACL):

    @finalize
    @property
    def local_manager_acl(self):
        # if self.name is None, User object was created by add model factory
        if self.name is not None:
            if not self.name in self.local_manager_target_uids:
                return []
        permissions = ['view', 'add', 'add_user', 'edit', 'edit_user',
                       'manage_expiration', 'manage_membership']
        return [(Allow,
                 authenticated_userid(get_current_request()),
                 permissions)]


class LocalManagerGroupsACL(LocalManagerACL):

    @finalize
    @property
    def local_manager_acl(self):
        if not self.local_manager_target_gids:
            return []
        permissions = ['view', 'manage_membership']
        return [(Allow,
                 authenticated_userid(get_current_request()),
                 permissions)]


class LocalManagerGroupACL(LocalManagerACL):

    @finalize
    @property
    def local_manager_acl(self):
        if not self.name in self.local_manager_target_gids:
            return []
        permissions = ['view', 'manage_membership']
        return [(Allow,
                 authenticated_userid(get_current_request()),
                 permissions)]
