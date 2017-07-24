# -*- coding: utf-8 -*-
#
# F5 Agent for OpenStack Neutron documentation build configuration file, created by
# sphinx-quickstart on Tue May 24 09:31:49 2016.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

import sys
import os

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('.'))

import f5_openstack_agent
import f5_sphinx_theme

VERSION = f5_openstack_agent.__version__

# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#needs_sphinx = '1.4'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
    'cloud_sptheme.ext.table_styling',
    'sphinxjp.themes.basicstrap',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The encoding of source files.
#source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'F5 Agent for OpenStack Neutron'
copyright = u'2017 F5 Networks'
author = u'F5 Networks'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = VERSION
# The full version, including alpha/beta/rc tags.
release = VERSION

# F5 SDK release version should be set here
f5_sdk_version = '2.3.3'
# F5 icontrol REST version should be set here
f5_icontrol_version = '1.3.0'

#rst_prolog = '''
#'''

# OpenStack release

openstack_release = "Liberty"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build',
                    'Thumbs.db',
                    '.DS_Store',
                    'README.rst',
                    'drafts/',
                    '_static/reuse',
                     ]

suppress_warnings = ['image.nonlocal_uri']

# The reST default role (used for this markup: `text`) to use for all
# documents.
#default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
#add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
#modindex_common_prefix = []

# If true, keep warnings as "system message" paragraphs in the built documents.
#keep_warnings = False

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'f5_sphinx_theme'
html_theme_path = f5_sphinx_theme.get_html_theme_path()

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
                        #'site_name': 'F5 OpenStack Docs Home',
                        'next_prev_link': False
                     }

# The name for this set of Sphinx documents.
# "<project> v<release> documentation" by default.
html_title = u'F5 Agent for OpenStack Neutron'

# A shorter title for the navigation bar.  Default is the same as html_title.
#html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
#html_logo = None

# The name of an image file (relative to this directory) to use as a favicon of
# the docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
#html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Add any extra paths that contain custom files (such as robots.txt or
# .htaccess) here, relative to this directory. These files are copied
# directly to the root of the documentation.
#html_extra_path = []

# If not None, a 'Last updated on:' timestamp is inserted at every page
# bottom, using the given strftime format.
# The empty string is equivalent to '%b %d, %Y'.
#html_last_updated_fmt = None

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
html_sidebars = {'**': ['searchbox.html', 'localtoc.html', 'globaltoc.html']}

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {}

# If false, no module index is generated.
#html_domain_indices = True

# If false, no index is generated.
#html_use_index = True

# If true, the index is split into individual pages for each letter.
#html_split_index = False

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
html_show_sphinx = False

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = None

# Language to be used for generating the HTML full-text search index.
# Sphinx supports the following languages:
#   'da', 'de', 'en', 'es', 'fi', 'fr', 'hu', 'it', 'ja'
#   'nl', 'no', 'pt', 'ro', 'ru', 'sv', 'tr', 'zh'
#html_search_language = 'en'

# A dictionary with options for the search language support, empty by default.
# 'ja' uses this config value.
# 'zh' user can custom change `jieba` dictionary path.
#html_search_options = {'type': 'default'}

# The name of a javascript file (relative to the configuration directory) that
# implements a search results scorer. If empty, the default will be used.
#html_search_scorer = 'scorer.js'

# Output file base name for HTML help builder.
htmlhelp_basename = 'F5-OpenStack-BIG-IP-Controllerdoc'

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
# The paper size ('letterpaper' or 'a4paper').
#'papersize': 'letterpaper',

# The font size ('10pt', '11pt' or '12pt').
#'pointsize': '10pt',

# Additional stuff for the LaTeX preamble.
#'preamble': '',

# Latex figure (float) alignment
#'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'F5-OpenStack-BIG-IP-Controller.tex', u'F5 Agent for OpenStack Neutron Documentation',
     u'F5 Networks', 'manual'),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
#latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#latex_use_parts = False

# If true, show page references after internal links.
#latex_show_pagerefs = False

# If true, show URL addresses after external links.
#latex_show_urls = False

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_domain_indices = True


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc,
     'f5-openstack-agent',
     u'F5 Agent for OpenStack Neutron Documentation',
     [author],
     1)
]

# If true, show URL addresses after external links.
#man_show_urls = False


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'f5-openstack-agent',
     u'F5 Agent for OpenStack Neutron Documentation',
     [author],
     'f5-openstack-agent',
     'manual'),
]

# Documents to append as an appendix to all manuals.
#texinfo_appendices = []

# If false, no module index is generated.
#texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
texinfo_show_urls = 'footnote'

# If true, do not generate a @detailmenu in the "Top" node's menu.
#texinfo_no_detailmenu = False


# intersphinx: refer to other F5 OpenStack documentation sets.
#intersphinx_mapping = {'heat': (
#    'http://f5-openstack-heat.readthedocs.io/en/'+openstack_release.lower(
# ), None),
#    'heatplugins': (
#    'http://f5-openstack-heat-plugins.readthedocs.io/en/'+openstack_release
# .lower(), None),
#    'lbaasv1': (
#    'http://f5-openstack-lbaasv1.readthedocs.io/en/'+openstack_release
# .lower(), None),
#    'lbaasv2driver': (
#    'http://f5-openstack-lbaasv2-driver.readthedocs.io/en
# /'+openstack_release.lower(), None),
#    'f5sdk': (
#    'http://f5-sdk.readthedocs.io/en/latest/', None),
#    'osdocs': (
#    'http://clouddocs.f5.com/cloud/openstack/latest/', None),
#    }

