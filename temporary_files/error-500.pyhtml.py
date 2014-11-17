# -*- coding:ascii -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1416265738.1316004
_enable_loop = True
_template_filename = '/root/tpm-server/error-500.pyhtml'
_template_uri = 'error-500.pyhtml'
_source_encoding = 'ascii'
_exports = []



import cgi, traceback


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        bool = context.get('bool', UNDEFINED)
        int = context.get('int', UNDEFINED)
        kargs = context.get('kargs', UNDEFINED)
        config = context.get('config', UNDEFINED)
        __M_writer = context.writer()
        __M_writer('\n<!doctype html>\n<html>\n\t<head>\n\t\t<script src="https://code.jquery.com/jquery-2.1.1.min.js"></script>\n\t\t<link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.1/css/bootstrap.min.css" rel="stylesheet">\n\t\t<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.1/css/bootstrap-theme.min.css">\n\t\t<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.1/js/bootstrap.min.js"></script>\n\t\t<title>TPM Package Database</title>\n\t</head>\n\t<body style="background-color: #E4DDCA;">\n\t\t<nav class="navbar navbar-default navbar-sticky-top" role="navigation">\n\t\t\t<div class="navbar-header">\n\t\t\t\t<a class="navbar-brand" style="font-size:large" href="/">TPM Package Database</a>\n\t\t\t</div>\n\t\t\t<div>\n\t\t\t\t<ul class="nav navbar-nav">\n\t\t\t\t\t<li><a href="#search">Search</a></li>\n\t\t\t\t\t<!--<button class="btn btn-default dropdown-toggle" type="button" id="dropdownMenu1" data-toggle="dropdown">\n\t\t\t\t\tSign in\n\t\t\t\t\t</button>-->\n\t\t\t\t</ul>\n\t\t\t</div>\n\t\t</nav>\n\n\t\t<div style="background-color:#f8f8f8; padding:30px; position:relative; margin-left:auto; margin-right:auto; width:80%" class="container-fluid">\n\t\t\t<h2>500 error</h2>\n\t\t\t<h3>The server encountered an error processing your request</h3>\n\t\t\t')

        try:
                x = kargs['error_string'].replace("\n","<br />")
        except:
                x = traceback.format_exc()
                                
        
        __M_locals_builtin_stored = __M_locals_builtin()
        __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['x'] if __M_key in __M_locals_builtin_stored]))
        __M_writer('\n')
        if bool(int(config.get("general","show_stack_trace_on_error"))):
            __M_writer('\t\t\t\t')
            __M_writer(str(x))
            __M_writer('\n')
        __M_writer('\t\t\t<br />\n\t\t\tPlease email the administrator of the server <a href="mailto:')
        __M_writer(str(cgi.escape(config.get("general","email"))))
        __M_writer('">here</a>\n\t\t</div>\n\t</body>\n</html>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"line_map": {"51": 45, "38": 36, "39": 37, "40": 38, "41": 38, "42": 38, "43": 40, "44": 41, "45": 41, "15": 1, "19": 0, "28": 3, "29": 31}, "source_encoding": "ascii", "filename": "/root/tpm-server/error-500.pyhtml", "uri": "error-500.pyhtml"}
__M_END_METADATA
"""
