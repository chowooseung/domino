# domino
from domino.assembler.ui import CommonComponentSettings

# gui
from PySide2 import QtWidgets, QtCore
from . import settings_ui


class IndividualSettings(QtWidgets.QWidget, settings_ui.Ui_Form):

    def __init__(self, parent=None):
        super(IndividualSettings, self).__init__(parent=parent)
        self.setupUi(self)


class Settings(CommonComponentSettings):
    title_name = "Eyebrow 01 Settings"

    def __init__(self, parent=None):
        super(Settings, self).__init__(parent=parent)

        ui = IndividualSettings(self.common_settings)
        self.common_settings.toolBox.addItem(ui, "Individual Settings")
        self.resize_window()

    def resize_window(self):
        super(Settings, self).resize_window()
        index = self.common_settings.toolBox.currentIndex()
        if index == 1:
            size = QtCore.QSize(370, 300)
            self.resize(size)
