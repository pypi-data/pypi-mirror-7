=====================================
 Sphinx Themes for Plone Documentation
=====================================

Introduction
============

This package is a collection of sphinx themes for the plone documentation.


Setup
=====



1. Install the package::

	  $ easy_install sphinx.themes.plone

	  or

      $ pip install sphinx.themes.plone

      or using buildout::

            [buildout]
		    parts=
		        sphinx
		    
		    [sphinx]
		    recipe=zc.recipe.egg
		    eggs=
		        Sphinx
		        sphinx.themes.plone

2. Edit the "conf.py" configuration file to point to the plone themes::

      # At the top.
      import sphinx.themes.plone

      # ...

      # Activate the theme path.
      html_theme_path = sphinx.themes.plone.get_html_theme_path()

3. Select a Plone theme:

	  # Activate the theme like this:
      html_theme = 'plone_org_4'

      # Avaliable Themes:
      * plone_org_4
      * plone_org_5 (todo finializisations)
      * plone_classic (todo implementation)
      * plone_sunburst (Todo implementation)
