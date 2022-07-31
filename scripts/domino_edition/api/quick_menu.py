# maya
from maya import cmds as mc
from maya import mel

# built-ins
from functools import partial

# domino
from domino.api import (attribute,
                        controller)


def _null(*args, **kwargs):
    pass


def __reset_SRT(*args):
    attribute.reset_SRT(args[0], args[1])


def __reset_all(*args):
    attribute.reset_all(args[0])


def __attribute_trigger(n, attr, value, *args, **kwargs):
    mc.setAttr(n + "." + attr, value)


def __message_dialog(message, *args, **kwargs):
    mc.confirmDialog(title="Notes",
                     message=message,
                     button=["Ok"],
                     defaultButton="Ok")


def install(menu_id):
    if not mc.optionVar(exists="domino_quick_menu"):
        mc.optionVar(intValue=("domino_quick_menu", 0))
    state = mc.optionVar(query="domino_quick_menu")

    mc.setParent(menu_id, menu=True)
    mc.menuItem("domino_quick_menu",
                label="Domino Quick Menu",
                command=partial(quick_menu_toggle),
                checkBox=state)
    mc.menuItem(divider=True)
    quick_menu_toggle(state)


def __quick_menu(parent_menu, current_control):
    asset_root = mc.ls(current_control, long=True)[0].split("|")[1]
    asset_container = mc.container(query=True,
                                   findContainer=asset_root)

    selected = mc.ls(sl=1)
    selected_controller = [x for x in selected if mc.objExists(f"{x}.is_domino_ctl")]

    child_controller = controller.get_child_controller(current_control)
    child_controller.append(current_control)

    connected_sets = mc.listConnections(current_control, type="objectSet")
    controller_sets = [x for x in connected_sets if mc.nodeType(x) == "objectSet"]
    if controller_sets:
        controller_sets = controller_sets[0]
    all_controller = mc.sets(controller_sets, query=True)

    selected_container = mc.container(query=True,
                                      findContainer=current_control)
    if selected_container:
        if selected_container != asset_container:
            mc.menuItem(parent=parent_menu, divider=True)
            selected_root = mc.container(selected_container,
                                         query=True,
                                         publishAsRoot=True)
            host = mc.listConnections(f"{selected_root}.host",
                                      destination=False,
                                      source=True)
            mc.menuItem(parent=parent_menu,
                        label="Select Host",
                        command=f"import maya.cmds as mc;mc.select({host})")
            mc.menuItem(parent=parent_menu, divider=True)

    if mc.objExists(f"{current_control}.is_domino_ctl"):
        mc.menuItem(parent=parent_menu,
                    label="Switch IK / FK (DEV)",
                    command=_null)
        mc.menuItem(parent=parent_menu,
                    label="Switch IK / FK + key (DEV)",
                    command=_null)
        mc.menuItem(parent=parent_menu, divider=True)

        mc.menuItem(parent=parent_menu,
                    label="Reset",
                    command=partial(__reset_all, selected_controller))
        mc.menuItem(parent=parent_menu,
                    label="Reset all below",
                    command=partial(__reset_all, child_controller))
        mc.menuItem(parent=parent_menu,
                    label="Reset translate",
                    command=partial(__reset_SRT, selected_controller, ["tx", "ty", "tz"]))
        mc.menuItem(parent=parent_menu,
                    label="Reset rotate",
                    command=partial(__reset_SRT, selected_controller, ["rx", "ry", "rz"]))
        mc.menuItem(parent=parent_menu,
                    label="Reset scale",
                    command=partial(__reset_SRT, selected_controller, ["sx", "sy", "sz"]))
        mc.menuItem(parent=parent_menu, divider=True)

        mc.menuItem(parent=parent_menu,
                    label="Mirror (DEV)",
                    command=_null)
        mc.menuItem(parent=parent_menu,
                    label="Mirror below (DEV)",
                    command=_null)
        mc.menuItem(parent=parent_menu,
                    label="Flip (DEV)",
                    command=_null)
        mc.menuItem(parent=parent_menu,
                    label="Flip below (DEV)",
                    command=_null)
        mc.menuItem(parent=parent_menu, divider=True)

        mc.menuItem(parent=parent_menu,
                    label="Select all controller",
                    command=f"import maya.cmds as mc;mc.select({all_controller})")
        mc.menuItem(parent=parent_menu,
                    label="Select child controller",
                    command=f"import maya.cmds as mc;mc.select({child_controller})")
        mc.menuItem(parent=parent_menu, divider=True)

        mc.menuItem(parent=parent_menu,
                    label="Keyframe child controller",
                    command=f"import maya.cmds as mc;mc.setKeyframe({child_controller})")
        mc.menuItem(parent=parent_menu, divider=True)

    for attr in mc.listAttr(asset_root, userDefined=True, channelBox=True) or []:
        at = mc.attributeQuery(attr, node=asset_root, attributeType=True)
        if at == "bool":
            menu = mc.menuItem(parent=parent_menu,
                               label=attr,
                               subMenu=True)
            mc.radioMenuItemCollection()
            on_value = True if mc.getAttr(f"{asset_root}.{attr}") else False
            off_value = True if not mc.getAttr(
                f"{asset_root}.{attr}") else False
            mc.menuItem(parent=menu,
                        label="on",
                        command=partial(__attribute_trigger,
                                        asset_root,
                                        attr,
                                        True),
                        radioButton=on_value,
                        sourceType="python")
            mc.menuItem(parent=menu,
                        label="off",
                        command=partial(__attribute_trigger,
                                        asset_root,
                                        attr,
                                        False),
                        radioButton=off_value,
                        sourceType="python")
        elif at == "enum":
            enum_names = mc.attributeQuery(attr,
                                           node=asset_root,
                                           listEnum=True)
            if not enum_names:
                continue
            menu = mc.menuItem(parent=parent_menu,
                               label=attr,
                               subMenu=True)
            mc.radioMenuItemCollection()
            current_value = mc.getAttr(f"{asset_root}.{attr}",
                                       asString=True)
            for index, name in enumerate(enum_names[0].split(":")):
                value = True if name == current_value else False
                mc.menuItem(parent=menu,
                            label=name,
                            command=partial(__attribute_trigger,
                                            asset_root,
                                            attr,
                                            index),
                            radioButton=value)
    roots_grp_index = mc.containerPublish(asset_container,
                                          query=True,
                                          bindNode=True).index("roots")
    roots_grp = mc.containerPublish(asset_container,
                                    query=True,
                                    bindNode=True)[roots_grp_index + 1]
    for i in mc.listRelatives(roots_grp, children=True, fullPath=True):
        if mc.getAttr(f"{i}.module") == "assembly_01":
            break
    notes = mc.getAttr(i + ".publish_notes")
    mc.menuItem(parent=parent_menu, divider=True)
    menu = mc.menuItem(parent=parent_menu,
                       label="rig notes",
                       command=partial(__message_dialog, notes))


