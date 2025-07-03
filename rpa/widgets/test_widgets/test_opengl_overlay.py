import sys
import numpy as np
from PySide2 import QtWidgets, QtGui, QtCore, QtOpenGL
from OpenGL.GL import *

class HtmlTextureRenderer:
    def __init__(self,  size=(512, 256)):
        self.size = size

    def render_html_to_image(self, html):
        doc = QtGui.QTextDocument()
        doc.setHtml(html)
        doc.setTextWidth(self.size[0])

        image = QtGui.QImage(self.size[0], self.size[1], QtGui.QImage.Format_ARGB32)
        image.fill(QtCore.Qt.transparent)

        painter = QtGui.QPainter(image)
        doc.drawContents(painter)
        painter.end()

        return image

    def qimage_to_gl_texture(self, image):
        ptr = image.bits()
        ptr.setsize(image.byteCount())
        img_array = np.array(ptr).reshape((image.height(), image.width(), 4))

        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width(), image.height(), 0,
                     GL_BGRA, GL_UNSIGNED_BYTE, img_array)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        return tex_id


class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, html, parent=None):
        super().__init__(parent)
        self.setMinimumSize(800, 600)
        self.texture_id = None
        self.html_renderer = HtmlTextureRenderer()

    def initializeGL(self):
        glEnable(GL_TEXTURE_2D)
        image = self.html_renderer.render_html_to_image()
        self.texture_id = self.html_renderer.qimage_to_gl_texture(image)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, w, h, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        w, h = self.html_renderer.size

        # Draw the texture as a quad
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex2f(50, 50)
        glTexCoord2f(1.0, 0.0)
        glVertex2f(50 + w, 50)
        glTexCoord2f(1.0, 1.0)
        glVertex2f(50 + w, 50 + h)
        glTexCoord2f(0.0, 1.0)
        glVertex2f(50, 50 + h)
        glEnd()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        html = """
            <div style="color:white; background-color: rgba(0, 0, 0, 0.5); padding: 10px;">
                <h2>Hello OpenGL</h2>
                <p>This text is <b>HTML</b> rendered to a texture.</p>
                <p style="color:red;">Red <i>italic</i> words!</p>
            </div>
        """
        self.setCentralWidget(GLWidget(html))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.setWindowTitle("Render HTML as OpenGL Texture")
    win.show()
    sys.exit(app.exec_())