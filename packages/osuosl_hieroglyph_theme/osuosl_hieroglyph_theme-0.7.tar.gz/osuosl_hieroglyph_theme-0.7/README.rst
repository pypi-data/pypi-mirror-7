Hieroglyph theme for the OSU Open Source Lab
--------------------------------------------

To make go:

In conf.py::

    import osuosl_hieroglyph_theme
    html_theme = 'osuosl'  ##(must be changed in file)!
    html_theme_path = osuosl_hieroglyph_theme.get_html_theme_path()
    html_static_path = ['_static', html_theme_path + '/osuosl/static/'] ##(must be changed in file)
    slide_theme_options = {'custom_css' : 'osuosl.css'}
    slide_footer = "<img src='_static/osu-tag.png'><img src='_static/logo.png'>"

For the html_theme and html_static_path variables, you must find the defaults in the file and change them, as they will not be overridden by your declaration of them!

    ::
    
    make slides
