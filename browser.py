#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Escrito por Daniel Fuentes B.
# Licencia: BSD <http://www.opensource.org/licenses/bsd-license.php>

import pygtk
pygtk.require("2.0")
import gtk
import webkit


class WebView(webkit.WebView):
    def get_html(self):
        self.execute_script('oldtitle=document.title;document.title=document.documentElement.innerHTML;')
        html = self.get_main_frame().get_title()
        self.execute_script('document.title=oldtitle;')
        return html





class Browser:
    # Ventana del programa
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_default_size(940, 600)
        self.window.connect("destroy", self.on_quit)

        self.mListLinks = []

        # Un vBox, en la parte de arriba hay una caja para ingresar
        # la direccion web, y abago se muestra la pagina
        vbox = gtk.VBox()

        # La parte de la entrada de la url
        self.url_text = gtk.Entry()
        self.url_text.connect('activate', self.url_text_activate)

        self.mComboBoxOutput = gtk.combo_box_new_text()

        self.mButtonCatch = gtk.Button(label='Catch the picture')
        self.mButtonCatch.connect('clicked', self.onButtonCatchClicked)

        self.mButtonOpen = gtk.Button(label='Save the image selected')
        self.mButtonOpen.connect('clicked', self.onButtonOpenClicked)

        self.mButtonDelete = gtk.Button(label='Delete')
        self.mButtonDelete.connect('clicked', self.onButtonDeleteClicked)

        # La parte en donde se muestra la pagina que se visita (con scroll incluido)
        self.scroll_window = gtk.ScrolledWindow()
        self.webview = WebView()
        self.scroll_window.add(self.webview)

        # Unimos todo en el vBox
        vbox.pack_start(self.url_text, fill=True, expand=False)
        vbox.pack_start(self.mComboBoxOutput, fill=True, expand=False)
        vbox.pack_start(self.mButtonCatch, fill=False, expand=False)
        vbox.pack_start(self.mButtonOpen, fill=False, expand=False)
        vbox.pack_start(self.mButtonDelete, fill=False, expand=False)

        # El expand=False al empaquetarlo es para que el entry no ocupe media pantalla

        vbox.pack_start(self.scroll_window, True, True)
        self.window.add(vbox)
        self.window.show_all()


    def messageBox(self, mMessage, mIsInfo=False):
        parent = None
        if mIsInfo:
            mType = gtk.MESSAGE_INFO
        else:
            mType = gtk.MESSAGE_WARNING
        md = gtk.MessageDialog(parent,
        gtk.DIALOG_DESTROY_WITH_PARENT, mType,
        gtk.BUTTONS_CLOSE, mMessage)
        md.connect("response", self.dialog_response)
        md.run()

    def dialog_response(self, widget, response_id):
        widget.destroy()

    def findAndGetOnHtml(self, mBuffer, mStartIndex = 0, mStartString = '', mEndString='', mClearBeginning=False):
        mData = ""
        mStarted = False
        mClearCount = -1
        for mIndex in range(mStartIndex, len(mBuffer)):

            if mClearCount >=0:
                mClearCount -=1
                continue

            if not mStarted:
                if mBuffer[mIndex+1: mIndex+len(mStartString)+1] == mStartString:
                    mStarted = True
                    mData += mBuffer[mIndex]
                    if mClearBeginning:
                        mClearCount = len(mStartString)-1
                    continue
            else:
                if mBuffer[mIndex:mIndex+len(mEndString)] == mEndString:
                    break
                else:
                    mData += mBuffer[mIndex]

        return mData



    def onButtonCatchClicked(self, mButton):

        mLinkStartIndex = self.webview.get_html().rfind('<div id="wrap"')
        mNameStartIndex = self.webview.get_html().rfind('id="zoom"')

        if mLinkStartIndex == -1:
            self.messageBox('Image not found!')
            return

        mLink = self.findAndGetOnHtml(self.webview.get_html(), mLinkStartIndex,
                mStartString='href="', mEndString='"', mClearBeginning=True)
        mName = self.findAndGetOnHtml(self.webview.get_html(),
                mStartIndex=mNameStartIndex, mStartString='alt="', mEndString='" style',
                mClearBeginning=True)

        if [mName, mLink] in self.mListLinks:
            self.messageBox('This image has already been added!')
            return
        self.mListLinks.append([mName, mLink])
        self.mComboBoxOutput.append_text(mName)
        print mName, '\n',mLink
        self.messageBox('Image gotten successfully!', True)
        pass


    def onButtonOpenClicked(self, mButton):

            if self.mComboBoxOutput.get_active() == -1:
                self.messageBox('Select one image before!')
                return

            if gtk.pygtk_version < (2,3,90):
               print "PyGtk 2.3.90 or later required for this example"
               raise SystemExit

            dialog = gtk.FileChooserDialog("Save the image", None,
                 gtk.FILE_CHOOSER_ACTION_SAVE, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                 gtk.STOCK_OK, gtk.RESPONSE_OK))

            filter = gtk.FileFilter()
            filter.set_name("Images")
            filter.add_mime_type("image/png")
            filter.add_mime_type("image/jpeg")
            filter.add_pattern("*.png")
            filter.add_pattern("*.jpg")
            dialog.add_filter(filter)

            dialog.set_current_name(self.mListLinks[self.mComboBoxOutput.get_active()][0])

            response = dialog.run()
            if response == gtk.RESPONSE_OK:
                print dialog.get_filename()
                self.downloadAndSave(dialog.get_filename(), self.mListLinks[self.mComboBoxOutput.get_active()][1])
                self.mListLinks.pop(self.mComboBoxOutput.get_active())
                self.mComboBoxOutput.remove_text(self.mComboBoxOutput.get_active())
                self.messageBox('Downloaded successfully!', True)
            elif response == gtk.RESPONSE_CANCEL:
                print 'Closed, no files selected'
            dialog.destroy()
            pass


    def downloadAndSave(self, mFilename, mUrl):

        if not mFilename.endswith('.png') or not mFilename.endswith('.jpg'):
            mFilename += mUrl[-4:]

        import urllib2
        mFile = urllib2.urlopen(mUrl)
        with open(mFilename,'wb') as output:
          output.write(mFile.read())


    def onButtonDeleteClicked(self, mButton):

        if self.mComboBoxOutput.get_active() >= 0:
            self.mListLinks.pop(self.mComboBoxOutput.get_active())
            self.mComboBoxOutput.remove_text(self.mComboBoxOutput.get_active())
            self.messageBox('Deleted successfully!', True)
        else:
            self.messageBox('Select one image before!')
        pass


    # Definimos las señales y demas cosas de la ventana:
    def url_text_activate(self, entry):
    # al activar el entry (por ejemplo al hacer enter), se obtiene el
    # texto de la entry (la url) y se activa la funcion que abre la url
        self.open_url(entry.get_text())
        #self.update_combobox_output(entry.get_text())


    def update_combobox_output(self, mData=''):
        '''
        self.mComboBoxOutput.append_text(mData)
        mFile = open('log.txt', 'w')
        mFile.write(self.webview.get_html())
        mFile.close()
        '''
        pass


    def on_quit(self, widget):
        gtk.main_quit()

    # La funcion magica que abre la url que se le pasa
    def open_url(self, url):
        "Funcion que carga la pagina elegida"
        # cambia el titulo de la ventana
        self.window.set_title("Cracking VipFolheados - %s" % url)
        # mostramos la direccion de la pagina abierta en el entry
        self.url_text.set_text(url)
        # abre la pagina
        self.webview.open(url)

if __name__ == "__main__":
    browser = Browser()
    # abrimos la pagina de inicio (opcional)
    #browser.open_url("https://vipfolheados.com.br/")
    browser.open_url("https://vipfolheados.com.br")
    gtk.main()
