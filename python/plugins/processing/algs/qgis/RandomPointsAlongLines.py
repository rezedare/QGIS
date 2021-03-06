# -*- coding: utf-8 -*-

"""
***************************************************************************
    RandomPointsAlongLines.py
    ---------------------
    Date                 : April 2014
    Copyright            : (C) 2014 by Alexander Bruy
    Email                : alexander dot bruy at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
from builtins import next

__author__ = 'Alexander Bruy'
__date__ = 'April 2014'
__copyright__ = '(C) 2014, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import random

from qgis.PyQt.QtCore import QVariant
from qgis.core import (QgsApplication,
                       QgsFields,
                       QgsField,
                       QgsGeometry,
                       QgsSpatialIndex,
                       QgsWkbTypes,
                       QgsDistanceArea,
                       QgsFeatureRequest,
                       QgsFeature,
                       QgsPoint,
                       QgsMessageLog,
                       QgsProcessingUtils)

from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterVector
from processing.core.parameters import ParameterNumber
from processing.core.outputs import OutputVector
from processing.tools import dataobjects, vector


class RandomPointsAlongLines(GeoAlgorithm):

    VECTOR = 'VECTOR'
    POINT_NUMBER = 'POINT_NUMBER'
    MIN_DISTANCE = 'MIN_DISTANCE'
    OUTPUT = 'OUTPUT'

    def icon(self):
        return QgsApplication.getThemeIcon("/providerQgis.svg")

    def svgIconPath(self):
        return QgsApplication.iconPath("providerQgis.svg")

    def group(self):
        return self.tr('Vector creation tools')

    def name(self):
        return 'randompointsalongline'

    def displayName(self):
        return self.tr('Random points along line')

    def defineCharacteristics(self):
        self.addParameter(ParameterVector(self.VECTOR,
                                          self.tr('Input layer'), [dataobjects.TYPE_VECTOR_LINE]))
        self.addParameter(ParameterNumber(self.POINT_NUMBER,
                                          self.tr('Number of points'), 1, None, 1))
        self.addParameter(ParameterNumber(self.MIN_DISTANCE,
                                          self.tr('Minimum distance'), 0.0, None, 0.0))
        self.addOutput(OutputVector(self.OUTPUT, self.tr('Random points'), datatype=[dataobjects.TYPE_VECTOR_POINT]))

    def processAlgorithm(self, context, feedback):
        layer = QgsProcessingUtils.mapLayerFromString(self.getParameterValue(self.VECTOR), context)
        pointCount = float(self.getParameterValue(self.POINT_NUMBER))
        minDistance = float(self.getParameterValue(self.MIN_DISTANCE))

        fields = QgsFields()
        fields.append(QgsField('id', QVariant.Int, '', 10, 0))
        writer = self.getOutputFromName(self.OUTPUT).getVectorWriter(fields, QgsWkbTypes.Point, layer.crs(), context)

        nPoints = 0
        nIterations = 0
        maxIterations = pointCount * 200
        featureCount = layer.featureCount()
        total = 100.0 / pointCount

        index = QgsSpatialIndex()
        points = dict()

        da = QgsDistanceArea()
        request = QgsFeatureRequest()

        random.seed()

        while nIterations < maxIterations and nPoints < pointCount:
            # pick random feature
            fid = random.randint(0, featureCount - 1)
            f = next(layer.getFeatures(request.setFilterFid(fid).setSubsetOfAttributes([])))
            fGeom = f.geometry()

            if fGeom.isMultipart():
                lines = fGeom.asMultiPolyline()
                # pick random line
                lineId = random.randint(0, len(lines) - 1)
                vertices = lines[lineId]
            else:
                vertices = fGeom.asPolyline()

            # pick random segment
            if len(vertices) == 2:
                vid = 0
            else:
                vid = random.randint(0, len(vertices) - 2)
            startPoint = vertices[vid]
            endPoint = vertices[vid + 1]
            length = da.measureLine(startPoint, endPoint)
            dist = length * random.random()

            if dist > minDistance:
                d = dist / (length - dist)
                rx = (startPoint.x() + d * endPoint.x()) / (1 + d)
                ry = (startPoint.y() + d * endPoint.y()) / (1 + d)

                # generate random point
                pnt = QgsPoint(rx, ry)
                geom = QgsGeometry.fromPoint(pnt)
                if vector.checkMinDistance(pnt, index, minDistance, points):
                    f = QgsFeature(nPoints)
                    f.initAttributes(1)
                    f.setFields(fields)
                    f.setAttribute('id', nPoints)
                    f.setGeometry(geom)
                    writer.addFeature(f)
                    index.insertFeature(f)
                    points[nPoints] = pnt
                    nPoints += 1
                    feedback.setProgress(int(nPoints * total))
            nIterations += 1

        if nPoints < pointCount:
            QgsMessageLog.logMessage(self.tr('Can not generate requested number of random points. '
                                             'Maximum number of attempts exceeded.'), self.tr('Processing'), QgsMessageLog.INFO)

        del writer
