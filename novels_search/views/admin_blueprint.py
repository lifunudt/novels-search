#!/usr/bin/env python
from sanic import Blueprint
from sanic.response import html, redirect
from jinja2 import Environment, PackageLoader, select_autoescape
from urllib.parse import urlparse, parse_qs

from novels_search.database.mongodb import MotorBase
from novels_search.config import LOGGER

admin_bp = Blueprint('admin_blueprint', url_prefix='admin')
admin_bp.static('/static', './static/novels')

# jinjia2 config
env = Environment(
    loader=PackageLoader('views.novels_blueprint', '../templates/novels'),
    autoescape=select_autoescape(['html', 'xml', 'tpl']))


def template(tpl, **kwargs):
    template = env.get_template(tpl)
    return html(template.render(kwargs))


@admin_bp.route("/bookmarks")
async def bookmarks(request):
    user = request['session'].get('user', None)
    if user:
        motor_db = MotorBase().db
        try:
            data = await motor_db.user_message.find_one({'user': user})
            if data:
                bookmarks = data.get('bookmarks', None)
                if bookmarks:
                    result = []
                    index = 0
                    for i in bookmarks:
                        item_result = {}
                        index += 1
                        bookmark = i.get('bookmark', None)
                        query = parse_qs(urlparse(bookmark).query)
                        item_result['index'] = index
                        item_result['novels_name'] = query.get('novels_name', '')[0] if query.get('novels_name',
                                                                                                  '') else ''
                        item_result['chapter_name'] = query.get('name', '')[0] if query.get('name', '') else ''
                        item_result['chapter_url'] = query.get('chapter_url', '')[0] if query.get('chapter_url',
                                                                                                  '') else ''
                        item_result['bookmark'] = bookmark
                        item_result['add_time'] = i.get('add_time', '')
                        result.append(item_result)
                    return template('admin_bookmarks.html', title='{user}的书签 - owllook'.format(user=user),
                                    is_login=1,
                                    user=user,
                                    is_bookmark=1,
                                    result=result)
            return template('admin_bookmarks.html', title='{user}的书签 - owllook'.format(user=user),
                            is_login=1,
                            user=user,
                            is_bookmark=0)
        except Exception as e:
            LOGGER.error(e)
    else:
        return redirect('/')


@admin_bp.route("/books")
async def books(request):
    user = request['session'].get('user', None)
    if user:
        motor_db = MotorBase().db
        try:
            data = await motor_db.user_message.find_one({'user': user})
            if data:
                books_url = data.get('books_url', None)
                if books_url:
                    result = []
                    for i in books_url:
                        item_result = {}
                        book_url = i.get('book_url', None)
                        query = parse_qs(urlparse(book_url).query)
                        item_result['novels_name'] = query.get('novels_name', '')[0] if query.get('novels_name',
                                                                                                  '') else ''
                        item_result['book_url'] = book_url
                        item_result['add_time'] = i.get('add_time', '')
                        result.append(item_result)
                    return template('admin_books.html', title='{user}的书架 - owllook'.format(user=user),
                                    is_login=1,
                                    user=user,
                                    is_bookmark=1,
                                    result=result[::-1])
            return template('admin_books.html', title='{user}的书架 - owllook'.format(user=user),
                            is_login=1,
                            user=user,
                            is_bookmark=0)
        except Exception as e:
            LOGGER.error(e)
    else:
        return redirect('/')
