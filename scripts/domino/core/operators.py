# maya
from pymel import core as pm

# domino
from domino.core import attribute


def space_switch(source_ctls, target_ctl, host, attr_name="space_switch", constraint="parent"):
    enum_name = ["this"] + [x.nodeName() for x in source_ctls]
    attribute.add(host,
                  attr_name,
                  "enum",
                  enumName=enum_name,
                  keyable=True)
    target_npo = target_ctl.getParent()
    if pm.controller(target_npo, query=True):
        target_npo = target_npo.getParent()
    if constraint == "parent":
        cons_func = pm.parentConstraint
    elif constraint == "point":
        cons_func = pm.pointConstraint
    elif constraint == "orient":
        cons_func = pm.orientConstraint
    cons = cons_func(source_ctls, target_npo, maintainOffset=True)
    weight_list = cons_func(cons, query=True, weightAliasList=True)
    for i, attr in enumerate(weight_list):
        condition = pm.createNode("condition")
        pm.connectAttr(f"{host}.{attr_name}", f"{condition}.firstTerm")
        condition.attr("secondTerm").set(i + 1)
        condition.attr("colorIfTrueR").set(1)
        condition.attr("colorIfFalseR").set(0)
        pm.connectAttr(condition.attr("outColorR"), attr)
    return cons


def ik_2jnt(jnt1, jnt2, scale_attr, slide_attr, stretch_value_attr, max_stretch_attr, negate):
    ik1_distance = jnt1.attr("tx").get()
    ik2_distance = jnt2.attr("tx").get()
    if negate:
        ik1_distance *= -1
        ik2_distance *= -1
        md = pm.createNode("multiplyDivide")
        md.attr("input1X").set(-1)
        pm.connectAttr(stretch_value_attr, md.attr("input2X"))
        stretch_value_attr = md.attr("outputX")

    md = pm.createNode("multiplyDivide")
    pm.connectAttr(scale_attr, md.attr("input1X"))
    pm.connectAttr(scale_attr, md.attr("input1Y"))
    md.attr("input2X").set(ik1_distance)
    md.attr("input2Y").set(ik2_distance)
    scaled_ik1_distance_attr = md.attr("outputX")
    scaled_ik2_distance_attr = md.attr("outputY")

    pma = pm.createNode("plusMinusAverage")
    pm.connectAttr(scaled_ik1_distance_attr, pma.attr("input1D")[0])
    pm.connectAttr(scaled_ik2_distance_attr, pma.attr("input1D")[1])
    scaled_total_distance_attr = pma.attr("output1D")

    rm = pm.createNode("remapValue")
    rm.attr("inputMin").set(0)
    rm.attr("inputMax").set(0.5)
    pm.connectAttr(slide_attr, rm.attr("inputValue"))
    pm.connectAttr(scaled_total_distance_attr, rm.attr("outputMin"))
    pm.connectAttr(scaled_ik1_distance_attr, rm.attr("outputMax"))
    min_ik1_slide_value_attr = rm.attr("outColorR")

    rm = pm.createNode("remapValue")
    rm.attr("inputMin").set(0.5)
    rm.attr("inputMax").set(1)
    pm.connectAttr(slide_attr, rm.attr("inputValue"))
    pm.connectAttr(scaled_ik1_distance_attr, rm.attr("outputMin"))
    rm.attr("outputMax").set(0)
    max_ik1_slide_value_attr = rm.attr("outColorR")

    condition = pm.createNode("condition")
    condition.attr("operation").set(4)
    condition.attr("secondTerm").set(0.5)
    pm.connectAttr(slide_attr, condition.attr("firstTerm"))
    pm.connectAttr(min_ik1_slide_value_attr, condition.attr("colorIfTrueR"))
    pm.connectAttr(max_ik1_slide_value_attr, condition.attr("colorIfFalseR"))
    ik1_slide_value_attr = condition.attr("outColorR")

    pma = pm.createNode("plusMinusAverage")
    pma.attr("operation").set(2)
    pm.connectAttr(scaled_total_distance_attr, pma.attr("input1D")[0])
    pm.connectAttr(ik1_slide_value_attr, pma.attr("input1D")[1])
    ik2_slide_value_attr = pma.attr("output1D")

    md = pm.createNode("multiplyDivide")
    md.attr("operation").set(2)
    pm.connectAttr(stretch_value_attr, md.attr("input1X"))
    pm.connectAttr(scaled_total_distance_attr, md.attr("input2X"))
    stretch_ratio_attr = md.attr("outputX")

    condition = pm.createNode("condition")
    condition.attr("operation").set(2)
    pm.connectAttr(stretch_value_attr, condition.attr("firstTerm"))
    pm.connectAttr(scaled_total_distance_attr, condition.attr("secondTerm"))
    pm.connectAttr(stretch_ratio_attr, condition.attr("colorIfTrueR"))
    condition.attr("colorIfFalseR").set(1)
    stretch_condition_attr = condition.attr("outColorR")

    condition = pm.createNode("condition")
    condition.attr("operation").set(4)
    pm.connectAttr(stretch_condition_attr, condition.attr("firstTerm"))
    pm.connectAttr(max_stretch_attr, condition.attr("secondTerm"))
    pm.connectAttr(stretch_condition_attr, condition.attr("colorIfTrueR"))
    pm.connectAttr(max_stretch_attr, condition.attr("colorIfFalseR"))

    md = pm.createNode("multiplyDivide")
    pm.connectAttr(ik1_slide_value_attr, md.attr("input1X"))
    pm.connectAttr(ik2_slide_value_attr, md.attr("input1Y"))
    pm.connectAttr(condition.attr("outColorR"), md.attr("input2X"))
    pm.connectAttr(condition.attr("outColorR"), md.attr("input2Y"))
    ik1_stretch_value_attr = md.attr("outputX")
    ik2_stretch_value_attr = md.attr("outputY")
    if negate:
        md = pm.createNode("multiplyDivide")
        pm.connectAttr(ik1_stretch_value_attr, md.attr("input1X"))
        pm.connectAttr(ik2_stretch_value_attr, md.attr("input1Y"))
        md.attr("input2X").set(-1)
        md.attr("input2Y").set(-1)
        ik1_stretch_value_attr = md.attr("outputX")
        ik2_stretch_value_attr = md.attr("outputY")

    pm.connectAttr(ik1_stretch_value_attr, jnt1.attr("tx"))
    pm.connectAttr(ik2_stretch_value_attr, jnt2.attr("tx"))