rst_epilog = '''
.. |openstack| replace:: %(openstack_release)s
.. |f5_agent_pip_url| replace:: git+https://github.com/F5Networks/f5-openstack-agent@v%(version)s
.. |f5_agent_pip_url_branch| replace:: git+https://github.com/F5Networks/f5-openstack-agent@%(openstack_release_l)s
.. |f5_agent_deb_url| replace:: https://github.com/F5Networks/f5-openstack-agent/releases/download/v%(version)s/python-f5-openstack-agent_%(version)s-1_1404_all.deb
.. |f5_agent_rpm_url| replace:: https://github.com/F5Networks/f5-openstack-agent/releases/download/v%(version)s/f5-openstack-agent-%(version)s-1.el7.noarch.rpm
.. |f5_agent_deb_package| replace:: python-f5-openstack-agent_%(version)s-1_1404_all.deb
.. |f5_agent_rpm_package| replace:: f5-openstack-agent-%(version)s-1.el7.noarch.rpm
.. |f5_sdk_deb_url| replace:: https://github.com/F5Networks/f5-common-python/releases/download/v%(f5_sdk_version)s/python-f5-sdk_%(f5_sdk_version)s-1_1404_all.deb
.. |f5_sdk_rpm_url| replace:: https://github.com/F5Networks/f5-common-python/releases/download/v%(f5_sdk_version)s/f5-sdk-%(f5_sdk_version)s-1.el7.noarch.rpm
.. |f5_sdk_rpm_package| replace:: f5-sdk-%(f5_sdk_version)s-1.el7.noarch.rpm
.. |f5_sdk_deb_package| replace:: python-f5-sdk_%(f5_sdk_version)s-1_1404_all.deb
.. |f5_icontrol_deb_url| replace:: https://github.com/F5Networks/f5-icontrol-rest-python/releases/download/v%(f5_icontrol_version)s/python-f5-icontrol-rest_%(f5_icontrol_version)s-1_1404_all.deb
.. |f5_icontrol_rpm_url| replace:: https://github.com/F5Networks/f5-icontrol-rest-python/releases/download/v%(f5_icontrol_version)s/f5-icontrol-rest-%(f5_icontrol_version)s-1.el7.noarch.rpm
.. |f5_icontrol_rpm_package| replace:: f5-icontrol-rest-%(f5_icontrol_version)s-1.el7.noarch.rpm
.. |f5_icontrol_deb_package| replace:: python-f5-icontrol-rest_%(f5_icontrol_version)s-1_1404_all.deb
.. |agent-long| replace:: F5 Agent for OpenStack Neutron
.. |agent| replace:: :code:`f5-openstack-agent`
.. |agent-short| replace:: F5 agent
.. |driver| replace:: :code:`f5-openstack-lbaasv2-driver`
.. |driver-long| replace:: F5 Driver for OpenStack LBaaS
.. |driver-short| replace:: F5 driver
.. |deb-download| raw:: html

    <a class="btn btn-info" href="https://github.com/F5Networks/f5-openstack-agent/releases/download/v%(version)s/python-f5-openstack-agent_%(version)s-1_1404_all.deb">Debian package</a>
.. |rpm-download| raw:: html

    <a class="btn btn-info" href="https://github.com/F5Networks/f5-openstack-agent/releases/download/v%(version)s/f5-openstack-agent-%(version)s-1.el7.noarch.rpm">RPM package</a>
.. |release-notes| raw:: html

    <a class="btn btn-success" href="https://github.com/F5Networks/f5-openstack-agent/releases/tag/v%(version)s/">Release Notes</a>
.. _Hierarchical Port Binding: /cloud/openstack/v1/lbaas/hierarchical-port-binding.html
.. _external provider network: https://docs.openstack.org/newton/networking-guide/intro-os-networking.html#provider-networks
.. _Cisco ACI: http://www.cisco.com/c/en/us/solutions/data-center-virtualization/application-centric-infrastructure/index.html
.. _system configuration: https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/bigip-system-initial-configuration-13-0-0/2.html
.. _local traffic management: https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/ltm-basics-13-0-0.html
.. _device service clustering: https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/bigip-device-service-clustering-admin-13-0-0.html
.. _VTEP: https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/bigip-tmos-tunnels-ipsec-13-0-0/3.html
.. _SNATs: https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/tmos-routing-administration-13-0-0/8.html
.. _self IP: https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/tmos-routing-administration-13-0-0/6.html
.. _Better or Best license: https://f5.com/products/how-to-buy/simplified-licensing
.. _secure network address translation: https://support.f5.com/kb/en-us/products/big-ip_ltm/manuals/product/tmos-routing-administration-13-0-0/8.html
.. _F5 Integration for OpenStack: /cloud/openstack/latest/lbaas
''' % {
  'version': version,
  'f5_sdk_version': f5_sdk_version,
  'f5_icontrol_version': f5_icontrol_version,
  'openstack_release': openstack_release,
  'openstack_release_l': openstack_release.lower(),
}
