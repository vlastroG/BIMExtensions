# -*- coding: utf-8 -*-

import clr

clr.AddReference("dosymep.Revit.dll")
clr.AddReference("dosymep.Bim4Everyone.dll")

import dosymep

clr.ImportExtensions(dosymep.Revit)
clr.ImportExtensions(dosymep.Bim4Everyone)

from Autodesk.Revit.DB import *
from pyrevit import revit, DB
from pyrevit import EXEC_PARAMS
from dosymep_libs.bim4everyone import *

doc = __revit__.ActiveUIDocument.Document

selection = revit.get_selection()


def is_group(element):
    return isinstance(element, DB.Group)


def get_group(element, group_elements=None):
    if not group_elements:
        group_elements = []

    group_elements.append(element)
    for element in get_group_elements(element):
        if is_group(element):
            get_group(element, group_elements)

        group_elements.append(element)

    return group_elements


def get_group_elements(group):
    if is_group(group):
        for sub_element_id in group.GetMemberIds():
            yield doc.GetElement(sub_element_id)

        if not group.IsAttached:
            for sub_element_id in group.GetAvailableAttachedDetailGroupTypeIds():
                for group in doc.GetElement(sub_element_id).Groups:
                    yield group


def is_parameters_editable(element):
    if element.IsExistsParam(BuiltInParameter.PHASE_CREATED) and element.IsExistsParam(
            BuiltInParameter.PHASE_DEMOLISHED):
        return not element.GetParam(BuiltInParameter.PHASE_CREATED).IsReadOnly and not element.GetParam(
            BuiltInParameter.PHASE_DEMOLISHED).IsReadOnly
    return False


def filter_elements(elements):
    for element in elements:
        if element.HasPhases() and is_parameters_editable(element):
            yield element


@notification()
@log_plugin(EXEC_PARAMS.command_name)
def script_execute(plugin_logger):
    elements = []
    for selected in selection:
        elements.extend(filter_elements(get_group(selected)))

    selection.set_to([e.Id for e in elements])
    show_executed_script_notification()


script_execute()
