from plumber import plumber
from pyramid.security import has_permission
from pyramid.i18n import TranslationStringFactory
from yafowil.base import ExtractionError
from yafowil.utils import UNSET
from cone.tile import (
    tile,
    Tile,
)
from cone.app.browser.utils import (
    make_url,
    make_query,
)
from cone.app.browser.form import Form
from cone.app.browser.authoring import (
    AddBehavior,
    EditBehavior,
)
from cone.app.browser.ajax import AjaxAction
from ..model.group import Group
from ..model.utils import (
    ugm_general,
    ugm_groups,
)
from . import form_field_definitions
from .columns import Column
from .listing import ColumnListing
from .roles import PrincipalRolesForm
from .authoring import (
    AddFormFiddle,
    EditFormFiddle,
)
from .principal import PrincipalForm
from webob.exc import HTTPFound

_ = TranslationStringFactory('cone.ugm')


@tile('leftcolumn', interface=Group, permission='view')
class GroupLeftColumn(Column):

    add_label = _('add_group', 'Add Group')

    @property
    def can_add(self):
        return has_permission('add_group', self.model.parent, self.request)

    def render(self):
        setattr(self.request, '_curr_listing_id', self.model.name)
        return self._render(self.model.parent, 'leftcolumn')


@tile('rightcolumn', 'templates/right_column.pt',
      interface=Group, permission='view')
class GroupRightColumn(Tile):

    @property
    def default_widget(self):
        settings = ugm_general(self.model)
        return settings.attrs['default_membership_assignment_widget']


class Principals(object):
    """Descriptor to return principal items for listing
    """
    def __init__(self,
                 members_only=False,
                 available_only=False):
        self.members_only = members_only
        self.available_only = available_only

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self

        appgroup = obj.model
        group = appgroup.model
        member_ids = group.keys()

        # always True if we list members only, otherwise will be set
        # in the loop below
        related = self.members_only

        available_only = self.available_only

        if related and available_only:
            raise Exception(u"Invalid object settings.")

        # XXX: so far only users as members of groups, for
        # group-in-group we need to prefix groups
        if related:
            users = group.users
        else:
            # XXX: LDAP query here.
            users = group.root.users.values()
            if available_only:
                users = [u for u in users if not u.name in member_ids]

        # reduce for local manager
        if obj.model.local_manager_consider_for_user:
            local_uids = obj.model.local_manager_target_uids
            users = [u for u in users if u.name in local_uids]

        attrlist = obj.user_attrs
        sort_attr = obj.user_default_sort_column

        ret = list()

        can_change = has_permission(
            'manage_membership', obj.model.parent, obj.request)

        for user in users:
            uid = user.name
            attrs = user.attrs

            item_target = make_url(obj.request, path=user.path[1:])
            action_query = make_query(id=uid)
            action_target = make_url(obj.request,
                                     node=appgroup,
                                     query=action_query)

            if not self.members_only:
                related = uid in member_ids

            actions = list()
            if can_change:
                action_id = 'add_item'
                action_enabled = not bool(related)
                action_title = _('add_user_to_selected_group',
                                 'Add user to selected group')
                add_item_action = obj.create_action(
                    action_id, action_enabled, action_title, action_target)
                actions.append(add_item_action)

                action_id = 'remove_item'
                action_enabled = bool(related)
                action_title = _('remove_user_from_selected_group',
                                 'Remove user from selected group')
                remove_item_action = obj.create_action(
                    action_id, action_enabled, action_title, action_target)
                actions.append(remove_item_action)

            vals = [obj.extract_raw(attrs, attr) for attr in attrlist]
            sort = obj.extract_raw(attrs, sort_attr)
            content = obj.item_content(*vals)
            current = False
            item = obj.create_item(sort, item_target, content,
                                   current, actions)
            ret.append(item)
        return ret


@tile('columnlisting', 'templates/column_listing.pt',
      interface=Group, permission='view')
class UsersOfGroupColumnListing(ColumnListing):
    css = 'users'
    slot = 'rightlisting'
    list_columns = ColumnListing.user_list_columns
    # XXX: Why items and not keys() / __iter__?
    # used to be a readonly property
    query_items = Principals(members_only=True)
    batchname = 'rightbatch'


