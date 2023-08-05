#!/usr/bin/env python
#
# -*- mode:python; sh-basic-offset:4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim:set tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8:
#

import bottle
from bottle import template
from bottle.ext import sqlalchemy as sqlaplugin
import hashlib
import IPy
import model
import os
import pasttle
import pygments
from pygments import formatters
from pygments import lexers
import sys
import util


application = bottle.app()

# Load an alternate template directory if specified in pasttle.ini
STATIC_CONTENT = None
if util.conf.has_option(util.cfg_section, 'templates'):
    tpl_path = util.conf.get(util.cfg_section, 'templates')
    tpl_path = os.path.expanduser(tpl_path)
    bottle.TEMPLATE_PATH.append(os.path.realpath(tpl_path))
    STATIC_CONTENT = tpl_path

# Load the templates shipped with the package
tpl_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'views')
STATIC_CONTENT = STATIC_CONTENT or tpl_path
bottle.TEMPLATE_PATH.append(tpl_path)

# Install sqlalchemy plugin
db_plugin = sqlaplugin.SQLAlchemyPlugin(
    model.engine, model.Base.metadata, create=True
)

application.install(db_plugin)


def get_url(path=False):
    (scheme, host, q_path, qs, fragment) = bottle.request.urlparts
    if path:
        return u'%s://%s%s' % (scheme, host, q_path)
    else:
        return u'%s://%s' % (scheme, host)


@bottle.get('/')
@bottle.view('index')
def index():
    """
    Main index
    """

    return dict(
        url=get_url(),
        title=util.conf.get(util.cfg_section, 'title'),
        version=pasttle.__version__,
    )


@bottle.get('/<filetype:re:(css|images)>/<path:path>')
def serve_static(filetype, path):
    "Serve static files if not configured on the web server"

    return bottle.static_file(os.path.join(filetype, path), STATIC_CONTENT)


@bottle.get('/favicon.ico')
def serve_icon():
    return serve_static('images', 'icon.png')


@bottle.get('/recent')
def recent(db):
    """
    Shows an unordered list of most recent pasted items
    """

    return template(
        'recent', dict(
            pastes=db.query(
                model.Paste.id, model.Paste.filename, model.Paste.mimetype,
                model.Paste.created, model.Paste.password
            ).order_by(
                model.Paste.id.desc()
            ).limit(20).all(),
            url=get_url(),
            title=util.conf.get(util.cfg_section, 'title'),
            version=pasttle.__version__,
        )
    )


@bottle.get('/post')
@bottle.view('post')
def upload_file():
    """
    Frontend for simple posting via web interface
    """
    return dict(
        title=u'Paste New', content=u'', password=u'',
        checked=u'', syntax=u'', url=get_url(),
    )


@bottle.post('/post')
def post(db):
    """
    Main upload interface. Users can password-protect an entry if they so
    desire. You can send an already SHA1 cyphered text to this endpoint so
    your intended password does not fly insecure through the internet
    """

    upload = bottle.request.forms.upload
    filename = None
    if bottle.request.forms.filename != '-':
        filename = bottle.request.forms.filename
    syntax = None
    if bottle.request.forms.syntax != '-':
        syntax = bottle.request.forms.syntax
    password = bottle.request.forms.password
    encrypt = not bool(bottle.request.forms.is_encrypted)
    redirect = bool(bottle.request.forms.redirect)
    util.log.debug('Filename: %s, Syntax: %s' % (filename, syntax,))
    default_lexer = lexers.get_lexer_for_mimetype('text/plain')
    if upload:
        if syntax:
            util.log.debug('Guessing lexer for explicit syntax %s' % (syntax,))
            try:
                lexer = lexers.get_lexer_by_name(syntax)
            except lexers.ClassNotFound:
                lexer = default_lexer
        else:
            if filename:
                util.log.debug('Guessing lexer for filename %s' % (filename,))
                try:
                    lexer = lexers.guess_lexer_for_filename(filename, upload)
                except lexers.ClassNotFound:
                    lexer = lexers.guess_lexer(upload)
            else:
                util.log.debug('Best guess of lexer based on content')
                try:
                    lexer = lexers.guess_lexer(upload)
                    util.log.debug(lexer)
                except lexers.ClassNotFound:
                    lexer = default_lexer
        util.log.debug(lexer.mimetypes)
        lx = None
        if lexer.mimetypes:
            mime = lexer.mimetypes[0]
        else:
            if lexer.aliases:
                lx = lexer.aliases[0]
            mime = u'text/plain'
        ip = bottle.request.remote_addr
        if ip:
            # Try not to store crap in the database if it's not a valid IP
            try:
                ip = bin(IPy.IP(ip).int())
            except Exception as ex:
                util.log.warn(
                    'Impossible to store the source IP address: %s' % (ex,)
                )
                ip = None
        paste = model.Paste(
            content=upload, mimetype=mime, encrypt=encrypt,
            password=password, ip=ip, filename=filename,
            lexer=lx
        )
        util.log.debug(paste)
        db.add(paste)
        db.commit()
        if redirect:
            bottle.redirect('%s/%s' % (get_url(), paste.id, ))
        else:
            return u'%s/%s' % (get_url(), paste.id, )
    else:
        return bottle.HTTPError(400, output='No paste provided')


