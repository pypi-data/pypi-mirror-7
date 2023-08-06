# -*- coding: utf-8 -*-

from .callbacks_mixin import BlueprintCallBacksMixin


class Blueprint(BlueprintCallBacksMixin):

    app = None

    def register2app(self, app):
        """
        注册到app上
        """
        self.app = app
        # 注册上
        self.app.blueprints.append(self)
