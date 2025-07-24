
"""Module for the slider."""
try:
    from PySide2 import QtGui, QtCore, QtWidgets
except ImportError:
    from PySide6 import QtGui, QtCore, QtWidgets
import itertools, math

__all__ = [
    'SliderWidgetMixin',
    'SliderWidget',
]

def cfit(value, oldmin, oldmax, newmin, newmax):
    return max(newmin, min(newmax, newmin + float(value-oldmin) / float(oldmax-oldmin) * float(newmax-newmin)) )

def clamp01(value):
    return max(0.0,min(1.0, value))

def isint(value):
    return (float(int(value)) == float(value))

def isinrange(value, minVal, maxVal):
    return (value>=minVal and value<=maxVal)

def roundToOneDigit(val):
    sign = (1.0,-1.0)[(val<0.0)]
    val = abs(val)

    if val == 0.0:
        return 0.0

    if val<=1.0:
        for digits in range(10):
            multiplier = float(10**digits)
            bigNum = int(val*multiplier)
            if bigNum>=1:
                return sign * bigNum / multiplier
    else:
        for digits in range(10):
            multiplier = float(10**digits)
            smallNum = int(val/multiplier)
            if smallNum<10:
                return sign * smallNum*multiplier
    return None

def equalWithRelError(v1, v2, e):
    return bool( abs(v1-v2) <= e * (abs(v1) + abs(v2)) * 0.5 )

_gradientColors = {
    'YELLOW_BLUE' : [(0.0, QtGui.QColor(246.0, 192.0, 67.0)),
                      (1.0, QtGui.QColor(156.0, 203.0, 248.0))],
    'GREEN_MAGENTA' : [(0.0, QtGui.QColor(0, 150.0, 0)),
                      (1.0, QtGui.QColor(150.0, 0, 150.0))],
    'RED' : [(1.0, QtGui.QColor(150,50,50))],
    'GREEN' : [(1.0, QtGui.QColor(50,150,50))],
    'BLUE' : [(1.0, QtGui.QColor(50,50,150))],
    'BLACK_GRAY_WHITE' : [(0.0,  QtGui.QColor(25,25,25)),
                          (0.25, QtGui.QColor(50,50,50)),
                          (0.5,  QtGui.QColor(65,65,65)),
                          (0.75, QtGui.QColor(80,80,80)),
                          (1.0, QtGui.QColor(110,110,110))],
}


_tenths = [10**i for i in range(-10,10)]
_PLabelCache = {}

def GetPrioritizedLabels(minVal, maxVal, midVal = None, onlyInts = False):

    assert(minVal < maxVal)
    if midVal is not None:
        assert((minVal < midVal) and (midVal < maxVal))

    # This will get the same queries a lot, and is contributingly slow: cache.
    cacheKey = (minVal, maxVal, midVal, onlyInts)
    labels = _PLabelCache.get(cacheKey)
    if labels is not None:
        return labels
    else:
        labels = []
        _PLabelCache[cacheKey] = labels

    labelSet = set()

    # Start, End
    for val in (minVal, maxVal, midVal):
        if val is None:
            continue

        if isint(val):
            text = str(int(val))
        else:
            text = str(round(val,3))
        if text not in labelSet:
            labels.append((text, val))
            labelSet.add(text)

    # powers of 10
    maxDigits = 6
    for val in itertools.chain( (0,), [10**i for i in range(maxDigits)], [-(10**i) for i in range(maxDigits)] ):
        if not isinrange(val, minVal, maxVal):
            continue
        text  = str(int(val))
        if text not in labelSet:
            labels.append((text, val))
            labelSet.add(text)

    if not onlyInts:
        # Powers of 10 < 1.0
        maxDigits = 6
        for val in itertools.chain( [10**i for i in range(-4,0)], [-(10**i) for i in range(-4,0)]):
            if not isinrange(val, minVal, maxVal):
                continue
            text = str(val)
            text = text[:text.index('1')+1]
            if text not in labelSet:
                labels.append((text, val))
                labelSet.add(text)

    # powers of 10 x 5
    maxDigits = 6
    for val in itertools.chain( [10**i for i in range(maxDigits)], [-(10**i) for i in range(maxDigits)] ):
        val = val * 5
        if not isinrange(val, minVal, maxVal):
            continue
        text  = str(int(val))
        if text not in labelSet:
            labels.append((text, val))
            labelSet.add(text)

    if not onlyInts:
        # Powers of (10 < 1.0) x 5
        maxDigits = 6
        for val in itertools.chain( [10**i for i in range(-4,0)], [-(10**i) for i in range(-4,0)]):
            val = val * 5
            if not isinrange(val, minVal, maxVal):
                continue
            text = str(val)
            text = text[:text.index('5')+1]
            if text not in labelSet:
                labels.append((text, val))
                labelSet.add(text)

    # Walk in 1/10th of max
    posMax = max(abs(maxVal), abs(minVal))
    roundedIncrement = max([c for c in _tenths if c<posMax])
    oneDigitMax = roundToOneDigit(posMax)

    for multiplier in (5.0,1.0,0.5,0.1):
        val = oneDigitMax
        while val>minVal:
            if not isinrange(val, minVal, maxVal):
                continue

            if isint(val):
                text = str(int(val))
            else:
                text = str(round(val,3))

                if onlyInts:
                    val -= roundedIncrement*multiplier
                    continue

            if text not in labelSet:
                labels.append((text, val))
                labelSet.add(text)

            val -= roundedIncrement*multiplier

    return labels

