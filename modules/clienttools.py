#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
   Client Tools for web2py 
   Developed by Nathan Freeze (Copyright © 2009)
   Email <nathan@freezable.com>
   License: GPL v2
   
   This file contains tools for managing client events 
   scripts and resources from the server in web2py
"""

import urllib
import os
import string

from gluon.contrib.simplejson import dumps
from gluon.html import *
from gluon.http import *
from gluon.validators import *
from gluon.sqlhtml import *

__all__ = ['PageManager','EventManager', 'ScriptManager', 'JQuery']

__events__ = ['blur', 'focus', 'load', 'resize', 'scroll', 'unload', 
                 'beforeunload', 'click', 'dblclick',  'mousedown', 
                 'mouseup', 'mousemove', 'mouseover', 'mouseout', 
                 'mouseenter', 'mouseleave', 'change', 'select',
                 'submit', 'keydown', 'keypress', 'keyup', 'error']

__events_live_unsupported__ = ['blur', 'focus', 'mouseenter', 
                               'mouseleave', 'change', 'submit']

__scripts__ = ['alert','delay','confirm','timer','stop_timer',
               'call_function','load','get_script','get_json','function','var','jQuery']

def valid_filename(filename):
    import string
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return ''.join(c for c in filename if c in valid_chars)

def get_selector(c):
    if not c: return ""
    if hasattr(c,'tag'):
        if c['_id']:
            return '"#%s"' % c['_id']   
        if c['_name']:
            return '"%s[name=\'%s\']"' % (c.tag.replace("/",""), c['_name'])          
        raise ValueError('Invalid component. No id or name attribute')
    if c.startswith("document") or c=="this": return c
    c = c.replace('"',"'")
    return '"%s"' % c  

def get_url(req, function, args):
    if not isinstance(function, str):        
        if not hasattr(function, '__call__'):
            raise TypeError('Invalid function for url. Object is not callable')
        return URL(r=req,f=function.__name__, args=args) \
                  if args else URL(r=req,f=function.__name__)
    return function

def is_script(cmd):
    if cmd.startswith("_"):
            return True
    for s in __scripts__:
        if cmd.startswith(s): return True
    return False

def get_data_fn(val):
    if isinstance(val, JQuery): return str(val)
    if isinstance(val, str):
        if val.startswith('jQuery'): 
            return val
        if val.startswith("_"):
            return  '"%s="+%s' %(val[1:],val)
    val = get_selector(val)
    return 'jQuery(%s).serialize()' % val

class PageManager(object):
    """
    The page manager object is used to dynamically
    include resources on a page
    
    include - downloads a resource and/or adds a 
              reference to it on the page              
    google_load - adds a reference to a google hosted library
                  example: page.google_load("jqueryui","1.7.2")
                  more here: http://code.google.com/apis/ajaxlibs/                  
    ready - adds a script to the jQuery(document).ready function    
    render - returns the page manager output for views    
    """
    def __init__(self, environment):
        self.environment = Storage(environment)        
        self.resources = []
        self.onready = []
        
    def include(self, path, download=False, filename=None,
                overwrite=False, subfolder=None):       
        request = self.environment.request
        out = path        
        if hasattr(path, 'xml'):
            out = path.xml()
        if download and path.startswith("http://"):                     
            if not request.env.web2py_runtime_gae:                
                if not filename:
                    filename = valid_filename(path.split("/")[-1])
                if len(filename):                    
                    pieces = (request.folder, 'static', subfolder)
                    fld = os.path.join(*(x for x in pieces if x))
                    if not os.path.exists(fld): os.mkdir(fld)
                    fpath = os.path.join(fld,filename)
                    exists = os.path.exists(fpath)
                    if (not exists) or (exists and overwrite):            
                        urllib.urlretrieve(path, fpath)
                    out = URL(r=request,c='/'.join(
                          x for x in ['static', subfolder] if x),f=filename)                 
        self.resources.append(out)
        
    def google_load(self, lib, version):
        gsapi = '<script src="http://www.google.com/jsapi"></script>'
        if not gsapi in self.resources:
            self.include(gsapi)
        self.include('<script type="text/javascript">google.load("%s", "%s");</script>' % \
                      (lib,version))
        
    def ready(self, script):
        if isinstance(script, SCRIPT):
            self.onready.append(script.xml())
        elif isinstance(script, str):
            self.onready.append(script) 
        else:
            raise ValueError("Invalid script for ready function. Must be string or SCRIPT.") 
            
    def render(self):
        out = ''
        for r in self.resources:
            if r.endswith(".js"):
                out += "<script type=\"text/javascript\" src=\"%s\"></script>" % r
            elif r.endswith(".css"):
                out += LINK(_href=r,_rel="stylesheet", _type="text/css").xml()
            else:
                out += r
        if len(self.onready):
            inner = "\n  ".join(s for s in self.onready)
            out += "<script type=\"text/javascript\">function page_onready(){\n  " + \
             inner + "\n}\njQuery(document).ready(page_onready);</script>"         
        
        return XML(out)

class EventManager(object):
    """
    The event manager allows you to bind client
    side events to client or server side functions.
    
    example: div = DIV('Click me',_id="clickme")
             event.listen('click',div,handle_it, "alert('Clicked!');")
             event.listen('blur',"#test", handle_it, div)
             
    requires an instance of PageManager             
    """
    def __init__(self, page_manager):
        self.events = []
        self.page_manager = page_manager
        self.environment = page_manager.environment  
              
    def listen(self, event, target, handler, success="eval(msg);", data='form:first', 
               args=None, on_error="" ,persist=False, event_args=False):
        if not event in __events__:            
            raise ValueError('Invalid event name.')
        if persist and event in __events_live_unsupported__:
            raise ValueError('Invalid event name. Unsupported persistent event.')
        bind = 'live' if persist else 'bind'  
        target = get_selector(target)
        if success != "eval(msg);":
            success = 'jQuery(%s).html(msg);' % get_selector(success)        
        data = get_data_fn(data)                             
        if not isinstance(handler, str):        
            url = get_url(self.environment.request,handler, args=args)
            e = '"event_target_id=" + encodeURIComponent(e.target.id) + "&event_target_html=" + '\
                'encodeURIComponent(jQuery(e.target).wrap("<div></div>").parent().html()) + '\
                '"&event_pageX=" + e.pageX + "&event_pageY=" + e.pageY + '\
                '"&event_timeStamp=" + e.timeStamp + "&"' if event_args else '""'
            handler = 'jQuery.ajax({type:"POST",url:"%s",data:%s + %s,'\
                      'success: function(msg){%s}, error: function(request,textStatus,errorThrown){%s} });' \
                        % (url, e, data, success, on_error)                   
        self.events.append([event, target, handler, data])        
        self.page_manager.onready.append('jQuery(%s).%s("%s", function(e){%s});' % 
                                         (target, bind, event, handler))
        
    def trigger(self, event, target, data=None):
        if not event in __events__:            
            raise ValueError('Invalid event name.') 
        target = get_selector(target)               
        return 'jQuery(%s).trigger("%s"%s);' % (target,event,"," + str(data) if data else "")
        
class ScriptManager(object):
    """
    Helpers to generate scripts
    All methods return a string
              
    example: page = PageManager(globals())
             scripts = Scripts(page)
             page.ready(scripts.call_function(function, data, success))
    """
    def __init__(self, page_manager):
        self.page_manager = page_manager
        self.environment = page_manager.environment
        
    def alert(self,message, unquote=False):
        if is_script(message): unquote = True
        if unquote: return 'alert(%s);' % message 
        return 'alert("%s");' %  message
    
    def confirm(self,message, if_ok, if_cancel=''):
        return 'var c = confirm("%s");if(c==true){%s}else{%s}' % \
               (message, if_ok, if_cancel)
               
    def prompt(self,message,default, if_ok, if_cancel='',var="reply"):
        return 'var _%s = prompt("%s","%s");if(%s != null){%s}else{%s}' % \
               (var, message, default, var ,if_ok, if_cancel)
    
    def delay(self, function, timeout):
        return 'setTimeout(\'%s\',%s);' % (function,timeout)
        
    def timer(self, function, interval=10000, append_to="form:first"):
        append_to = get_selector(append_to)
        return 'var timer_id = setInterval(\'%s\',%s);jQuery(%s).'\
               'append("<input name=\'timer_id\' type=\'hidden\' value=\'" + timer_id + "\'/>");' % \
                (function, interval, append_to)
                
    def stop_timer(self, timer_id):
        return 'clearTimeout(%s);jQuery("input[name=\'timer_id\']").remove();' % timer_id 
    
    def call_function(self, function, success="eval(msg);", 
                      data="form:first", extra="", args=None, on_error=""):
        if success != "eval(msg);":
            success = 'jQuery(%s).html(msg);' % get_selector(success)             
        function = get_url(self.environment.request,function,args)
        data = get_data_fn(data) 
        return 'jQuery.ajax({type:"POST",url:"%s",data: %s + "&%s",'\
               'success: function(msg){%s}, error: function(request,textStatus,errorThrown){%s} });'  % \
                       (function, data, extra, success, on_error) 
                      
    def load(self, function, target, data=dict(), callback="", args=None):
        target = get_selector(target)
        if not isinstance(function, str):        
            if not hasattr(function, '__call__'):
                raise TypeError('Invalid function. Object is not callable')
            function = URL(r=self.environment.request,f=function.__name__, args=args) \
                  if args else URL(r=self.environment.request,f=function.__name__)
        return 'jQuery("%s").load("%s", %s, function(){%s});'  % (target, function, data, callback) 
    
    def get_script(self, url, success=""):
        return 'jQuery.getScript("%s",function(){%s});' % (url,success)
    
    def get_json(self, url, data=dict(), success=""):
        return 'jQuery.getJSON("%s", %s, function(json){%s});' % (url, str(data), success)
    
    def function(self, name,args=[],body=''):
        if type(args)==type([]):
            args = ", ".join(args)      
        return 'function %s(%s){%s}' % (name, args, body)

    def var(self, name, value=None, unquote=False):
        if not isinstance(name,dict):
            if not value: return "_" + name
            name = dict(name=value)
        out = []
        for k,v in name.items():
           if isinstance(v,str) and not unquote: v = "'%s'" % v
           out.append('var _%s %s;' % (k, "= " + str(v) if v else ""))
        return "".join(out)       
    
class JQuery:
    def __init__(self,name=None,attr=None,*args):
        self.name=name        
        self.attr=attr
        if self.attr:
            if self.attr.startswith('_'):
                self.attr = self.attr[1:]        
        else:
            if not isinstance(self.name,JQuery):
                 self.name = get_selector(self.name)
        self.args=args 
    def __str__(self):        
        def encode(obj):
            if isinstance(obj,JQuery): return str(obj)
            if isinstance(obj,str):
                if is_script(obj):return obj
            if hasattr(obj, "xml"):
                    return dumps(obj.xml().replace('"',"'"))
            return dumps(obj).replace("'",'"')
        if not self.name:
            return 'jQuery'
        if not self.attr:                        
            return 'jQuery(%s)' % self.name        
        args=', '.join([encode(a) for a in self.args])
        return '%s.%s(%s)' % (self.name, self.attr, args)
    def __repr__(self):
        return str(self)
    def __nonzero__(self):
        return True
    def xml(self):
        raise AttributeError
    def __getattr__(self,attr):
        def f(*args):
            return JQuery(self,attr,*args)
        return f
    def __call__(self,*args):
        if not args:
            jq = str(JQuery(self))       
            return jq[7:-1] + ";"
    def __coerce__(self, other):
        return (str(self),str(other))
       


