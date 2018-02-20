# -*- coding: utf-8 -*-
"""Adds a wiki macro [[Components(pattern)]] which lists and describes the
project's components, and links to wiki pages describing the components in
more detail, and any tickets for the components.  The optional pattern
parameter is a regex that can be used to filter components.

terry_n_brown@yahoo.com
"""

import inspect
import sys
import re

from trac.core import Component, implements
from trac.wiki.api import IWikiMacroProvider
from trac.wiki import format_to_html
from trac.env import Environment
from trac.env import open_environment

class ComponentsProcessor(Component):
    implements(IWikiMacroProvider)

    # IWikiMacroProvider interface

    def get_macros(self):
        yield 'Components'

    def get_macro_description(self, name):
        return inspect.getdoc(sys.modules.get(self.__module__))

    def expand_macro(self, formatter, name, pattern):
        with self.env.db_query as db:
            cursor = db.cursor()
            cursor.execute("SELECT name, description from component order by name;")

            comps = [comp for comp in cursor]

            # get a distinct list of all components for which there are tickets
            query = "SELECT component from ticket group by component;"
            cursor.execute(query)
            tickets = [page[0] for page in cursor]

            content = []

            for name, descrip in comps:
                if pattern and not re.match(pattern, name): continue

                 # Get number of tickets
                count = 0
                query = "SELECT count(id) FROM ticket WHERE component='%s'" % name
                cursor.execute(query)
                for count, in cursor:
                    break

                p = re.compile(' ')
                wiki_str = p.sub('',name)
                ticket_str = p.sub('+',name)
                dt = ' [wiki:%s %s]' % (wiki_str, name)
                if name in tickets:
                    dt += ' ([query:component=%s %d tickets])' % (ticket_str.replace('&','\&'), count)
                dt += '::'
                content.append(dt)
                if descrip != None and descrip.strip() != '':
                    content.append('   %s' % descrip)

            content = '\n'.join(content)
            content = format_to_html(self.env, formatter.context, content)
            p = re.compile('%2B')
            content = p.sub('+',content)
            content = '<div class="component-list">%s</div>' % content
            return content
