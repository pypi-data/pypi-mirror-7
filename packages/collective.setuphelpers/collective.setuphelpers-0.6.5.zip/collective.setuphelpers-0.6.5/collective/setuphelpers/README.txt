collective.setuphelpers
=======================

This package provides a few simple functions with common tasks used with initial
site content setup.

This does not aim to be as general as possible but it may speed things up.

>>> from collective.setuphelpers.structure import setupStructure
>>> portal = layer['portal']
>>> STRUCTURE = [{'id':'example-id','title':'Example title','type':'Document'}]
>>> setupStructure(portal, STRUCTURE)
>>> portal['example-id']
<ATDocument at /plone/example-id>
>>> portal.manage_delObjects(['example-id'])

You can use subfolders etc.

>>> setupStructure(portal, layer['test_structure'])
>>> portal['testfolder']['item1'].getText()
'<p>Text body</p>'


Content related methods:
~~~~~~~~~~~~~~~~~~~~~~~~

::

  def clearUpSite(context, to_delete):
    """ Remove content from the plone site root using given list of ids e.g.:
        TO_DELETE = ['news', 'events']
    """


  def setupStructure(portal, structure, default_language=LANGUAGE, base_path=''):
    """ Setup initial content structure. e.g.:

        STRUCTURE = [
            {
                'title' : 'About us',
                'type' : 'Document',
                'interfaces': (
                    IMyCustomMarkerInterface,
                )
            },
            {
                'title' : 'Products',
                'type' : 'Folder',
                'layout': 'folder_listing',
                'subfolder': [
                    {
                        'title': 'Cheap Products',
                        'type': 'Folder',
                        'allowed_types': ['Document'],
                        'block-portlets': {'manager': 'plone.rightcolumn'},
                        # pass either module or configuration dict to the 'portlets' key
                        'portlets':
                            [ plone.app.portlets.portlets.calendar,
                              { 'module': plone.app.portlets.portlets.classic,
                                'name': 'myportlet1',
                                'manager': 'plone.rightcolumn',
                                'params': dict(template='mytemplate', macro='portlet')
                               }
                            ],
                        'subfolder': [
                            {
                                'title': 'Product 1',
                                'type': 'Document',
                                'layout': '@@product-page'
                            },
                            {
                                'title': 'Recommended',
                                'type': 'Collection',
                            },
                            {
                                 'title': u'Picture',
                                 'id': u'image1.jpg',
                                 'type':'Image',
                                 'file': 'data/image1.jpg',
                            },
                        ]
                    }
                ]
            }
        ]

        base_path parameter can specify absolute path for Files and Images. For example
        you can use context._profile_path, where context is GenericSetup context. It allows
        you to put files and images to profiles/default/data/image1.jpg.
    """


Users and groups related methods:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  def createGroups(portal, groups):
    """ Create user groups by passing list of tuples containing group ids and titles:

        @example groups list:

        GROUPS = [
          ('customers', 'Customers'),
          ('staff', 'Staff')
        ]

        from tools.sitesetup import createGroups
        createGroups(portal, GROUPS)

    """

  enableSelfRegistration(portal):
    """ Enable anonymous users to register their user account. """

  def enableUserPwdChoice(portal):
    """ Enable user password choice during user registration. """


Various methods:
~~~~~~~~~~~~~~~~

