"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
try:
    from qgis.core import Qgis
except ImportError:
    from qgis.core import QGis as Qgis

if Qgis.QGIS_VERSION_INT < 29900:
    from qgis.PyQt.QtGui import QStringListModel
else:
    from qgis.PyQt.QtCore import QStringListModel

from ui_manager import DupPsector
from functools import partial

from .. import utils_giswater
from .parent_manage import ParentManage



class DuplicatePsector(ParentManage):

    def __init__(self, iface, settings, controller, plugin_dir):
        """ Class to control 'Workcat end' of toolbar 'edit' """
        ParentManage.__init__(self, iface, settings, controller, plugin_dir)


    def manage_duplicate_psector(self):

        # Create the dialog and signals
        self.dlg_duplicate_psector = DupPsector()
        self.load_settings(self.dlg_duplicate_psector)

        # Populate combo duplicate psector
        sql = ('SELECT psector_id as id, name as id_val FROM plan_psector')
        rows = self.controller.get_rows(sql)

        utils_giswater.set_item_data(self.dlg_duplicate_psector.duplicate_psector, rows, 1)

        # Set listeners
        self.dlg_duplicate_psector.btn_cancel.clicked.connect(partial(self.close_dialog, self.dlg_duplicate_psector))
        self.dlg_duplicate_psector.btn_accept.clicked.connect(partial(self.duplicate_psector))

        # Open dialog
        self.open_dialog(self.dlg_duplicate_psector)


    def duplicate_psector(self):
        id_psector = utils_giswater.get_item_data(self.dlg_duplicate_psector, self.dlg_duplicate_psector.duplicate_psector, 0)
        new_psector_name = utils_giswater.getWidgetText(self.dlg_duplicate_psector,
                                                        self.dlg_duplicate_psector.new_psector_name)

        # Create body
        feature = '"type":"PSECTOR"'
        extras = '"psector_id":"' + str(id_psector) + '", "new_psector_name":"' + str(new_psector_name) + '"'
        body = self.create_body(feature=feature, extras=extras)
        body = body.replace('""', 'null')

        # Execute manage add fields function
        sql = ("SELECT gw_fct_duplicate_psector($${" + body + "}$$)::text")
        print(str(sql))
        status = self.controller.execute_sql(sql, log_sql=True, commit=True)

        if not status:
            return

        # Close dialog
        self.close_dialog(self.dlg_duplicate_psector)