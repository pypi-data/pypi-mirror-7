# -*- coding: utf-8 -*-

# Resource object code
#
# Created: št 24. 4 18:02:27 2014
#      by: The Resource Compiler for PySide (Qt v4.8.5)
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore

qt_resource_data = b"\x00\x00\x01 Qt\x0d\x0aQuarterly\x0d\x0ais\x0d\x0aa\x0d\x0apaper\x0d\x0abased\x0d\x0anewsletter\x0d\x0aexclusively\x0d\x0aavailable\x0d\x0ato\x0d\x0aQt\x0d\x0acustomers\x0d\x0aEvery\x0d\x0aquarter\x0d\x0awe\x0d\x0amail\x0d\x0aout\x0d\x0aan\x0d\x0aissue\x0d\x0athat\x0d\x0awe\x0d\x0ahope\x0d\x0awill\x0d\x0abring\x0d\x0aadded\x0d\x0ainsight\x0d\x0aand\x0d\x0apleasure\x0d\x0ato\x0d\x0ayour\x0d\x0aQt\x0d\x0aprogramming\x0d\x0awith\x0d\x0ahigh\x0d\x0aquality\x0d\x0atechnical\x0d\x0aarticles\x0d\x0awritten\x0d\x0aby\x0d\x0aQt\x0d\x0aexperts\x0d\x0a"
qt_resource_name = b"\x00\x0a\x0b\x0b\x17\xd9\x00d\x00i\x00c\x00t\x00i\x00o\x00n\x00a\x00r\x00y\x00\x09\x08\xb6\xa74\x00w\x00o\x00r\x00d\x00s\x00.\x00t\x00x\x00t"
qt_resource_struct = b"\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x1a\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00"
def qInitResources():
    QtCore.qRegisterResourceData(0x01, qt_resource_struct, qt_resource_name, qt_resource_data)

def qCleanupResources():
    QtCore.qUnregisterResourceData(0x01, qt_resource_struct, qt_resource_name, qt_resource_data)

qInitResources()
