#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages
from zope.interface import Interface, Attribute
from zope.schema import TextLine, Bool

# import local packages
from ztfy.file.schema import ImageField, FileField

from ztfy.myams import _


class IMyAMSStaticConfiguration(Interface):
    """MyAMS static configuration"""

    include_top_links = Bool(title=_("Include top links?"),
                             default=True,
                             required=True)

    include_site_search = Bool(title=_("Include site search?"),
                               default=True,
                               required=True)

    include_mobile_search = Bool(title=_("Include mobile search?"),
                                 default=True,
                                 required=True)

    include_user_activity = Bool(title=_("Include user dropdown window?"),
                                 default=True,
                                 required=True)

    include_user_shortcuts = Bool(title=_("Include user shortcuts?"),
                                  default=True,
                                  required=True)

    include_logout_button = Bool(title=_("Include logout button?"),
                                 default=True,
                                 required=True)

    include_minify_button = Bool(title=_("Include minify button?"),
                                 default=True,
                                 required=True)

    include_flags = Bool(title=_("Include flags menu?"),
                         default=True,
                         required=True)

    include_menus = Bool(title=_("Include main menus?"),
                         default=True,
                         required=True)

    include_ribbon = Bool(title=_("Include ribbon?"),
                          default=True,
                          required=True)

    include_reload_button = Bool(title=_("Include reload button?"),
                                 default=True,
                                 required=True)

    body_css_class = TextLine(title=_("Body HTML tag CSS class"),
                              required=False)


class IMyAMSConfiguration(Interface):
    """MyAMS application global configuration"""

    title = TextLine(title=_("Title"),
                     description=_("Application title displayed in title bar"),
                     required=False)

    description = TextLine(title=_("Description"),
                           description=_("Main application description"),
                           required=False)

    author = TextLine(title=_("Author"),
                      description=_("Public author name"),
                      required=False)

    icon = ImageField(title=_("Favorites icon"),
                      description=_("Please provide a transparent image of 32x32 pixels..."),
                      required=False)

    logo = ImageField(title=_("Logo"),
                      description=_("Please provide a transparent image in PNG format..."),
                      required=False)

    logo_title = TextLine(title=_("Logo title"),
                          description=_("This text will be used as logo alternate text"),
                          required=False)

    custom_css = FileField(title=_("Custom CSS file"),
                           required=False)

    custom_js = FileField(title=_("Custom javascript file"),
                          required=False)

    google_analytics_key = TextLine(title=_("Google Analytics key"),
                                    required=False)

    static_configuration = Attribute(_("Application static configuration utility"))


class IMyAMSConfigurationTarget(Interface):
    """MyAMS configuration marker interface"""