def _get_paste(db, id):
    """
    Queries the database for the given paste, or returns False is not found
    """

    try:
        paste = db.query(model.Paste).filter_by(id=id).one()
    except:
        paste = None
    return paste


def _pygmentize(paste, lang):
    """
    Guess (or force if lang is given) highlight on a given paste via pygments
    """

    util.log.debug(paste)
    if lang:
        try:
            lexer = lexers.get_lexer_by_name(lang)
        except lexers.ClassNotFound:
            lexer = lexers.get_lexer_by_name('text')
    else:
        try:
            util.log.debug(paste.lexer)
            lexer = lexers.get_lexer_by_name(paste.lexer)
            util.log.debug(lexer)
        except lexers.ClassNotFound:
            lexer = lexers.get_lexer_for_mimetype(paste.mimetype)
    util.log.debug('Lexer is %s' % (lexer,))
    a = '<small><a href="/edit/%s">edit as new paste</a></small>' % (paste.id,)
    if paste.ip:
        ip = IPy.IP(long(paste.ip, 2))
        util.log.debug('Originally pasted from %s' % (ip,))
    if paste.filename:
        title = u'%s, created on %s' % (paste.filename, paste.created, )
    else:
        title = u'created on %s' % (paste.created, )
    title = '%s %s (%s)' % (paste.mimetype, title, a,)
    util.log.debug(lexer)
    return pygments.highlight(
        paste.content, lexer, formatters.HtmlFormatter(
            full=True, linenos='table',
            encoding='utf-8', lineanchors='ln', title=title)
        )


@bottle.get('/<id:int>')
@bottle.post('/<id:int>')
def showpaste(db, id, lang=None):
    """
    Shows the highlighted entry on the browser. If the entry is protected
    with a password it will display a password entry and will compare against
    the database for a match
    """

    paste = _get_paste(db, id)
    if not paste:
        return bottle.HTTPError(404, output='This paste does not exist')
    password = bottle.request.forms.password
    util.log.debug(
        '%s == %s ? %s' % (
            hashlib.sha1(password).hexdigest(), paste.password,
            hashlib.sha1(password).hexdigest() == paste.password,
        )
    )
    if paste.password:
        if not password:
            return template('password_protect')
        if hashlib.sha1(password).hexdigest() == paste.password:
            bottle.response.content_type = 'text/html'
            return _pygmentize(paste, lang)
        else:
            return bottle.HTTPError(401, output='Wrong password provided')
    else:
        return _pygmentize(paste, lang)


@bottle.get('/<id:int>/<lang>')
@bottle.post('/<id:int>/<lang>')
def forcehighlight(db, id, lang):
    """Forces a certain highlight against an entry"""

    return showpaste(db, id, lang)


@bottle.get('/raw/<id:int>')
@bottle.post('/raw/<id:int>')
def showraw(db, id):
    """
    Returns the plain-text version of the entry. If the entry is protected
    with a password it will display a simple password entry form until the
    password is a match in the database
    """

    paste = _get_paste(db, id)
    if not paste:
        return bottle.HTTPError(404, output='This paste does not exist')
    password = bottle.request.forms.password
    is_encrypted = bool(bottle.request.forms.is_encrypted)
    if not is_encrypted:
        match = hashlib.sha1(password).hexdigest()
    else:
        match = password
    util.log.debug(
        '%s == %s ? %s' % (match, paste.password, match == paste.password, )
    )
    if paste.password:
        if not password:
            return template('password_protect')
        if match == paste.password:
            bottle.response.content_type = 'text/plain'
            return paste.content
        else:
            return bottle.HTTPError(401, output='Wrong password provided')
    else:
        bottle.response.content_type = 'text/plain'
        return paste.content


@bottle.post('/edit/<id:int>')
@bottle.get('/edit/<id:int>')
def edit(db, id):
    """
    Edits the entry. If the entry is protected with a password it will display
    a simple password entry form until the password is a match in the database
    """

    paste = _get_paste(db, id)
    if not paste:
        return bottle.HTTPError(404, output='This paste does not exist')
    password = bottle.request.forms.password
    is_encrypted = bool(bottle.request.forms.is_encrypted)
    if not is_encrypted:
        match = hashlib.sha1(password).hexdigest()
    else:
        match = password
    util.log.debug(
        '%s == %s ? %s' % (
            match, paste.password,
            match == paste.password,
        )
    )

    post_args = dict(
        title='Edit entry #%s' % (paste.id),
        password=paste.password or u'',
        content=paste.content,
        checked=u'',
        syntax=lexers.get_lexer_for_mimetype(paste.mimetype).aliases[0],
        url=get_url(),
    )

    if paste.password:
        if not password:
            return template('password_protect')
        if match == paste.password:
            post_args['checked'] = 'checked'
            return template('post', post_args)
        else:
            return bottle.HTTPError(401, output='Wrong password provided')
    else:
        return template('post', post_args)


def main():
    util.log.info('Using Python %s' % (sys.version, ))
    bottle.run(
        application, host=util.conf.get(util.cfg_section, 'bind'),
        port=util.conf.getint(util.cfg_section, 'port'),
        reloader=util.is_debug,
        server=util.conf.get(util.cfg_section, 'wsgi')
    )

if __name__ == '__main__':
    sys.exit(main())
