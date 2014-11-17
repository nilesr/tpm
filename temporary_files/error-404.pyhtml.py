# -*- coding:ascii -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1416266428.4943862
_enable_loop = True
_template_filename = '/root/tpm-server/error-404.pyhtml'
_template_uri = 'error-404.pyhtml'
_source_encoding = 'ascii'
_exports = []



import cgi


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        config = context.get('config', UNDEFINED)
        filename = context.get('filename', UNDEFINED)
        __M_writer = context.writer()
        __M_writer('\n<!doctype html>\n<html>\n\t<head>\n\t\t<script src="https://code.jquery.com/jquery-2.1.1.min.js"></script>\n\t\t<link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.1/css/bootstrap.min.css" rel="stylesheet">\n\t\t<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.1/css/bootstrap-theme.min.css">\n\t\t<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.1/js/bootstrap.min.js"></script>\n\t\t<title>TPM Package Database</title>\n\t</head>\n\t<body style="background-color: #E4DDCA;">\n\t\t<nav class="navbar navbar-default navbar-sticky-top" role="navigation">\n\t\t\t<div class="navbar-header">\n\t\t\t\t<a class="navbar-brand" style="font-size:large" href="/">TPM Package Database</a>\n\t\t\t</div>\n\t\t\t<div>\n\t\t\t\t<ul class="nav navbar-nav">\n\t\t\t\t\t<li><a href="#search">Search</a></li>\n\t\t\t\t\t<!--<button class="btn btn-default dropdown-toggle" type="button" id="dropdownMenu1" data-toggle="dropdown">\n\t\t\t\t\tSign in\n\t\t\t\t\t</button>-->\n\t\t\t\t</ul>\n\t\t\t</div>\n\t\t</nav>\n\n\t\t<div style="background-color:#f8f8f8; padding:30px; position:relative; margin-left:auto; margin-right:auto; width:80%" class="container-fluid">\n\t\t\t<h2>404 error</h2>\n\t\t\t<h3>The file <span style="background-color:lightgrey;border:1px solid grey;border-radius:4px;">')
        __M_writer(str(cgi.escape(filename)))
        __M_writer('</span> could not be found</h3>\n\t\t\tPlease report a broken link to whoever led you here, or if you think this page should exist, report it to the owner <a href="mailto:')
        __M_writer(str(cgi.escape(config.get("general","email"))))
        __M_writer('">here</a>\n\t\t</div>\n\t</body>\n</html>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"uri": "error-404.pyhtml", "filename": "/root/tpm-server/error-404.pyhtml", "line_map": {"19": 0, "36": 30, "26": 3, "27": 30, "28": 30, "29": 31, "30": 31, "15": 1}, "source_encoding": "ascii"}
__M_END_METADATA
"""
