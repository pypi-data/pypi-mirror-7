Vincent-Qt
==========
The folks at Trifacta are making it easy to build visualizations on top of D3 with Vega. Vincent makes it easy to build Vega with Python. Vincent-Qt makes it easy to use Vincent in QtWidgets applications.

Installation
------------
.. code:: sh

   $ pip install vincent_qt

Usage
-----
Create `QWebView` object, plot something with Vincent then call function display:

.. sourcecode:: python

   from vincent_qt import vincent_qt
   web_view = QWebView()
   plot = vincent.Line(data)
   vincent_qt.display(web_view, plot)