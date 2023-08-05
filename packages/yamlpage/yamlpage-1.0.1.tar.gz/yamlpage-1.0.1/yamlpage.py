# -*- coding: utf-8 -*-
'''
yamlpage
========
Flatpages based on files with yaml syntax

Install
-------
    pip install yamlpage

Usage
-----
    >>> from yamlpage import YamlPage
    >>> p = YamlPage('./content')


Put page

    >>> url = '/my/url'
    >>> p.put(url, (
    ...     ('title', 'foo'),
    ...     ('body', 'foo\\nbar'),
    ... ))

    >>> path = './content/^my^url.yaml'
    >>> print(open(path).read())
    title: foo
    body: |-
      foo
      bar
    <BLANKLINE>


Get page

    >>> p.get(url) == {'body': 'foo\\nbar', 'url': '/my/url',
    ...     'filename': './content/^my^url.yaml', 'title': 'foo'}
    True

    >>> p.get('/not/found/') is None
    True

Check exists

    >>> p.exists(url)
    True
    >>> p.exists('/not/found/')
    False
'''
from __future__ import print_function
from __future__ import absolute_import

import os
import sys
import warnings

import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    warnings.warn('You have to install libyaml and reinstall pyyaml '
                  'for increase perfomance')
    from yaml import Loader
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


if sys.version_info > (3, ):
    unicode = str
    basestring = str


class YamlPage(object):
    def __init__(self, root_dir='.', path_delimiter='^',
                 file_extension='yaml'):
        self.root_dir = root_dir
        self.path_delimiter = path_delimiter
        self.file_extension = '.' + file_extension.lstrip('.')

    def url_to_path(self, url):
        '''
            >>> obj = YamlPage('root/dir')
            >>> obj.url_to_path('a/b/c')
            'root/dir/a^b^c.yaml'
        '''
        filename = url.replace('/', self.path_delimiter) + self.file_extension
        return os.path.join(self.root_dir, filename)

    def exists(self, url):
        filename = self.url_to_path(url)
        return os.path.isfile(filename)

    def get(self, url):
        '''Return loaded yaml or None'''
        filename = self.url_to_path(url)
        try:
            with open(filename, 'rb') as f:
                page = yaml.load(f, Loader=Loader)
                page.setdefault('url', url)
                page.setdefault('filename', filename)
                return page
        except IOError:
            return None

    def put(self, url, data):
        dump = dumps(data)
        filename = self.url_to_path(url)
        with open(filename, 'w') as f:
            f.write(dump)


class literal(unicode):
    pass


class unquoted(unicode):
    pass


def ordered_dict_presenter(dumper, data):
    return dumper.represent_dict(data.items())


def literal_presenter(dumper, data):
    return dumper.represent_scalar(
        'tag:yaml.org,2002:str', data, style='|')


def unquoted_presenter(dumper, data):
    return dumper.represent_scalar(
        'tag:yaml.org,2002:str', data, style='')

yaml.add_representer(literal, literal_presenter)
yaml.add_representer(OrderedDict, ordered_dict_presenter)
yaml.add_representer(unquoted, unquoted_presenter)


def dumps(items):
    '''
    Tip: if you want to do literal (|) style of strings, remove trailing spaces

        >>> dumps([1, 2, 3])
        '- 1\\n- 2\\n- 3\\n'

        >>> print(dumps([('foo', 1), ('bar', 2)]))
        foo: 1
        bar: 2
        <BLANKLINE>

        >>> print(dumps({'foo': 1, 'bar': 2}))
        bar: 2
        foo: 1
        <BLANKLINE>
    '''
    if isinstance(items, dict):
        items = sorted(items.items(), key=lambda x: x[0])
    try:
        dict(items)
    except (TypeError, ValueError):
        data = items
    else:
        data = OrderedDict()
        for k, v in items:
            if isinstance(v, basestring):
                if '\n' in v:
                    v = v.replace('\r', '')
                    v = v.replace('\t', '    ')
                    # literal string doesn't works
                    # if any of string has trailing space
                    v = '\n'.join(r.rstrip() for r in v.split('\n'))
                    v = literal(v)
                else:
                    v = unquoted(v)
            data[k] = v
    return yaml.dump(data, allow_unicode=True, default_flow_style=False)


if __name__ == '__main__':
    import shutil
    import doctest

    content_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'content')
    shutil.rmtree(content_dir, ignore_errors=True)
    os.makedirs(content_dir)

    print(doctest.testmod())
