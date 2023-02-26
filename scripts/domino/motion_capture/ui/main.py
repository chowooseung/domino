# gui
from PySide2 import QtWidgets
from . import main_ui

# mocap
from .. import api
from ..api.utils import DOMINO_MOTION_DIR

# built-ins
import os

# maya
from pymel import core as pm

# domino
from domino.core import log


class ImitatorUI(QtWidgets.QDialog, main_ui.Ui_Dialog):
    ui_name = "DominoMotionCaptureImitatorUI"

    def __init__(self, parent=None):
        super(ImitatorUI, self).__init__(parent=parent)
        self.setupUi(self)
        self.setWindowTitle("Motion Capture Imitator")
        self.setObjectName(self.ui_name)


class Imitator(ImitatorUI):

    def __init__(self, parent=None):
        super(Imitator, self).__init__(parent=parent)
        self.populate()
        self.create_connections()

    @property
    def motion_capture_dir(self):
        motion_dir = os.getenv(DOMINO_MOTION_DIR, None)
        if not os.path.exists(motion_dir):
            pm.displayWarning(f"{DOMINO_MOTION_DIR} is None")
        return os.path.join(motion_dir, "rig"), os.path.join(motion_dir, "motion")

    def populate(self):
        self.motion_definition_comboBox.clear()
        self.interface_comboBox.clear()
        rig_directory, motion_directory = self.motion_capture_dir
        if not (os.path.exists(rig_directory) and os.path.exists(motion_directory)):
            return

        for definition in [x for x in os.listdir(motion_directory) if x.endswith(".xml")]:
            self.motion_definition_comboBox.addItem(definition.split(".xml")[0])

        for definition in [x for x in os.listdir(rig_directory) if x.endswith(".xml")]:
            fbx_file = os.path.join(rig_directory, definition.replace(".xml", ".fbx"))
            json_file = os.path.join(rig_directory, definition.replace(".xml", ".json"))
            if os.path.exists(fbx_file) and os.path.exists(json_file):
                self.interface_comboBox.addItem(definition.split(".xml")[0])

    def create_connections(self):
        self.load_rig_pushButton.clicked.connect(self.load_rig)
        self.export_pushButton.clicked.connect(self.export)

    def load_rig(self):
        rig_directory, motion_directory = self.motion_capture_dir

        rig_file = self.target_rig_file_lineEdit.text()
        interface_name = self.interface_comboBox.currentText()
        interface_file = os.path.join(rig_directory, interface_name + ".fbx")
        map_file = os.path.join(rig_directory, interface_name + ".json")
        definition_file = os.path.join(rig_directory, interface_name + ".xml")
        if False in [os.path.exists(x) for x in [rig_file, interface_file, map_file, definition_file]]:
            return

        # new scene, import rig
        api.prepare_rig(rig_file)

        # import interface, attach
        api.load_interface(interface_file, map_file, definition_file)

    def export(self):
        rig_directory, motion_directory = self.motion_capture_dir

        rig_file = self.target_rig_file_lineEdit.text()
        rig_file = rig_file.replace(os.sep, "/")
        interface_name = self.interface_comboBox.currentText()
        interface_file = os.path.join(rig_directory, interface_name + ".fbx")
        map_file = os.path.join(rig_directory, interface_name + ".json")
        rig_definition_file = os.path.join(rig_directory, interface_name + ".xml")

        motion_definition_name = self.motion_definition_comboBox.currentText()
        motion_definition_file = os.path.join(motion_directory, motion_definition_name + ".xml")
        motion_definition_file = motion_definition_file.replace(os.sep, "/")

        motion_directory = self.motion_directory_lineEdit.text()
        motion_directory = motion_directory.replace(os.sep, "/")
        export_directory = self.export_directory_lineEdit.text()
        export_directory = export_directory.replace(os.sep, "/")
        if False in [os.path.exists(x) for x in [rig_file,
                                                 interface_file,
                                                 map_file,
                                                 rig_definition_file,
                                                 motion_definition_file,
                                                 motion_directory,
                                                 export_directory]]:
            return

        log.Logger.info(f"Rig : '{rig_file}'")
        log.Logger.info(f"Motion Directory : '{motion_directory}'")
        log.Logger.info(f"Export Directory : '{export_directory}'")
        for fbx in [x for x in os.listdir(motion_directory) if x.endswith("fbx")]:
            api.prepare_rig(rig_file)
            api.load_interface(interface_file, map_file, rig_definition_file)

            motion_file = os.path.join(motion_directory, fbx)
            log.Logger.info(f"Motion : '{motion_file}'")
            api.load_motion(motion_file, motion_definition_file)

            api.set_source("interfaceCharacter", "motionCharacter")

            retargeted_file = os.path.join(export_directory, "retargeted_" + fbx.replace(".fbx", ".ma"))
            log.Logger.info(f"Retargeted : '{retargeted_file}'")
            api.export(retargeted_file)
