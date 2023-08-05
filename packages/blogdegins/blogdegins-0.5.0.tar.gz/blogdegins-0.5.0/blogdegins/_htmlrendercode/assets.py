# -*- encoding: utf-8 -*-
import os.path
from webassets import Environment, Bundle

css_or_scss_content = [
    'css/libs/normalize/normalize.css',  # must be in first place
    'css/app/base.scss',
    'css/app/content.scss',
    'css/widgets/boxlist.scss'
]
top_js_content = [
    'js/top/modernizr.js',          # must be in first place
    'js/top/jquery.js',
]
bottom_js_content = [
    'js/bottom/libs/plugins.js',
    'js/bottom/app/base.js',
    'js/bottom/app/content.js',
    'js/bottom/widgets/boxlist.js',
]


def get_assets_env(htmlrendercode_path, output_path, debug=False):
    """ The directory structure of assets is:
        output_path
            static
                css
                js
    """
    output_path = os.path.join(output_path, 'static')
    assets_env = Environment(output_path, 'static', debug=debug)
    assets_env.config['compass_config'] = {
        'additional_import_paths': [
            os.path.join(htmlrendercode_path, 'scss-mixins')
        ],
        #'sass_options': "cache: False", ??? i can't get it.
        'http_path': "/static",
    }

    css_list = []
    scss_list = []

    for filename in css_or_scss_content:
        ext = os.path.splitext(filename)[1]
        if ext == '.scss':
            scss_list.append(filename)
        elif ext == '.css':
            css_list.append(filename)
        else:
            raise Exception('Bad extension: is %s instead of css/scss' % ext)

    css_bundle = Bundle(*css_list)
    scss_bundle = []
    for scss_file in scss_list:
        x = Bundle(
            scss_file,
            filters='compass',
            output=scss_file + '.css',
        )
        scss_bundle.append(x)
    css = Bundle(
        css_bundle,
        *scss_bundle,
        filters='yui_css',
        output='css/packed.css'
        #output='css/packed.%(version)s.css'
    )
    assets_env.register('css', css)

    top_js = Bundle(
        *top_js_content,
        filters='yui_js',
        output='js/top.js'
        #output='js/top.%(version)s.js'
    )
    assets_env.register('top_js', top_js)

    bottom_js = Bundle(
        *bottom_js_content,
        filters='yui_js',
        output='js/bottom.js'
        #output='js/bottom.%(version)s.js'
    )
    assets_env.register('bottom_js', bottom_js)

    return assets_env