def ik_3jnt(jnt1, jnt2, jnt3, multi1_attr, multi2_attr, multi3_attr, stretch_value_attr, max_stretch_attr, negate):
    ik1_distance = jnt1.attr("tx").get()
    ik2_distance = jnt2.attr("tx").get()
    ik3_distance = jnt3.attr("tx").get()
    if negate:
        ik1_distance *= -1
        ik2_distance *= -1
        ik3_distance *= -1
        md = pm.createNode("multiplyDivide")
        md.attr("input1X").set(-1)
        pm.connectAttr(stretch_value_attr, md.attr("input2X"))
        stretch_value_attr = md.attr("outputX")

    md = pm.createNode("multiplyDivide")
    pm.connectAttr(multi1_attr, md.attr("input1X"))
    pm.connectAttr(multi2_attr, md.attr("input1Y"))
    pm.connectAttr(multi3_attr, md.attr("input1Z"))
    md.attr("input2X").set(ik1_distance)
    md.attr("input2Y").set(ik2_distance)
    md.attr("input2Z").set(ik3_distance)
    multiple_ik1_distance_attr = md.attr("outputX")
    multiple_ik2_distance_attr = md.attr("outputY")
    multiple_ik3_distance_attr = md.attr("outputZ")

    pma = pm.createNode("plusMinusAverage")
    pm.connectAttr(multiple_ik1_distance_attr, pma.attr("input1D")[0])
    pm.connectAttr(multiple_ik2_distance_attr, pma.attr("input1D")[1])
    pm.connectAttr(multiple_ik3_distance_attr, pma.attr("input1D")[2])
    multiple_total_distance_attr = pma.attr("output1D")

    md = pm.createNode("multiplyDivide")
    md.attr("operation").set(2)
    pm.connectAttr(stretch_value_attr, md.attr("input1X"))
    pm.connectAttr(multiple_total_distance_attr, md.attr("input2X"))
    stretch_ratio_attr = md.attr("outputX")

    condition = pm.createNode("condition")
    condition.attr("operation").set(2)
    pm.connectAttr(stretch_value_attr, condition.attr("firstTerm"))
    pm.connectAttr(multiple_total_distance_attr, condition.attr("secondTerm"))
    pm.connectAttr(stretch_ratio_attr, condition.attr("colorIfTrueR"))
    condition.attr("colorIfFalseR").set(1)
    stretch_condition_attr = condition.attr("outColorR")

    condition = pm.createNode("condition")
    condition.attr("operation").set(4)
    pm.connectAttr(stretch_condition_attr, condition.attr("firstTerm"))
    pm.connectAttr(max_stretch_attr, condition.attr("secondTerm"))
    pm.connectAttr(stretch_condition_attr, condition.attr("colorIfTrueR"))
    pm.connectAttr(max_stretch_attr, condition.attr("colorIfFalseR"))

    md = pm.createNode("multiplyDivide")
    pm.connectAttr(multiple_ik1_distance_attr, md.attr("input1X"))
    pm.connectAttr(multiple_ik2_distance_attr, md.attr("input1Y"))
    pm.connectAttr(multiple_ik3_distance_attr, md.attr("input1Z"))
    pm.connectAttr(condition.attr("outColorR"), md.attr("input2X"))
    pm.connectAttr(condition.attr("outColorR"), md.attr("input2Y"))
    pm.connectAttr(condition.attr("outColorR"), md.attr("input2Z"))
    ik1_stretch_value_attr = md.attr("outputX")
    ik2_stretch_value_attr = md.attr("outputY")
    ik3_stretch_value_attr = md.attr("outputZ")
    if negate:
        md = pm.createNode("multiplyDivide")
        pm.connectAttr(ik1_stretch_value_attr, md.attr("input1X"))
        pm.connectAttr(ik2_stretch_value_attr, md.attr("input1Y"))
        pm.connectAttr(ik3_stretch_value_attr, md.attr("input1Z"))
        md.attr("input2X").set(-1)
        md.attr("input2Y").set(-1)
        md.attr("input2Z").set(-1)
        ik1_stretch_value_attr = md.attr("outputX")
        ik2_stretch_value_attr = md.attr("outputY")
        ik3_stretch_value_attr = md.attr("outputZ")

    pm.connectAttr(ik1_stretch_value_attr, jnt1.attr("tx"))
    pm.connectAttr(ik2_stretch_value_attr, jnt2.attr("tx"))
    pm.connectAttr(ik3_stretch_value_attr, jnt3.attr("tx"))