def DoesLineSegmentIntersect(testLine, lineList, extraPadding=0):
    """
    Does the given line segment intersect any segments in the list?
    Lines are given as (start, end) tuples. The extraPadding is for either end.
    """
    for start,end in lineList:
        if testLine[0]-extraPadding < end and testLine[1]+extraPadding > start:
            return True
    return False


class SliderWidgetMixin(object):
    """
    Base slider functionality, to be shared among QWidgets and FormItems. (Abstract.)
    Concrete subclasses should provide/implement:
        fontMetrics() -> QFontMetrics
        _displayChanged(): state has been change in a way that affects display
        _valueChanged(value, final): value has been changed through UI interaction (_doDrag, _endDrag)
        _toggleComponent(): toggle between a default and the locally-assigned value
        rect() -> pixel bounds of the widget, for computing window<->value comversion
    and should call:
        _clearLabelsCache(): size changed and labels should be recomputed on next draw
            (auto-called on range/exponent changes)
        _doPaint(...)
        _toggleComponent() if _getToggleComponentEnabled() and not getReadOnly(), for click events
        _doDrag(windowLocalX) and _endDrag(windowLocalX), for dragging the slider center
    """
    def __init__(self, range=None, center=None, axisExponent=None, gradient=None, integer=None):
        self.__readOnly = False
        self.__disableComponentToggle = False

        self.__hasFocus = False
        self.__inDrag = False
        self.__isInteger = False

        self.__minVal = 0.0
        self.__maxVal = 1.0
        self.__centerVal = None # (optional)

        # This applies an exponent to the graph axis allocation.

        # 1.0 : linear allocation
        # (0.0, 1.0) : will give more allocation to numbers on the low-end (common)
        # > 1.0 : will give more allocation to numbers on the high-end
        # < 0.0: Non-sensical, not allowed

        self.__axisExponent = 1.0
        self.__splitCenter = False

        self.__value = 0.0

        self.__padding = 5
        self.__markInset = 3
        self.__color = None
        self.__gradient = None

        self.__visibleLabels = None # cache of (labelText, value, labelBounds)
        self.__labelBounds = {} # cache of (value, text) -> window bounds as (min, max)

        if range is not None:
            self.setRange(*range)
        if center is not None:
            self.setCenter(center)
        if axisExponent is not None:
            self.setAxisExponent(axisExponent)
        if gradient is not None:
            self.setGradient(gradient)
        if integer is not None:
            self.setInteger(integer)

    def setInteger(self, isInt):
        self.__isInteger = isInt
        self._displayChanged()

    def setColor(self, c):
        self.__color = c
        self._displayChanged()

    def setGradient(self, gradientName):
        """Set the slider gradient, by name, to one of the predefined gradients."""
        colors = _gradientColors.get(gradientName)
        if colors:
            self.__gradient = QtGui.QLinearGradient()
            for position, color in colors:
                self.__gradient.setColorAt(position,  color)
        else:
            self.__gradient = None
        self._displayChanged()

    def getReadOnly(self):
        return self.__readOnly

    def setReadOnly(self, readOnly, disableComponentToggle = None):
        if disableComponentToggle is None:
            disableComponentToggle = readOnly

        r = bool(readOnly)
        t = bool(disableComponentToggle)

        if self.__readOnly != r or self.__disableComponentToggle != t:
            self.__readOnly = r
            self.__disableComponentToggle = t
            self._displayChanged()

    def setHasFocus(self, hasFocus):
        f = bool(hasFocus)
        if self.__hasFocus != f:
            self.__hasFocus = bool(hasFocus)
            self._displayChanged()

    def setRange(self, minVal, maxVal):
        self.__minVal = min(minVal, maxVal)
        self.__maxVal = max(minVal, maxVal)

        if not self.__splitCenter:
            self.__computeAutoAxisExponent()
        self._clearLabelsCache()

        self._displayChanged()

    def setCenter(self, centerVal):
        self.__centerVal = centerVal

        self.__splitCenter = False
        self.__computeAutoAxisExponent()
        self._clearLabelsCache()

        self._displayChanged()

    def setAxisExponent(self, exponent):
        if exponent <= 0.0:
            raise ValueError("Exponent must be positive valued.")

        self.__axisExponent = exponent

        if self.__axisExponent is None:
            self.__splitCenter = False
            self.__computeAutoAxisExponent()
        else:
            self.__splitCenter = True
        self._clearLabelsCache()

        self._displayChanged()

    def __computeAutoAxisExponent(self):
        if self.__centerVal is None:
            self.__axisExponent = 1.0
        else:
            self.__axisExponent = math.log(0.5, cfit(self.__centerVal, self.__minVal, self.__maxVal, 0.0, 1.0))

    def isPreselectionActive(self):
        if (self.__hasFocus or self.__inDrag) and (not self.__readOnly):
            return True
        return False

    #########
    #
    # Data model
    #

    def setValue(self, value):
        if value == self.__value:
            return
        self.__value = value
        self._valueChanged(self.__value, True)
        self._displayChanged()

    def getValue(self):
        return self.__value


    # component value is mapped to output space. [-10,1000]
    def normalizedValueToValue(self, normValue):
        if self.__splitCenter and self.__centerVal is not None:
            # This does a split fit around the center point
            if normValue>0.5:
                altNorm = cfit(normValue, 0.5, 1.0, 0.0, 1.0)
                altNorm = altNorm ** (1.0/self.__axisExponent) # Apply axis exponent in norm space
                normValue = cfit(altNorm, 0.0, 1.0, 0.5, 1.0)

                value = cfit(normValue, 0.5, 1.0, self.__centerVal, self.__maxVal)
            else:
                altNorm = cfit(normValue, 0.0, 0.5, 0.0, 1.0)
                altNorm = 1.0-((1.0-altNorm) ** (1.0/self.__axisExponent)) # Apply axis exponent in norm space
                normValue = cfit(altNorm, 0.0, 1.0, 0.0, 0.5)

                value = cfit(normValue, 0.0, 0.5, self.__minVal, self.__centerVal)
        else:
            normValue = normValue ** (1.0/self.__axisExponent) # Apply axis exponent in norm space
            value = cfit(normValue, 0.0, 1.0, self.__minVal, self.__maxVal)

        if self.__isInteger:
            # We round this on purpose, to make the drag-regions
            # for each number centered on the integers
            value = int(round(value))

        return value

    def valueToNormalizedValue(self, value):
        if self.__isInteger:
            # We don't round this on purpose, to make a displayed value
            # agree with an interpreted value
            value = int(value)

        if self.__splitCenter and self.__centerVal is not None:
            # This does a split fit around the center point, with gamma applied individually to each half
            if value > self.__centerVal:
                normValue = cfit(value, self.__centerVal, self.__maxVal, 0.5, 1.0)

                altNorm = cfit(normValue, 0.5, 1.0, 0.0, 1.0)
                altNorm = altNorm ** self.__axisExponent # Apply axis exponent in norm space
                normValue = cfit(altNorm, 0.0, 1.0, 0.5, 1.0)
            else:
                normValue = cfit(value, self.__minVal, self.__centerVal, 0.0, 0.5)
                altNorm = cfit(normValue, 0.0, 0.5, 0.0, 1.0)
                altNorm = 1.0-((1.0-altNorm) ** self.__axisExponent) # Apply axis exponent in norm space
                normValue = cfit(altNorm, 0.0, 1.0, 0.0, 0.5)
        else:
            normValue = cfit(value, self.__minVal, self.__maxVal, 0.0, 1.0)
            normValue = normValue ** self.__axisExponent  # Apply axis exponent in norm space

        return normValue

    # normalized value is [0,1]
    # this corresponds to position along the slider range
    def normalizedValueToWindowPosition(self, normValue):
        sliderWidth = self.rect().width() - 2*self.__padding
        sliderOffset = self.__padding + self.rect().left()
        return int( round( sliderOffset + (sliderWidth-1.0)*clamp01(normValue) ) )

    def windowPositionToNormalizedValue(self, pos):
        pos = int(pos)
        sliderWidth = self.rect().width() - 2*self.__padding
        sliderOffset = self.__padding + self.rect().left()
        return clamp01( (pos - sliderOffset) / (sliderWidth - 1.0) )

    def valueToWindowPosition(self, value):
        normValue = self.valueToNormalizedValue( value )
        return self.normalizedValueToWindowPosition( normValue )

    def windowPositionToValue(self, pos, applyLabelSnapping = True):
        pos = int(pos)
        if applyLabelSnapping and self.__visibleLabels:
            snappingRange = 2
            for labelText, labelValue, bounds in self.__visibleLabels:
                labelPos = self.valueToWindowPosition( labelValue )
                if abs(labelPos-pos) <= snappingRange:
                    return labelValue

        normValue = self.windowPositionToNormalizedValue(pos)
        value = self.normalizedValueToValue(normValue)

        # Do dynamic snapping (make the resulted values as 'pretty' as possible.
        # I.e., round to the coarsest value, that when converted back, still yields the same integer pixel
        # Both are correct answers, but the pretty one is more convenient

        for digits in range(10):
            roundedValue = round(value, digits)
            if int(self.valueToWindowPosition(roundedValue)) == int(pos):
                value = roundedValue
                break

        return value

    #########
    #
    # Event Handling
    #
    #

    def _toggleComponent(self):
        pass

    def _getToggleComponentEnabled(self):
        return not self.__disableComponentToggle

    def _isInDrag(self):
        return self.__inDrag

    def _doDrag(self, windowLocalX):
        if self.__readOnly: return
        self.__inDrag = True
        self.__value = self.windowPositionToValue(windowLocalX)

        self._valueChanged(self.__value, False)
        self._displayChanged()

    def _endDrag(self, windowLocalX):
        if self.__readOnly or not self.__inDrag:
            return

        self.__inDrag = False
        self.__value = self.windowPositionToValue(windowLocalX)

        self._valueChanged(self.__value, True)
        self._displayChanged()


    #########
    #
    # Drawing
    #

    def _doPaint(self, p, palette):
        rect = self.rect()

        # Set up geometry
        fontHeight = self.fontMetrics().height()
        verticalFontPadding = 2
        maxMarkHeight = 10
        widgetHeight = maxMarkHeight + verticalFontPadding + fontHeight
        verticalMargin = (rect.height() - widgetHeight)/2.0

        centerLine_y = verticalMargin + maxMarkHeight/2 + 4

        rect.center().y()
        centerLine_x0 = self.normalizedValueToWindowPosition(0.0)
        centerLine_x1 = self.normalizedValueToWindowPosition(1.0)
        centerLine_width = centerLine_x1 - centerLine_x0
        if centerLine_width<8:
            return

        # Compute colors
        fgColor = self.__color
        if fgColor is None:
            fgColor = palette.light().color()

        if self.__readOnly:
            textColor = QtGui.QColor(palette.text().color())
            textColor.setAlpha(64)
            hilightedTextColor = QtGui.QColor(textColor)
            hilightedTextColor.setAlpha(160)
            dimTickColor = QtGui.QColor(fgColor)
            dimTickColor.setAlpha(64)
            markFillColor = QtGui.QColor(palette.color(QtGui.QPalette.Window))
            markOutlineColor = QtGui.QColor(palette.light().color())
        else:
            textColor = QtGui.QColor(palette.color(QtGui.QPalette.BrightText))
            textColor.setAlpha(128)
            hilightedTextColor = QtGui.QColor(textColor)
            hilightedTextColor.setAlpha(230)
            dimTickColor = QtGui.QColor(fgColor)
            dimTickColor.setAlpha(128)

            markFillColor = QtGui.QColor(palette.color(QtGui.QPalette.Window)).lighter(150)
            markOutlineColor = QtGui.QColor(palette.light().color())

            if self.__inDrag:
                markFillColor = markFillColor.lighter(180)
                markOutlineColor = markOutlineColor.lighter(180)
            elif self.isPreselectionActive():
                markOutlineColor = markOutlineColor.lighter(120)

        tickPen = QtGui.QPen(fgColor, 1)
        textPen = QtGui.QPen(textColor, 1)
        hilightedTextPen = QtGui.QPen(hilightedTextColor, 1)
        dimTickPen = QtGui.QPen(dimTickColor, 1)
        markOutlinePen = QtGui.QColor( markOutlineColor )


        # Determine which labels should be visible based on space constraints
        # TODO calculating visible labels is slow, and is the main contributor to (non-cache-hit) draws
        if self.__visibleLabels is None:
            filledAreas = []
            self.__visibleLabels = []
            textMargin = 25

            for labelText, value in GetPrioritizedLabels(self.__minVal, self.__maxVal, self.__centerVal, self.__isInteger):
                # TODO lots of iterations over this loop -> lots of time spent in __measureLabelBounds (most of label computation time)
                bounds = self.__measureLabelBounds(value, labelText)
                if DoesLineSegmentIntersect(bounds, filledAreas, textMargin):
                    continue
                filledAreas.append(bounds)
                self.__visibleLabels.append( (labelText, value, bounds) )


        if self.__gradient:
            # TODO gradient drawing is about 1:7 v. uncached label calculation, and about 1:1 with cached
            self.__gradient.setStart(centerLine_x0, 0.0)
            self.__gradient.setFinalStop(centerLine_x1, 0.0)

            gradHeight = 12

            # Draw label ticks on bottom
            p.setPen(dimTickPen)
            for labelText, value, bounds in self.__visibleLabels:
                x = self.valueToWindowPosition( value )
                p.drawLine(x, centerLine_y-gradHeight-1, x, centerLine_y+3)

            # Overlay the gradient
            p.fillRect(QtCore.QRectF(centerLine_x0, centerLine_y-gradHeight, centerLine_width+1, gradHeight), self.__gradient)

            # TODO tick drawing is about 1:1 with gradient drawing
            # Draw the bottom axis
            tickHeight = 3
            p.setPen(dimTickPen)
            p.drawLine(centerLine_x0, centerLine_y, centerLine_x1, centerLine_y)

            # Finally, draw the text labels
            for labelText, value, bounds in self.__visibleLabels:
                pen = textPen
                if self.__value is not None and equalWithRelError(value, self.__value,1e-9):
                    pen = hilightedTextPen
                self.__drawLabelText(p, value, labelText, centerLine_y, pen, bounds)
        else:
            # TODO tick drawing is about 1:1 with gradient drawing
            p.setPen(tickPen)
            p.drawLine(centerLine_x0, centerLine_y, centerLine_x1, centerLine_y)

            tickHeight = 3
            for labelText, value, bounds in self.__visibleLabels:
                x = self.valueToWindowPosition( value )

                p.setPen(tickPen)
                p.drawLine(x, centerLine_y-tickHeight, x, centerLine_y+tickHeight)

                pen = textPen
                if self.__value is not None and equalWithRelError(value, self.__value,1e-9):
                    pen = hilightedTextPen

                self.__drawLabelText(p, value, labelText, centerLine_y, pen, bounds)


        # Draw Mark
        if self.__value is not None:
            vOffset = 1
            x = int(self.valueToWindowPosition( self.__value ))
            markHeight = maxMarkHeight/2

            yBottom = centerLine_y+maxMarkHeight/2-vOffset
            yTop = centerLine_y-maxMarkHeight/2-vOffset

            poly = QtGui.QPolygonF()
            poly.append( QtCore.QPointF(x, yBottom) )
            poly.append( QtCore.QPointF(x+2, yBottom-2) )
            poly.append( QtCore.QPointF(x+2, yTop) )
            poly.append( QtCore.QPointF(x-2, yTop) )
            poly.append( QtCore.QPointF(x-2, yBottom-2) )

            p.setPen(markOutlinePen)
            p.setBrush(markFillColor)
            p.drawConvexPolygon(poly)


    def _clearLabelsCache(self):
        self.__visibleLabels = None
        self.__labelBounds = {}

    def __measureLabelBounds(self, value, text):
        """
        @return the window x-value range the label text covers as a tuple
        """
        cacheKey = (value, text)
        bounds = self.__labelBounds.get(cacheKey)
        if bounds is None:
            bounds = [None, None]
            self.__labelBounds[cacheKey] = bounds
        else:
            return bounds

        textWidth = self.fontMetrics().horizontalAdvance(text)
        normValue = self.valueToNormalizedValue(value)
        x = self.normalizedValueToWindowPosition( normValue)

        if equalWithRelError(normValue,0.0,1e-3):
            bounds[0], bounds[1] = (x, x + textWidth)
        elif equalWithRelError(normValue,1.0,1e-3):
            bounds[0], bounds[1] = (x - textWidth, x)
        else:
            bounds[0], bounds[1] = (x - textWidth/2.0, x + textWidth/2.0)
        return bounds

    def __drawLabelText(self, painter, value, text,
                        centerLine_y,
                        textPen,
                        labelBounds):
        painter.setPen( textPen )
        point = QtCore.QPointF(labelBounds[0], centerLine_y+self.fontMetrics().height())
        painter.drawText(point, text)



