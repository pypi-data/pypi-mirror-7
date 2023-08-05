# -*- coding: UTF-8 -*-
from lisa.server.plugins.IPlugin import IPlugin
import gettext

class {{ plugin_name }}(IPlugin):
    def __init__(self):
        super({{ plugin_name }}, self).__init__()
        self.configuration_plugin = self.mongo.lisa.plugins.find_one({"name": "{{ plugin_name }}"})
        self._ = translation = gettext.translation(domain='{{ plugin_name_lower }}',
                                                   localedir=self.path,
                                                   languages=[self.configuration_lisa['lang']]).ugettext

    def sayHello(self, jsonInput):
        return {"plugin": "{{ plugin_name }}",
                "method": "sayHello",
                "body": self._('Hello. How are you ?')
        }