def volume(original_distance_attr, delta_distance_attr, squash_attrs, stretch_attrs, switch_attr, objs):
    md = pm.createNode("multiplyDivide")
    md.attr("operation").set(2)
    pm.connectAttr(delta_distance_attr, md.attr("input1X"))
    pm.connectAttr(original_distance_attr, md.attr("input2X"))
    ratio_attr = md.attr("outputX")

    md = pm.createNode("multiplyDivide")
    md.attr("operation").set(3)
    pm.connectAttr(ratio_attr, md.attr("input1X"))
    md.attr("input2X").set(2)
    pow_value = md.attr("outputX")

    md = pm.createNode("multiplyDivide")
    md.attr("operation").set(3)
    pm.connectAttr(pow_value, md.attr("input1X"))
    md.attr("input2X").set(0.5)
    abs_value = md.attr("outputX")

    for i, obj in enumerate(objs):
        condition = pm.createNode("condition")
        condition.attr("operation").set(3)
        pm.connectAttr(ratio_attr, condition.attr("firstTerm"))
        condition.attr("secondTerm").set(0)
        pm.connectAttr(stretch_attrs[i], condition.attr("colorIfTrueR"))
        pm.connectAttr(squash_attrs[i], condition.attr("colorIfFalseR"))

        md = pm.createNode("multiplyDivide")
        pm.connectAttr(condition.attr("outColorR"), md.attr("input1X"))
        pm.connectAttr(switch_attr, md.attr("input2X"))
        volume_multiple = md.attr("outputX")

        md = pm.createNode("multiplyDivide")
        pm.connectAttr(abs_value, md.attr("input1X"))
        pm.connectAttr(volume_multiple, md.attr("input2X"))

        pma = pm.createNode("plusMinusAverage")
        pma.attr("input3D")[0].set((1, 1, 1))
        pm.connectAttr(md.attr("outputX"), pma.attr("input3D[1].input3Dx"))
        pm.connectAttr(md.attr("outputX"), pma.attr("input3D[1].input3Dy"))
        pm.connectAttr(md.attr("outputX"), pma.attr("input3D[1].input3Dz"))

        pm.connectAttr(pma.attr("output3D"), obj.attr("s"))


def set_fk_ik_blend_matrix(blend, fk, ik, switch):
    for i in range(len(blend)):
        blend_m = pm.createNode("blendMatrix")
        blend_m.attr("envelope").set(1)

        if i == 0:
            mult_m = pm.createNode("multMatrix")
            pm.connectAttr(fk[i].attr("worldMatrix"), mult_m.attr("matrixIn")[0])
            pm.connectAttr(blend[i].attr("parentInverseMatrix"), mult_m.attr("matrixIn")[1])
            pm.connectAttr(mult_m.attr("matrixSum"), blend_m.attr("inputMatrix"))
        else:
            pm.connectAttr(fk[i].attr("matrix"), blend_m.attr("inputMatrix"))

        comp_m = pm.createNode("composeMatrix")
        comp_m.attr("inputTranslate").set(ik[i].attr("t").get())
        comp_m.attr("inputRotate").set(ik[i].attr("jointOrient").get())

        inv_m = pm.createNode("inverseMatrix")
        inv_m.attr("inputMatrix").set(comp_m.attr("outputMatrix").get())
        pm.delete(comp_m)

        mult_m = pm.createNode("multMatrix")
        pm.connectAttr(ik[i].attr("matrix"), mult_m.attr("matrixIn")[0])
        pm.connectAttr(inv_m.attr("outputMatrix"), mult_m.attr("matrixIn")[1])

        pm.connectAttr(mult_m.attr("matrixSum"), blend_m.attr("target.target[0].targetMatrix"))

        decom_m = pm.createNode("decomposeMatrix")
        pm.connectAttr(blend_m.attr("outputMatrix"), decom_m.attr("inputMatrix"))

        pm.connectAttr(decom_m.attr("outputTranslate"), blend[i].attr("t"))
        pm.connectAttr(decom_m.attr("outputRotate"), blend[i].attr("r"))
        pm.connectAttr(decom_m.attr("outputScale"), blend[i].attr("s"))
        pm.connectAttr(decom_m.attr("outputShear"), blend[i].attr("shear"))

        pm.connectAttr(switch, blend_m.attr("envelope"))