class SliderWidget(QtWidgets.QWidget, SliderWidgetMixin):
    SIG_TOGGLE_COMPONENT = QtCore.Signal()
    SIG_VALUE_CHANGED = QtCore.Signal(float, bool)
    SIG_RESET_TRIGGERED = QtCore.Signal()

    def __init__(self, parent, fontScale=None, **kwargs):
        QtWidgets.QWidget.__init__(self, parent)
        SliderWidgetMixin.__init__(self, **kwargs)

        if fontScale is not None:
            newFont = QtGui.QFont(self.font())
            if newFont.pointSize() > 0:
                newFont.setPointSizeF(newFont.pointSize()*fontScale)
            else:
                newFont.setPixelSize(int(newFont.pixelSize()*fontScale))
            self.setFont(newFont)

    ###
    # Painting

    def _displayChanged(self):
        self.update()

    def resizeEvent(self, ev):
        QtWidgets.QWidget.resizeEvent(self, ev)
        self._clearLabelsCache()

    def paintEvent(self, ev):
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
        self._doPaint(p, self.palette())

    ###
    # Events

    def _valueChanged(self, value, final):
        self.SIG_VALUE_CHANGED.emit(value, final)

    def _toggleComponent(self):
        self.SIG_TOGGLE_COMPONENT.emit()

    def mousePressEvent(self, ev):
        if bool(ev.modifiers() & QtCore.Qt.ControlModifier) and ev.button() == QtCore.Qt.LeftButton:
            self.SIG_RESET_TRIGGERED.emit()
            return

        if bool(ev.modifiers() & QtCore.Qt.ControlModifier) and self._getToggleComponentEnabled():
            self._toggleComponent()
            return

        if bool(ev.buttons() & QtCore.Qt.LeftButton) and not self.getReadOnly():
            self.setCursor(QtCore.Qt.BlankCursor)
            self._doDrag(ev.x())

    def mouseMoveEvent(self, ev):
        if ev.modifiers() == QtCore.Qt.NoModifier and bool(ev.buttons() & QtCore.Qt.LeftButton):
            self._doDrag(ev.x())

    def mouseReleaseEvent(self, ev):
        if ev.modifiers() == QtCore.Qt.NoModifier:
            self._endDrag(ev.x())

            self.unsetCursor()

    def enterEvent(self, ev):
        if not self.getReadOnly():
            self.setHasFocus(True)

    def leaveEvent(self, ev):
        if not self.getReadOnly():
            self.setHasFocus(False)

    ###
    # Spacing

    def sizePolicy(self):
        return QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)

    def sizeHint(self):
        return QtCore.QSize(128,12)



import sys
if __name__ == '__main__':
    theApp = QtWidgets.QApplication(sys.argv)
    # import DarkMojo
    # theApp.setPalette(DarkMojo.DarkMojoPalette())

    w = SliderWidget(None)

    @QtCore.Slot(float, bool)
    def callback(value, final):
        print(value, final)
    w.SIG_VALUE_CHANGED.connect(callback)

    w.show()
    theApp.lastWindowClosed.connect(theApp.quit)
    theApp.exec_()