::

  def registerDisplayViews(portal, views):
    """ Register additional display views for content types based on "views"
        dictionary containing list of additional view ids for each content type.

        @example views dictionary:

        DISPLAY_VIEWS = {
            'Folder': [
                'short-listing',
                'extended-listing'
            ],

            'Document': [
                'article-view',
                'fancy-document-view'
            ]
        }

        @call from setup handler:

        from tools.sitesetup import registerDisplayViews
        registerDisplayViews(portal, DISPLAY_VIEWS)

    """


  def unregisterDisplayViews(portal, views):
    """ Unregister additional display views for content types based on "views"
        dictionary containing list of additional view ids for each content type
        (the same as for registerDisplayViews method).
    """


  def setupCatalog(portal, indexes={}, metadata=[]):
    """ Register portal catalog indexes and metadata columns. """


  def hideActions(portal, actions):
    """ Hide actions given dict of action categories with values as list of action ids
        example actions:
        HIDE_ACTIONS = {'user':['dashboard'], 'object':['contentrules', 'local_roles']}
    """


  def registerActions(portal, actions={}):
    """ Register new portal actions using dict of action attributes like in the following
        example:
        CUSTOM_ACTIONS = {
            '1': { # order in which will be action registered
                'id': 'my-action',
                'category': 'site_actions',
                'title': 'My action',
                'i18n_domain': 'myi18n.domain',
                'url_expr': string:${globals_view/navigationRootUrl}/my-action-view',
                'available_expr': 'python:member is not None'
                'permissions': ('View',),
                'visible': True
            }
        }
    """


  def setupTinyMCE(portal, settings):
    """ Configures tinymce wysiwyg editor. Here is an example settings object:
    EDITOR_SETTINGS = {
        'attributes': {
            'contextmenu': False,
            'link_using_uids': True,
            'allow_captioned_images': True,
            '...': True
        },
        'commands': {
            'install_transforms': True
        },
        'toolbar': {
            'advhr':False,
            'anchor':False,
            'attribs':False,
            'backcolor':False,
            'bold':True,
            'bullist':True,
            'charmap':False,
            'cleanup':False,
            'code':True,
            'copy':False,
            'cut':False,
            'definitionlist':False,
            'emotions':False,
            'external':False,
            'forecolor':False,
            'fullscreen':False,
            'hr':False,
            'iespell':False,
            'image':True,
            'indent':False,
            'insertdate':False,
            'inserttime':False,
            'italic':True,
            'justifycenter':False,
            'justifyfull':False,
            'justifyleft':False,
            'justifyright':False,
            'link':True,
            'media':False,
            'nonbreaking':False,
            'numlist':True,
            'outdent':False,
            'pagebreak':False,
            'paste':False,
            'pastetext':False,
            'pasteword':False,
            'preview':False,
            'print':False,
            'redo':False,
            'removeformat':False,
            'replace':False,
            'save':False,
            'search':False,
            'strikethrough':False,
            'style':True,
            'sub':False,
            'sup':False,
            'tablecontrols':True,
            'underline':False,
            'undo':False,
            'unlink':True,
            'visualaid':False,
            'visualchars':False,
            'width':u'440'
        },
        'styles': [
            'Subheading|h3',
            '...|..'
        ],
        'tablestyles': [
            'Subdued grid|plain',
            '...|...'
        ],
        'linkable': [
            'News Item',
            '...'
        ],
        'containsanchors': [
            'Document',
            '...'
        ],
        'containsobjects': [
            'Folder',
            '...'
        ],
        'imageobjects': [
            'Image',
            '...'
        ],
    }
    """


  def setupCTAvailability(portal, settings):
    """ Use this method to allow/disable content types to be globally or locally addable.
        All non listed content types will be automatically disabled.
        Here is example settings object (NOTE: "DISABLE" key is used to disable
        content types adding globally):

        CONTENT_TYPES_AVAILABILITY = {
            'DISABLE': [
                'Event',
                'Link'
            ],
            'Plone Site': [
                'Folder',
                'Document'
            ]
        }
    """


  def setupHTMLFiltering(portal, settings):
    """ Update html filtering configlet settings, by passing dict of settings as in the
        following example for enabling embed html content in the richtext:

        HTML_FILTER = {
            'remove': {
                'nasty': ['embed', 'object'],
                'stripped': ['object', 'param'],
                'custom': []
            },
            'add': {
                'nasty': [],
                'stripped': [],
                'custom': ['embed']
            }
        }

        NOTE: you can ommit empty lists
    """


  def registerTransform(portal, name, module):
    """
    Usage:

    registerTransform(portal, 'web_intelligent_plain_text_to_html',
        'Products.intelligenttext.transforms.web_intelligent_plain_text_to_html')

    """


  def unregisterTransform(portal, name):
    """
    Usage:

    unregisterTransform(portal, 'web_intelligent_plain_text_to_html')

    """


  def setHomePage(portal, view_name):
    """ Set default view for the site root. """


  def setupNavigation(portal, settings):
    """ Use this method to exclude/include content types from navigation  globally.
        Here is example settings object:

        NAVIGATION = {
            'include': [
                'Folder',
                'CustomFolder'
            ],
            'exclude': [
                'Link',
                'Document',
                'Event'
            ]
        }
    """


  def hidePortletTypes(portal, portlets=[]):
    """
        Hides portlets from the portlet management pages.
        @param: portlets - list of portlet idenifiers used in portlets.xml to register them

        example: portlets=['portlets.Calendar', 'portlets.Classic']
    """

  def registerResourceBundle(portal, bundles={}):
    """
        Register resource registry bundles for themes (skin layers).
        @param: bundles - dict of skin layers with list of bundles

        example: RESOURCE_BUNDLES = {
            'MySkin': ['default', 'jquery', 'jquerytools'],
            'OtherSkin': ['default']
        }
    """


  def unregisterResourceBundle(portal, layers=[]):
    """
        Unregister custom resource registry bundles for themes (skin layers).
        @param: layers - list of layers for which will be custom bundles unregistered so the skin layer will use only 'default' bundle.

        example: BUNDLES_TO_REMOVE = ['MySkin', 'OtherSkin']
    """


Utils:
~~~~~~

::

  def makeFieldsInvisible(schema=None, fields=[]):
    """ Makes schemata fields respective widgets invisible in the view page or edit form.

        @schema: Archetypes schema object
        @fields: list of field ids/names
    """

  def changeFieldsSchemata(schema=None, fields=[]):
    """ Moves fields into different schemata parts like categorisation or settings etc.
        "fields" parameter is expected to be a list of dicts with key: (field) id and
        (schemata id) schemata
    """


Contributors:
~~~~~~~~~~~~~

- `Matous Hora (mhora)`__

.. _mhora: mailto:matous@fry-it.com

__ mhora_

- `Radim Novotny (naro)`__

.. _naro: mailto:radim@fry-it.com

__ naro_

- `Lukas Zdych (lzdych)`__

.. _lzdych: mailto:lukas@fry-it.com

__ lzdych_


