# -*- coding: utf-8 -*-
from PyQt4.QtGui import QComboBox, QDateEdit, QPushButton, QTableView, QTabWidget, QLineEdit

from functools import partial

import utils_giswater
from parent_init import ParentDialog
from ui.add_sum import Add_sum          # @UnresolvedImport


def formOpen(dialog, layer, feature):
    ''' Function called when a connec is identified in the map '''
    
    global feature_dialog
    utils_giswater.setDialog(dialog)
    # Create class to manage Feature Form interaction  
    feature_dialog = ManConnecDialog(dialog, layer, feature)
    init_config()

    
def init_config():
     
    # Manage visibility    
    ''' 
    feature_dialog.dialog.findChild(QComboBox, "connecat_id").setVisible(False)    
    feature_dialog.dialog.findChild(QComboBox, "cat_connectype_id").setVisible(False) 
    '''
    # Manage 'connecat_id'
    connecat_id = utils_giswater.getWidgetText("connecat_id") 
    utils_giswater.setSelectedItem("connecat_id", connecat_id)   
    
    # Manage 'connec_type'
    cat_connectype_id = utils_giswater.getWidgetText("cat_connectype_id")    
    
    # Set button signals      
    #feature_dialog.dialog.findChild(QPushButton, "btn_accept").clicked.connect(feature_dialog.save)            
    #feature_dialog.dialog.findChild(QPushButton, "btn_close").clicked.connect(feature_dialog.close)  

     
class ManConnecDialog(ParentDialog):   
    
    def __init__(self, dialog, layer, feature):
        ''' Constructor class '''
        super(ManConnecDialog, self).__init__(dialog, layer, feature)      
        self.init_config_form()
        
        
    def init_config_form(self):
        ''' Custom form initial configuration '''
      
        table_element = "v_ui_element_x_connec" 
        table_document = "v_ui_doc_x_connec"
        table_event_element = "v_ui_event_x_element_x_connec" 
        table_event_connec = "v_ui_event_x_connec"
        table_hydrometer = "v_rtc_hydrometer"    
        table_hydrometer_value = "v_edit_rtc_hydro_data_x_connec"    
              
        # Define class variables
        self.field_id = "connec_id"        
        self.id = utils_giswater.getWidgetText(self.field_id, False)  
        self.filter = self.field_id+" = '"+str(self.id)+"'"                    
        self.connec_type = utils_giswater.getWidgetText("cat_connectype_id", False)        
        self.connec_type = utils_giswater.getWidgetText("connec_type", False) 
        
        # Get widget controls      
        self.tab_main = self.dialog.findChild(QTabWidget, "tab_main")  
        self.tbl_info = self.dialog.findChild(QTableView, "tbl_element")   
        self.tbl_document = self.dialog.findChild(QTableView, "tbl_document")
        self.tbl_event_element = self.dialog.findChild(QTableView, "tbl_event_element") 
        self.tbl_event_connec = self.dialog.findChild(QTableView, "tbl_event_connec")  
        self.tbl_hydrometer = self.dialog.findChild(QTableView, "tbl_hydro") 
        self.tbl_hydrometer_value = self.dialog.findChild(QTableView, "tbl_hydro_value") 
              
        # Load data from related tables
        self.load_data()
        
        # Set layer in editing mode
        self.layer.startEditing()
        
        # Fill the info table
        self.fill_table(self.tbl_info, self.schema_name+"."+table_element, self.filter)
        
        # Configuration of info table
        self.set_configuration(self.tbl_info, table_element)    
        
        # Fill the tab Document
        self.fill_tbl_document_man(self.tbl_document, self.schema_name+"."+table_document, self.filter)
        
        # Configuration of table Document
        self.set_configuration(self.tbl_document, table_document)

        
        # Fill tab event | element
        self.fill_tbl_event(self.tbl_event_element, self.schema_name+"."+table_event_element, self.filter)
        
        # Configuration of table event | element
        self.set_configuration(self.tbl_event_element, table_event_element)
        
        # Fill tab event | connec
        self.fill_tbl_event(self.tbl_event_connec, self.schema_name+"."+table_event_connec, self.filter)
        
        # Configuration of table event | connec
        self.set_configuration(self.tbl_event_connec, table_event_connec)
        
  
        
        # Fill tab hydrometer | hydrometer
        self.fill_tbl_hydrometer(self.tbl_hydrometer, self.schema_name+"."+table_hydrometer, self.filter)
        
        # Configuration of table hydrometer | hydrometer
        self.set_configuration(self.tbl_hydrometer, table_hydrometer)
        
        # Fill tab hydrometer | hydrometer value
        self.fill_tbl_hydrometer(self.tbl_hydrometer_value, self.schema_name+"."+table_hydrometer_value, self.filter)
        
        # Configuration of table hydrometer | hydrometer value
        self.set_configuration(self.tbl_hydrometer_value, table_hydrometer_value)
        
        
        # Set signals          
        self.dialog.findChild(QPushButton, "btn_doc_delete").clicked.connect(partial(self.delete_records, self.tbl_document, table_document))            
        self.dialog.findChild(QPushButton, "delete_row_info").clicked.connect(partial(self.delete_records, self.tbl_info, table_element))       
        
      
      
        
       