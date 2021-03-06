"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import Qt

from ..parent_maptool import GwParentMapTool
from ...utils.giswater_tools import create_body


class GwFlowExitButton(GwParentMapTool):
    """
        Button 57: Flow exit
    """

    def __init__(self, icon_path, text, toolbar, action_group, iface, settings, controller, plugin_dir):
        """ Class constructor """

        # Call ParentMapTool constructor
        super().__init__(icon_path, text, toolbar, action_group, iface, settings, controller, plugin_dir)

        self.layers_added = []


    """ QgsMapTools inherited event functions """

    def canvasMoveEvent(self, event):

        # Hide marker and get coordinates
        self.vertex_marker.hide()
        event_point = self.snapper_manager.get_event_point(event)

        # Snapping
        result = self.snapper_manager.snap_to_current_layer(event_point)
        if self.snapper_manager.result_is_valid():
            self.snapper_manager.add_marker(result, self.vertex_marker)
            # Data for function
            self.snapped_feat = self.snapper_manager.get_snapped_feature(result)


    def canvasReleaseEvent(self, event):
        """ With left click the digitizing is finished """

        if event.button() == Qt.LeftButton and self.current_layer:

            # Execute SQL function
            function_name = "gw_fct_flow_exit"

            elem_id = self.snapped_feat.attribute('node_id')
            feature_id = f'"id":["{elem_id}"]'
            body = create_body(feature=feature_id)
            result = self.controller.get_json(function_name, body, log_sql=True)
            if not result:
                return

            # Refresh map canvas
            self.refresh_map_canvas()

            # Set action pan
            self.set_action_pan()


    def activate(self):

        # set active and current layer
        self.layer_node = self.controller.get_layer_by_tablename("v_edit_node")
        self.iface.setActiveLayer(self.layer_node)
        self.current_layer = self.layer_node

        # Check button
        self.action.setChecked(True)

        # Set main snapping layers
        self.snapper_manager.set_snapping_layers()

        # Store user snapping configuration
        self.snapper_manager.store_snapping_options()

        # Clear snapping
        self.snapper_manager.enable_snapping()

        # Set snapping to node
        self.snapper_manager.snap_to_node()

        # Change cursor
        self.canvas.setCursor(self.cursor)

        # Show help message when action is activated
        if self.show_help:
            message = "Select a node and click on it, the downstream nodes are computed"
            self.controller.show_info(message)

        # Control current layer (due to QGIS bug in snapping system)
        if self.canvas.currentLayer() is None:
            layer = self.controller.get_layer_by_tablename('v_edit_node')
            if layer:
                self.iface.setActiveLayer(layer)


    def deactivate(self):
        
        # Call parent method
        super().deactivate()

