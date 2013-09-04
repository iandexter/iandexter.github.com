#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generates resume from JSON data using Jinja2 templates.
"""

import json
import codecs
import jinja2
import os
import re

__version__ = '0.2'

def objwalk(obj, path = (), memo = None):
    """From http://code.activestate.com/recipes/577982-recursively-walk-python-objects/"""
    from collections import Mapping, Set, Sequence

    string_types = (str, unicode) if str is bytes else (str, bytes)
    iteritems = lambda mapping: getattr(mapping, 'iteritems', mapping.items)()

    if memo is None:
        memo  = set()
    iterator = None
    if isinstance(obj, Mapping):
        iterator = iteritems
    elif isinstance(obj, (Sequence, Set)) and not isinstance(obj, string_types):
        iterator = enumerate
    if iterator:
        if id(obj) not in memo:
            memo.add(id(obj))
            for path_component, value in iterator(obj):
                for result in objwalk(value, path + (path_component,), memo):
                    yield result
            memo.remove(id(obj))
    else:
        yield path, obj

def transform(obj, patt, repl):
    """ From http://stackoverflow.com/questions/11501090/iterate-over-nested-lists-and-dictionaries"""
    regex = re.compile(patt)
    for p, v in objwalk(obj):
        if isinstance(v, basestring):
            if regex.findall(v):
                new_obj = obj
                for s in p[:-1]:
                    new_obj = new_obj[s]
                new_obj[p[-1]] = regex.sub(repl, v)

def load_json(json_file = None):
    return json.load(codecs.open(json_file, 'r', 'utf-8-sig'))

def get_keywords(json_data = None):
    keywords = []
    for k in json_data['overview']['skills']:
        keywords.append(k['area'])
    for k in json_data['overview']['platforms']:
        keywords.append(k['platform'])
    for k in json_data['overview']['languages']:
        keywords.append(k['language'])
    return keywords

def render_resume():
    resume_renderer = jinja2.Environment(
        block_start_string = '%(',
        block_end_string = '%)',
        variable_start_string = '%((',
        variable_end_string = '%))',
        loader = jinja2.FileSystemLoader(os.path.abspath('.')))
    return resume_renderer

if __name__ == '__main__':
    JSON_FILE = 'resume-iandexter.json'
    ftype = 'tex'
    TEMPLATE = "resume.%s.j2" % ftype
    OUTPUT = 'resume-iandexter.%s' % ftype

    resume_data = load_json(JSON_FILE)['resume']
    resume_data[u'keywords'] = get_keywords(resume_data)

    link_marker = '\\[([^\\]]+)\\]\\(([^\\)]+)\\)'
    link_sub = r'\\href{\2}{\1}'
    transform(resume_data, link_marker, link_sub)

    resume_template = render_resume().get_template(TEMPLATE)
    with open(OUTPUT, 'w') as resume:
        resume.write(resume_template.render(resume_data))
