# -*- coding: utf-8 -*-
from collections import defaultdict

from django.contrib.sites.models import Site
from django.utils.translation import get_language

from cms.apphook_pool import apphook_pool
from cms.compat import user_related_name
from cms.models.permissionmodels import ACCESS_DESCENDANTS
from cms.models.permissionmodels import ACCESS_PAGE_AND_DESCENDANTS
from cms.models.permissionmodels import ACCESS_CHILDREN
from cms.models.permissionmodels import ACCESS_PAGE_AND_CHILDREN
from cms.models.permissionmodels import ACCESS_PAGE
from cms.models.permissionmodels import PagePermission, GlobalPagePermission
from cms.utils import get_language_from_request
from cms.utils.conf import get_cms_setting
from cms.utils.i18n import get_fallback_languages, hide_untranslated
from cms.utils.page_resolver import get_page_queryset
from cms.utils.moderator import get_title_queryset, use_draft
from cms.utils.plugins import current_site
from menus.base import Menu, NavigationNode, Modifier
from menus.menu_pool import menu_pool


def get_visible_pages(request, pages, site=None):
    """
     This code is basically a many-pages-at-once version of
     Page.has_view_permission.
     pages contains all published pages
     check if there is ANY restriction
     that needs a permission page visibility calculation
    """
    public_for = get_cms_setting('PUBLIC_FOR')
    is_setting_public_all = public_for == 'all'
    is_setting_public_staff = public_for == 'staff'
    is_auth_user = request.user.is_authenticated()
    visible_page_ids = []
    restricted_pages = defaultdict(list)
    page_permissions = PagePermission.objects.filter(can_view=True).select_related(
            'page').prefetch_related('group__' + user_related_name)

    for perm in page_permissions:
        # collect the pages that are affected by permissions
        if site and perm.page.site_id != site.pk:
            continue
        if perm is not None and perm not in restricted_pages[perm.page.pk]:
            # affective restricted pages gathering
            # using mptt functions 
            # add the page with the perm itself
            if perm.grant_on in [ACCESS_PAGE, ACCESS_PAGE_AND_CHILDREN, ACCESS_PAGE_AND_DESCENDANTS]:
                restricted_pages[perm.page.pk].append(perm)
                restricted_pages[perm.page.publisher_public_id].append(perm)
                # add children
            if perm.grant_on in [ACCESS_CHILDREN, ACCESS_PAGE_AND_CHILDREN]:
                child_ids = perm.page.get_children().values_list('id', 'publisher_public_id')
                for id, public_id in child_ids:
                    restricted_pages[id].append(perm)
                    restricted_pages[public_id].append(perm)
            # add descendants
            elif perm.grant_on in [ACCESS_DESCENDANTS, ACCESS_PAGE_AND_DESCENDANTS]:
                child_ids = perm.page.get_descendants().values_list('id', 'publisher_public_id')
                for id, public_id in child_ids:
                    restricted_pages[id].append(perm)
                    restricted_pages[public_id].append(perm)

    # anonymous
    # no restriction applied at all
    if (not is_auth_user and
        is_setting_public_all and
        not restricted_pages):
        return [page.pk for page in pages]

    if site is None:
        site = current_site(request)

    # authenticated user and global permission
    if is_auth_user:
        global_view_perms = GlobalPagePermission.objects.user_has_view_permission(
            request.user, site.pk).exists()

        #no page perms edge case - all visible
        if ((is_setting_public_all or (
                is_setting_public_staff and request.user.is_staff)) and
            not restricted_pages and
            not global_view_perms):
            return [page.pk for page in pages]
        #no page perms edge case - none visible
        elif (is_setting_public_staff and
            not request.user.is_staff and
            not restricted_pages and
            not global_view_perms):
            return []


    def has_global_perm():
        if has_global_perm.cache < 0:
            has_global_perm.cache = 1 if request.user.has_perm('cms.view_page') else 0
        return bool(has_global_perm.cache)

    has_global_perm.cache = -1

    def has_permission_membership(page):
        """
        PagePermission user group membership tests
        """
        user_pk = request.user.pk
        page_pk = page.pk
        for perm in restricted_pages[page_pk]:
            if perm.user_id == user_pk:
                return True
            if not perm.group_id:
                continue
            user_set = getattr(perm.group, user_related_name)
            # Optimization equivalent to
            # if user_pk in user_set.values_list('pk', flat=True)
            if any(user_pk == user.pk for user in user_set.all()):
                return True
        return False

    for page in pages:
        to_add = False
        # default to false, showing a restricted page is bad
        # explicitly check all the conditions
        # of settings and permissions
        is_restricted = page.pk in restricted_pages
        # restricted_pages contains as key any page.pk that is
        # affected by a permission grant_on
        if is_auth_user:
            # a global permission was given to the request's user
            if global_view_perms:
                to_add = True
            # setting based handling of unrestricted pages
            elif not is_restricted and (
                    is_setting_public_all or (
                        is_setting_public_staff and request.user.is_staff)
            ):
                # authenticated user, no restriction and public for all
                # or 
                # authenticated staff user, no restriction and public for staff
                to_add = True
            # check group and user memberships to restricted pages
            elif is_restricted and has_permission_membership(page):
                to_add = True
            elif has_global_perm():
                to_add = True
        # anonymous user, no restriction  
        elif not is_restricted and is_setting_public_all:
            to_add = True
            # store it
        if to_add:
            visible_page_ids.append(page.pk)
    return visible_page_ids


