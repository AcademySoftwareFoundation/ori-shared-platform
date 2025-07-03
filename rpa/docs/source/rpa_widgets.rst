RPA Widgets
===========

.. contents::
   :local:
   :depth: 1

==========================
Where are the RPA widgets?
==========================

RPA Widgets
-----------

You can find all the RPA widgets in the root level of,
**./widgets/**

Sub Widgets
-----------

The sub-widgets that are used by more than 1 RPA widgets are here,
**./widgets/sub_widgets/**

Test Widgets
------------

The test-widgets that are used to semi-automatically test RPA modules and many of the core RPA widgets are here,
**./widgets/test_widgets/**

By default the test widgets are commented out in, **./open_rv/pkgs/rpa_widgets_pkg/rpa_widgets_mode.py** under the RpaWidgetsMode class's self.init call.
Kindly un-comment them and set the following environment variable to point to a folder containing media to use
for testing,

.. code-block:: shell

   setenv env TEST_MEDIA_DIR /path/to/test/media

In your path to test media, kindly have 9 mp4 files which are named,
one.mp4, two.mp4, three.mp4, four.mp4, five.mp4, six.mp4, seven.mp4, eight.mp4, nine.mp4

And have one png file,
one.png

=============================
How to create an RPA widget ?
=============================

To get started with creating RPA widgets, you can look at MediaPathOverlay RPA widget,
**./widgets/media_path_overlay/media_path_overlay.py**
It is a simple RPA widget that overlays the media-path of the current clip in your forground playlist.

Anatomy of an RPA widget
------------------------

A RPA widget will take in rpa and main_window as the arguments in it's __init__ method.

.. code-block:: python

   class MediaPathOverlay(QtWidgets.QWidget):

      def __init__(self, rpa, main_window):
         super().__init__(main_window)        
         self.__rpa = rpa

**rpa** - A RPA widget needs to get an instance of RPA to start manipulating the RPA session.
**main_window** - And it needs an instance of the PySide MainWindow to which it needs to be parented to.


================================================
How to make RPA widgets available inside of RV ?
================================================

Since RPA widgets are PySide widgets and RV allows us to create RV Packages with PySide widgets, we can create RV packages that import and use these RPA widgets.

As an example you can see how the following RV Package loads all the RPA widgets,
**./open_rv/pkgs/rpa_widgets_pkg/rpa_widgets_mode.py**