@tile('allcolumnlisting', 'templates/column_listing.pt',
      interface=Group, permission='view')
class AllUsersColumnListing(ColumnListing):
    css = 'users'
    slot = 'rightlisting'
    list_columns = ColumnListing.user_list_columns
    # XXX: Why items and not keys() / __iter__?
    # used to be a readonly property
    query_items = Principals()
    batchname = 'rightbatch'

    @property
    def ajax_action(self):
        return 'allcolumnlisting'


@tile('inoutlisting', 'templates/in_out.pt',
      interface=Group, permission='view')
class InOutListing(ColumnListing):
    selected_items = Principals(members_only=True)
    available_items = Principals(available_only=True)

    @property
    def user_attrs(self):
        settings = ugm_general(self.model)
        return [settings.attrs['user_display_name_attr']]

    @property
    def user_default_sort_column(self):
        settings = ugm_general(self.model)
        return settings.attrs['user_display_name_attr']

    @property
    def display_control_buttons(self):
        return True
        #settings = ugm_general(self.model)
        #return settings.attrs['controls_membership_assignment_widget']


class GroupForm(PrincipalForm):
    form_name = 'groupform'

    @property
    def form_attrmap(self):
        settings = ugm_groups(self.model)
        return settings.attrs.groups_form_attrmap

    @property
    def form_field_definitions(self):
        return form_field_definitions.group

    def exists(self, widget, data):
        group_id = data.extracted
        if group_id is UNSET:
            return data.extracted
        if group_id in self.model.parent.backend:
            message = _('group_already_exists',
                        default="Group ${gid} already exists.",
                        mapping={'gid': group_id})
            raise ExtractionError(message)
        return data.extracted


@tile('addform', interface=Group, permission="add_group")
class GroupAddForm(GroupForm, Form):
    __metaclass__ = plumber
    __plumbing__ = AddBehavior, PrincipalRolesForm, AddFormFiddle

    show_heading = False
    show_contextmenu = False

    def save(self, widget, data):
        settings = ugm_groups(self.model)
        attrmap = settings.attrs.groups_form_attrmap
        extracted = dict()
        for key, val in attrmap.items():
            val = data.fetch('groupform.%s' % key).extracted
            if not val:
                continue
            extracted[key] = val
        groups = self.model.parent.backend
        gid = extracted.pop('id')
        #group = groups.create(gid, **extracted)
        groups.create(gid, **extracted)
        self.request.environ['next_resource'] = gid
        groups()
        self.model.parent.invalidate()
        # XXX: access already added user after invalidation.
        #      if not done, there's some kind of race condition with ajax
        #      continuation. figure out why.
        self.model.parent[gid]

    def next(self, request):
        next_resource = self.request.environ.get('next_resource')
        if next_resource:
            url = make_url(request.request,
                           node=self.model,
                           resource=next_resource)
        else:
            url = make_url(request.request, node=self.model)
        if self.ajax_request:
            return [
                AjaxAction(url, 'leftcolumn', 'replace', '.left_column'),
                AjaxAction(url, 'rightcolumn', 'replace', '.right_column'),
            ]
        return HTTPFound(location=url)


@tile('editform', interface=Group, permission="edit_group", strict=False)
class GroupEditForm(GroupForm, Form):
    __metaclass__ = plumber
    __plumbing__ = EditBehavior, PrincipalRolesForm, EditFormFiddle

    show_heading = False
    show_contextmenu = False

    def save(self, widget, data):
        settings = ugm_groups(self.model)
        attrmap = settings.attrs.groups_form_attrmap
        for key in attrmap:
            if key in ['id']:
                continue
            extracted = data.fetch('groupform.%s' % key).extracted
            if not extracted:
                if key in self.model.attrs:
                    del self.model.attrs[key]
            else:
                self.model.attrs[key] = extracted
        self.model.model.context()

    def next(self, request):
        url = make_url(request.request, node=self.model)
        if self.ajax_request:
            return [
                AjaxAction(url, 'leftcolumn', 'replace', '.left_column'),
                AjaxAction(url, 'rightcolumn', 'replace', '.right_column'),
            ]
        return HTTPFound(location=url)
