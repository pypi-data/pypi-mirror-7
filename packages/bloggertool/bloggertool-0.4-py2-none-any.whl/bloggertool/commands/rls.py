# commands/rls.py
# Copyright (C) 2011-2014 Andrew Svetlov
# andrew.svetlov@gmail.com
#
# This module is part of BloggerTool and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from textwrap import dedent

from bloggertool.str_util import a
from .basecommand import BaseCommand


class RLsCommand(BaseCommand):
    NAME = 'rls'
    HELP = "Display list of remove posts."
    DESCR = dedent("""\
    Display list of remove posts.
    """)

    @classmethod
    def fill_parser(cls, parser):
        parser.add_argument('-l', '--long', default=False, action='store_true',
                            help="long output format")

    def __init__(self, args):
        self.long = args.long

    def run(self):
        config = self.config

        info = config.info

        if not info.email:
            self.log.error('Set user email first')
            return 1

        srv = info.remote()

        rposts = srv.get_posts()
        out = []
        for rpost in rposts:
            state = "[DRAFT] " if rpost.draft else ''

            ret = a("{state}{rpost.title!q} -> {rpost.link}")
            if self.long:
                labels = ', '.join(sorted(rpost.labels))
                ret += '\n' + a("""
                    blogid: {rpost.blogid}
                    postid: {rpost.postid}
                    published: {rpost.published!t}
                    updated: {rpost.updated!t}
                    labels: {labels}
                    """)
            out.append(ret)

        self.log.info("Remote posts for blog '%s':\n----------\n%s",
                      rposts.title, '\n'.join(out))
