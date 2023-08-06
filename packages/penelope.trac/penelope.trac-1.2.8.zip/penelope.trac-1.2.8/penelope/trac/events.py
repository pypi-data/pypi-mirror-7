# -*- coding: utf-8 -*-

from sqlalchemy import event
from penelope.core.models.dashboard import Application
from penelope.core.models.dashboard import modify_application_type, TRAC, SVN
from penelope.trac.populate import add_trac_to_project, add_svn_to_project


def app_insert_listener(mapper, connection, target):

    modify_application_type(mapper, connection, target)

    if not target.api_uri:

        if target.application_type == TRAC:
            add_trac_to_project(target)

        elif target.application_type == SVN:
            add_svn_to_project(target)


event.listen(Application, 'before_insert', app_insert_listener, propagate=True)
