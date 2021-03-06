"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU 
General Public License as published by the Free Software Foundation, either version 3 of the License, 
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import QObject
from qgis.PyQt.QtWidgets import QAction, QDockWidget, QToolBar, QToolButton
from qgis.PyQt.QtGui import QIcon

import configparser
import os.path
import sys

from . import global_vars
from .lib.qgis_tools import QgisTools
from .core.load_project import LoadProject
from .core.admin import GwAdmin
from .dao.controller import DaoController


class Giswater(QObject):

    def __init__(self, iface):
        """ Constructor
        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """

        super(Giswater, self).__init__()

        # Initialize instance attributes
        self.iface = iface
        self.srid = None
        self.load_project = None
        self.dict_toolbars = {}
        self.dict_actions = {}
        self.actions_not_checkable = None
        self.available_layers = []
        self.btn_add_layers = None
        self.update_sql = None
        self.action = None
        self.action_info = None
        self.toolButton = None
        self.gw_actions = None

        # Initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        self.qgis_tools = QgisTools(iface, self.plugin_dir)
        global_vars.init_qgis_tools(self.qgis_tools)
        self.plugin_name = self.qgis_tools.get_value_from_metadata('name', 'giswater')
        self.icon_folder = self.plugin_dir + os.sep + 'icons' + os.sep

        # Check if config file exists
        setting_file = os.path.join(self.plugin_dir, 'config', self.plugin_name + '.config')
        if not os.path.exists(setting_file):
            message = f"Config file not found at: {setting_file}"
            self.iface.messageBar().pushMessage("", message, 1, 20)
            return

        # Set plugin and QGIS settings: stored in the registry (on Windows) or .ini file (on Unix)
        global_vars.init_settings(setting_file)
        global_vars.init_qgis_settings(self.plugin_name)
        global_vars.plugin_settings_set_value('aaa', 'vbrgs')

        # Enable Python console and Log Messages panel if parameter 'enable_python_console' = True
        enable_python_console = global_vars.settings.value('system_variables/enable_python_console', 'FALSE').upper()
        if enable_python_console == 'TRUE':
            self.qgis_tools.enable_python_console()

        # Define signals
        self.set_signals()


    def set_signals(self):
        """ Define widget and event signals """

        try:
            self.iface.projectRead.connect(self.project_read)
            self.iface.newProjectCreated.connect(self.project_new)
            self.iface.actionSaveProject().triggered.connect(self.save_toolbars_position)
        except AttributeError:
            pass


    def set_info_button(self):
        """ Set main information button (always visible) """

        self.toolButton = QToolButton()
        self.action_info = self.iface.addToolBarWidget(self.toolButton)

        icon_path = self.icon_folder + '36.png'
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            self.action = QAction(icon, "Show info", self.iface.mainWindow())
        else:
            self.action = QAction("Show info", self.iface.mainWindow())

        self.toolButton.setDefaultAction(self.action)
        self.update_sql = GwAdmin(self.iface, global_vars.settings, self.controller, self.plugin_dir)
        self.action.triggered.connect(self.update_sql.init_sql)


    def unset_info_button(self):
        """ Unset main information button (when plugin is disabled or reloaded) """

        if self.action:
            self.action.triggered.disconnect()
        if self.action_info:
            self.iface.removeToolBarIcon(self.action_info)
        self.action = None
        self.action_info = None


    def initGui(self):
        """ Create the menu entries and toolbar icons inside the QGIS GUI """

        # Initialize plugin
        self.init_plugin()

        # Force project read (to work with PluginReloader)
        self.project_read(False)


    def init_plugin(self):
        """ Plugin main initialization function """

        # Set controller (no database connection yet)
        self.controller = DaoController(self.plugin_name, self.iface, create_logger=True)
        self.controller.set_plugin_dir(self.plugin_dir)

        # Set main information button (always visible)
        self.set_info_button()

        # Manage section 'actions_list' of config file
        self.manage_section_actions_list()

        # Manage section 'toolbars' of config file
        self.manage_section_toolbars()


    def manage_section_actions_list(self):
        """ Manage section 'actions_list' of config file """

        # Dynamically get parameters defined in section 'actions_list'
        section = 'actions_not_checkable'
        global_vars.settings.beginGroup(section)
        list_keys = global_vars.settings.allKeys()
        global_vars.settings.endGroup()
        for key in list_keys:
            list_values = global_vars.settings.value(f"{section}/{key}")
            if list_values:
                self.dict_actions[key] = list_values
            else:
                self.controller.show_warning(f"Parameter not set in section '{section}' of config file: '{key}'")

        # Get list of actions not checkable (normally because they open a form)
        aux = []
        for list_actions in self.dict_actions.values():
            for elem in list_actions:
                aux.append(elem)

        self.actions_not_checkable = sorted(aux)


    def manage_section_toolbars(self):
        """ Manage section 'toolbars' of config file """

        # Dynamically get parameters defined in section 'toolbars'
        section = 'toolbars'
        global_vars.settings.beginGroup(section)
        list_keys = global_vars.settings.allKeys()
        global_vars.settings.endGroup()
        for key in list_keys:
            list_values = global_vars.settings.value(f"{section}/{key}")
            if list_values:
                # Check if list_values has only one value
                if type(list_values) is str:
                    list_values = [list_values]
                self.dict_toolbars[key] = list_values
            else:
                self.controller.show_warning(f"Parameter not set in section '{section}' of config file: '{key}'")


    def project_new(self):
        """ Function executed when a user creates a new QGIS project """

        self.unload(False)


    def project_read(self, show_warning=True):
        """ Function executed when a user opens a QGIS project (*.qgs) """

        # Unload plugin before reading opened project
        self.unload(False)

        # Create class to manage code that performs project configuration
        self.load_project = LoadProject(self.iface, global_vars.settings, self.controller, self.plugin_dir)
        self.load_project.project_read(show_warning)


    def save_toolbars_position(self):

        parser = configparser.ConfigParser(comment_prefixes=';', allow_no_value=True)
        main_folder = os.path.join(os.path.expanduser("~"), self.plugin_name)
        config_folder = main_folder + os.sep + "config" + os.sep
        if not os.path.exists(config_folder):
            os.makedirs(config_folder)
        path = config_folder + 'user.config'
        parser.read(path)

        # Get all QToolBar
        widget_list = self.iface.mainWindow().findChildren(QToolBar)
        x = 0
        own_toolbars = []
        # Get a list with own QToolBars
        for w in widget_list:
            if w.property('gw_name'):
                own_toolbars.append(w)

        # Order list of toolbar in function of X position
        own_toolbars = sorted(own_toolbars, key=lambda k: k.x())
        if len(own_toolbars) == 0:
            return

        # Check if section toolbars_position exists in file
        if 'toolbars_position' not in parser:
            parser = configparser.RawConfigParser()
            parser.add_section('toolbars_position')

        # Save position of Giswater toolbars
        for w in own_toolbars:
            parser['toolbars_position'][f'pos_{x}'] = f"{w.property('gw_name')},{w.x()},{w.y()}"
            x += 1

        with open(path, 'w') as configfile:
            parser.write(configfile)
            configfile.close()


    def unload(self, remove_modules=True):
        """ Removes plugin menu items and icons from QGIS GUI
            :param @remove_modules is True when plugin is disabled or reloaded
        """

        # Remove Giswater dockers
        self.remove_dockers()

        # Save toolbar position after unload plugin
        try:
            self.save_toolbars_position()
        except Exception as e:
            self.controller.log_warning(str(e))

        try:
            # Unlisten notify channel and stop thread
            if global_vars.settings.value('system_variables/use_notify').upper() == 'TRUE' and hasattr(self, 'notify'):
                list_channels = ['desktop', self.controller.current_user]
                self.notify.stop_listening(list_channels)

            if self.load_project:
                if self.load_project.actions:
                    for action in list(self.load_project.actions.values()):
                        self.iface.removePluginMenu(self.plugin_name, action)
                        self.iface.removeToolBarIcon(action)

            if self.load_project:
                if self.load_project.plugin_toolbars:
                    for plugin_toolbar in list(self.load_project.plugin_toolbars.values()):
                        if plugin_toolbar.enabled:
                            plugin_toolbar.toolbar.setVisible(False)
                            del plugin_toolbar.toolbar

            if remove_modules:
                # Unset main information button (when plugin is disabled or reloaded)
                self.unset_info_button()

                # unload all loaded giswater related modules
                for mod_name, mod in list(sys.modules.items()):
                    if mod and hasattr(mod, '__file__') and mod.__file__:
                        if self.plugin_dir in mod.__file__:
                            del sys.modules[mod_name]

            else:
                self.set_info_button_visible()

        except Exception:
            pass
        finally:
            self.load_project = None


    def remove_dockers(self):
        """ Remove Giswater dockers """

        docker_search = self.iface.mainWindow().findChild(QDockWidget, 'dlg_search')
        if docker_search:
            self.iface.removeDockWidget(docker_search)

        docker_info = self.iface.mainWindow().findChild(QDockWidget, 'docker')
        if docker_info:
            self.iface.removeDockWidget(docker_info)

        if self.btn_add_layers:
            dockwidget = self.iface.mainWindow().findChild(QDockWidget, 'Layers')
            toolbar = dockwidget.findChildren(QToolBar)[0]
            # TODO improve this, now remove last action
            toolbar.removeAction(toolbar.actions()[len(toolbar.actions()) - 1])
            self.btn_add_layers = None

