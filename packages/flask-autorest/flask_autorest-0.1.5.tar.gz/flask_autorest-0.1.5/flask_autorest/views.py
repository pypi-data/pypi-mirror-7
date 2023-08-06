# -*- coding: utf-8 -*-

from math import ceil
import datetime
from flask.views import MethodView
from flask import abort, request, current_app
import dataset
from . import constants
from .utils import autorest_jsonify


class AutoRestMethodView(MethodView):

    def __init__(self, autorest, db_name, db_conf):
        super(AutoRestMethodView, self).__init__()
        self.autorest = autorest
        self.db_name = db_name
        self.db_conf = db_conf

    def get_tb(self, tb_name):
        tb_conf = self.db_conf['tables'].get(tb_name)

        if tb_conf is None:
            # 说明不存在
            return None, None, None

        uri = self.db_conf['uri']
        db = self.autorest.databases.get(self.db_name)
        if not db:
            try:
                self.autorest.db_alloc_lock.acquire()
                db = self.autorest.databases.get(self.db_name)
                if not db:
                    db = self.autorest.databases[self.db_name] = dataset.connect(
                        uri,
                        engine_kwargs=self.db_conf.get('engine_kwargs')
                    )
            finally:
                self.autorest.db_alloc_lock.release()

        if tb_name not in db.tables and \
           not tb_conf.get('auto_fix', constants.DEFAULT_AUTO_FIX_TABLE):
            return None, None, None

        tb = db[tb_name]
        pk_name = tb.table.primary_key.columns.values()[0].name
        return tb, pk_name, tb_conf

    def dispatch_request(self, *args, **kwargs):
        auth_conf = self.db_conf.get('auth')
        if auth_conf:
            if not request.authorization or \
                            (request.authorization.username, request.authorization.password) != tuple(auth_conf):
                # 权限验证失败
                abort(403)
                return

        return super(AutoRestMethodView, self).dispatch_request(*args, **kwargs)


class ResourceView(AutoRestMethodView):
    """
    /resource/<id>
    """
    def get(self, tb_name, pk):
        tb, pk_name, tb_conf = self.get_tb(tb_name)
        if tb is None or pk_name is None:
            abort(403)
            return

        kwargs = {
            pk_name: pk
        }

        obj = tb.find_one(**kwargs)
        if not obj:
            abort(404)
            return
        return autorest_jsonify(
            **obj
        )

    def patch(self, tb_name, pk):
        json_data = request.get_json(force=True)

        tb, pk_name, tb_conf = self.get_tb(tb_name)
        if tb is None or pk_name is None:
            abort(403)
            return

        auto_fix_table = tb_conf.get('auto_fix', constants.DEFAULT_AUTO_FIX_TABLE)

        json_data.update({
            pk_name: pk
        })

        tb.update(json_data, [pk_name], ensure=auto_fix_table)

        kwargs = {
            pk_name: pk
        }

        obj = tb.find_one(**kwargs)
        if not obj:
            abort(404)
            return
        return autorest_jsonify(
            **obj
        )

    put = patch

    def delete(self, tb_name, pk):
        tb, pk_name, tb_conf = self.get_tb(tb_name)
        if tb is None or pk_name is None:
            abort(403)
            return

        kwargs = {
            pk_name: pk
        }

        tb.delete(**kwargs)

        return current_app.response_class(status=204)


class ResourceListView(AutoRestMethodView):
    """
    /resource/
    """

    def options(self, tb_name):
        tb, pk_name, tb_conf = self.get_tb(tb_name)
        if tb is None or pk_name is None:
            abort(403)
            return

        return autorest_jsonify(
            columns=tb.columns
        )

    def get(self, tb_name):
        tb, pk_name, tb_conf = self.get_tb(tb_name)
        if tb is None or pk_name is None:
            abort(403)
            return

        conf_per_page = self.db_conf['tables'][tb_name].get('per_page') or constants.DEFAULT_PER_PAGE
        conf_max_per_page = self.db_conf['tables'][tb_name].get('max_per_page', constants.DEFAULT_MAX_PER_PAGE)

        page = request.args.get('page', type=int) or 1
        per_page = request.args.get('per_page', type=int)

        if not per_page:
            per_page = conf_per_page

        if per_page > conf_max_per_page > 0:
            per_page = conf_max_per_page

        total = len(tb)
        pages = int(ceil(total / float(per_page)))

        obj_list = tb.find(_limit=per_page, _offset=(page-1)*per_page)
        json_obj_list = [obj for obj in obj_list]

        return autorest_jsonify(
            total=total,
            pages=pages,
            page=page,
            per_page=per_page,
            objects=json_obj_list
        )

    def post(self, tb_name):
        json_data = request.get_json(force=True)

        tb, pk_name, tb_conf = self.get_tb(tb_name)
        if tb is None or pk_name is None:
            abort(403)
            return

        auto_fix_table = tb_conf.get('auto_fix', constants.DEFAULT_AUTO_FIX_TABLE)

        pk = tb.insert(json_data, ensure=auto_fix_table)

        kwargs = {
            pk_name: pk
        }

        obj = tb.find_one(**kwargs)
        if not obj:
            abort(404)
            return
        return autorest_jsonify(
            **obj
        )