def page_to_node(page, home, cut):
    """
    Transform a CMS page into a navigation node.

    :param page: the page you wish to transform
    :param home: a reference to the "home" page (the page with tree_id=1)
    :param cut: Should we cut page from its parent pages? This means the node will not
         have a parent anymore.
    """
    # Theses are simple to port over, since they are not calculated.
    # Other attributes will be added conditionnally later.
    attr = {'soft_root': page.soft_root,
        'auth_required': page.login_required,
        'reverse_id': page.reverse_id, }

    parent_id = page.parent_id
    # Should we cut the Node from its parents?
    if home and page.parent_id == home.pk and cut:
        parent_id = None

    # possible fix for a possible problem
    #if parent_id and not page.parent.get_calculated_status():
    #    parent_id = None # ????

    if page.limit_visibility_in_menu == None:
        attr['visible_for_authenticated'] = True
        attr['visible_for_anonymous'] = True
    else:
        attr['visible_for_authenticated'] = page.limit_visibility_in_menu == 1
        attr['visible_for_anonymous'] = page.limit_visibility_in_menu == 2
    attr['is_home'] = page.is_home
    # Extenders can be either navigation extenders or from apphooks.
    extenders = []
    if page.navigation_extenders:
        extenders.append(page.navigation_extenders)
        # Is this page an apphook? If so, we need to handle the apphooks's nodes
    lang = get_language()
    # Only run this if we have a translation in the requested language for this
    # object. The title cache should have been prepopulated in CMSMenu.get_nodes
    # but otherwise, just request the title normally
    if not hasattr(page, 'title_cache') or lang in page.title_cache:
        app_name = page.get_application_urls(fallback=False)
        if app_name: # it means it is an apphook
            app = apphook_pool.get_apphook(app_name)
            for menu in app.menus:
                extenders.append(menu.__name__)

    if extenders:
        attr['navigation_extenders'] = extenders

    # Do we have a redirectURL?
    attr['redirect_url'] = page.get_redirect()  # save redirect URL if any

    # Now finally, build the NavigationNode object and return it.
    ret_node = NavigationNode(
        page.get_menu_title(),
        page.get_absolute_url(),
        page.pk,
        parent_id,
        attr=attr,
        visible=page.in_navigation,
    )
    return ret_node


class CMSMenu(Menu):
    def get_nodes(self, request):
        page_queryset = get_page_queryset(request)
        site = Site.objects.get_current()
        lang = get_language_from_request(request)

        filters = {
            'site': site,
        }

        if hide_untranslated(lang, site.pk):
            filters['title_set__language'] = lang

        if not use_draft(request):
            page_queryset = page_queryset.published(lang)
        pages = page_queryset.filter(**filters).order_by("tree_id", "lft")
        ids = {}
        nodes = []
        first = True
        home_cut = False
        home_children = []
        home = None
        actual_pages = []

        # cache view perms
        visible_pages = get_visible_pages(request, pages, site)
        for page in pages:
            # Pages are ordered by tree_id, therefore the first page is the root
            # of the page tree (a.k.a "home")
            if page.pk not in visible_pages:
                # Don't include pages the user doesn't have access to
                continue
            if not home:
                home = page
            if first and page.pk != home.pk:
                home_cut = True
            if (page.parent_id == home.pk or page.parent_id in home_children) and home_cut:
                home_children.append(page.pk)
            if (page.pk == home.pk and home.in_navigation) or page.pk != home.pk:
                first = False
            ids[page.id] = page
            actual_pages.append(page)
            page.title_cache = {}

        langs = [lang]
        if not hide_untranslated(lang):
            langs.extend(get_fallback_languages(lang))

        titles = list(get_title_queryset(request).filter(page__in=ids, language__in=langs))
        for title in titles: # add the title and slugs and some meta data
            page = ids[title.page_id]
            page.title_cache[title.language] = title

        for page in actual_pages:
            if page.title_cache:
                nodes.append(page_to_node(page, home, home_cut))
        return nodes


menu_pool.register_menu(CMSMenu)