def domino_quick_menu(*args, **kwargs):
    parent_menu = args[0]

    run_menu = False
    if type(args[1]) != bool:
        sel = mc.ls(selection=True, long=True)
        if sel and mc.objExists(f"{sel[0]}.is_domino_ctl"):
            _parent_menu = parent_menu.replace('"', '')
            mc.menu(_parent_menu, edit=True, deleteAllItems=True)

            __quick_menu(_parent_menu, sel[0])
            run_menu = True
    if not run_menu:
        mel.eval("buildObjectMenuItemsNow " + parent_menu)
    return parent_menu


def quick_menu_toggle_cb(state):
    for m_menu in mc.lsUI(menus=True):
        menu_cmd = mc.menu(m_menu, query=True, postMenuCommand=True) or []
        if state and isinstance(menu_cmd, str):
            if "buildObjectMenuItemsNow" in menu_cmd:
                parent_menu = menu_cmd.split(" ")[-1]
                mc.menu(m_menu, edit=True, postMenuCommand=partial(
                    domino_quick_menu, parent_menu))
        elif not state and type(menu_cmd) == partial:
            if "domino_quick_menu" in menu_cmd.func.__name__:
                parent_menu = menu_cmd(state)
                mel.eval('menu -edit -postMenuCommand '
                         '"buildObjectMenuItemsNow '
                         + parent_menu.replace('"', '') + '"' + m_menu)


def quick_menu_toggle(*args, **kwargs):
    state = args[0]

    if state:
        mc.optionVar(intValue=("domino_quick_menu", 1))
    else:
        mc.optionVar(intValue=("domino_quick_menu", 0))

    quick_menu_toggle_cb(state)
