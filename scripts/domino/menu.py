# domino
from .api import menu
from domino_edition.api import quick_menu
from domino_edition.api import menu as edition_menu


def install():
    menu.create()

    # quick menu checkbox
    quick_menu.install(menu.menu_id)

    # Edition
    edition_menu.install()

    # ---
    menu.divide(menu.menu_id)

    # RiggingTools
    rigging_menu()

    # MotionCaptureTools
    motion_capture_menu()

    # ---
    menu.divide(menu.menu_id)

    # Utils
    menu.install_utils()


cb_add_blended_jnt = """from domino_edition.api import lib
domino_edition.api.lib.add_blended_jnt()"""

cb_add_support_jnt = """from domino_edition.api import lib
domino_edition.api.lib.add_support_jnt()"""


def rigging_menu():
    command = (
        ("Add Blended Joint", cb_add_blended_jnt, ""),
        ("Add Support Joint", cb_add_support_jnt, "")
    )
    menu.add("Rigging Tools", command)


def motion_capture_menu():
    commands = (
        ("MotionCaptureCmd", "qwer", ""),
    )
    menu.add("Motion Capture Tools", commands)