class NavExtender(Modifier):
    def modify(self, request, nodes, namespace, root_id, post_cut, breadcrumb):
        if post_cut:
            return nodes
        exts = []
        # rearrange the parent relations
        home = None
        for node in nodes:
            if node.attr.get("is_home", False):
                home = node
            extenders = node.attr.get("navigation_extenders", None)
            if extenders:
                for ext in extenders:
                    if not ext in exts:
                        exts.append(ext)
                    for extnode in nodes:
                        if extnode.namespace == ext and not extnode.parent_id:# if home has nav extenders but home is not visible
                            if node.attr.get("is_home", False) and not node.visible:
                                extnode.parent_id = None
                                extnode.parent_namespace = None
                                extnode.parent = None
                            else:
                                extnode.parent_id = node.id
                                extnode.parent_namespace = node.namespace
                                extnode.parent = node
                                node.children.append(extnode)
        removed = []
        # find all not assigned nodes
        for menu in menu_pool.menus.items():
            if hasattr(menu[1], 'cms_enabled') and menu[1].cms_enabled and not menu[0] in exts:
                for node in nodes:
                    if node.namespace == menu[0]:
                        removed.append(node)
        if breadcrumb:
        # if breadcrumb and home not in navigation add node
            if breadcrumb and home and not home.visible:
                home.visible = True
                if request.path == home.get_absolute_url():
                    home.selected = True
                else:
                    home.selected = False
                    # remove all nodes that are nav_extenders and not assigned
        for node in removed:
            nodes.remove(node)
        return nodes


menu_pool.register_modifier(NavExtender)


class SoftRootCutter(Modifier):
    """
    Ask evildmp/superdmp if you don't understand softroots!
    
    Softroot description from the docs:
    
        A soft root is a page that acts as the root for a menu navigation tree.
    
        Typically, this will be a page that is the root of a significant new
        section on your site.
    
        When the soft root feature is enabled, the navigation menu for any page
        will start at the nearest soft root, rather than at the real root of
        the site’s page hierarchy.
    
        This feature is useful when your site has deep page hierarchies (and
        therefore multiple levels in its navigation trees). In such a case, you
        usually don’t want to present site visitors with deep menus of nested
        items.
    
        For example, you’re on the page -Introduction to Bleeding-?, so the menu
        might look like this:
    
            School of Medicine
                Medical Education
                Departments
                    Department of Lorem Ipsum
                    Department of Donec Imperdiet
                    Department of Cras Eros
                    Department of Mediaeval Surgery
                        Theory
                        Cures
                        Bleeding
                            Introduction to Bleeding <this is the current page>
                            Bleeding - the scientific evidence
                            Cleaning up the mess
                            Cupping
                            Leaches
                            Maggots
                        Techniques
                        Instruments
                    Department of Curabitur a Purus
                    Department of Sed Accumsan
                    Department of Etiam
                Research
                Administration
                Contact us
                Impressum
    
        which is frankly overwhelming.
    
        By making -Department of Mediaeval Surgery-? a soft root, the menu
        becomes much more manageable:
    
            Department of Mediaeval Surgery
                Theory
                Cures
                    Bleeding
                        Introduction to Bleeding <current page>
                        Bleeding - the scientific evidence
                        Cleaning up the mess
                    Cupping
                    Leaches
                    Maggots
                Techniques
                Instruments
    """

    def modify(self, request, nodes, namespace, root_id, post_cut, breadcrumb):
        # only apply this modifier if we're pre-cut (since what we do is cut)
        if post_cut:
            return nodes
        selected = None
        root_nodes = []
        # find the selected node as well as all the root nodes
        for node in nodes:
            if node.selected:
                selected = node
            if not node.parent:
                root_nodes.append(node)

        # if we found a selected ...
        if selected:
            # and the selected is a softroot
            if selected.attr.get("soft_root", False):
                # get it's descendants
                nodes = selected.get_descendants()
                # remove the link to parent
                selected.parent = None
                # make the selected page the root in the menu
                nodes = [selected] + nodes
            else:
                # if it's not a soft root, walk ancestors (upwards!)
                nodes = self.find_ancestors_and_remove_children(selected, nodes)
        return nodes

    def find_and_remove_children(self, node, nodes):
        for child in node.children:
            if child.attr.get("soft_root", False):
                self.remove_children(child, nodes)
        return nodes

    def remove_children(self, node, nodes):
        for child in node.children:
            nodes.remove(child)
            self.remove_children(child, nodes)
        node.children = []

    def find_ancestors_and_remove_children(self, node, nodes):
        """
        Check ancestors of node for soft roots
        """
        if node.parent:
            if node.parent.attr.get("soft_root", False):
                nodes = node.parent.get_descendants()
                node.parent.parent = None
                nodes = [node.parent] + nodes
            else:
                nodes = self.find_ancestors_and_remove_children(node.parent, nodes)
        else:
            for newnode in nodes:
                if newnode != node and not newnode.parent:
                    self.find_and_remove_children(newnode, nodes)
        for child in node.children:
            if child != node:
                self.find_and_remove_children(child, nodes)
        return nodes


menu_pool.register_modifier(SoftRootCutter)
