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


class HTML:

	@staticmethod
	def removeTags(s):
	  tag = False
	  quote = False
	  out = ""
	  for c in s:
	    if c == '<' and not quote:
	      tag = True
	    elif c == '>' and not quote:
	      tag = False
	    elif (c == '"' or c == "'") and tag:
	      quote = not quote
	    elif not tag:
	      out = out + c
	  return out


class Browser:
    # Ventana del programa
    def __init__(self):

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_default_size(940, 600)
        self.window.connect("destroy", self.on_quit)

        self.mListItem = []

        # Un vBox, en la parte de arriba hay una caja para ingresar
        # la direccion web, y abago se muestra la pagina
        vbox = gtk.VBox()

        # La parte de la entrada de la url
        self.url_text = gtk.Entry()
        self.url_text.connect('activate', self.url_text_activate)

        self.mTextEdit = gtk.Entry()

        self.mComboBoxOutput = gtk.combo_box_new_text()

        self.mButtonCatch = gtk.Button(label='Catch the product')
        self.mButtonCatch.connect('clicked', self.onButtonCatchClicked)

        self.mButtonSendToServer = gtk.Button(label='Send to server')
        self.mButtonSendToServer.connect('clicked', self.onButtonSendToServerClicked)

        self.mButtonDelete = gtk.Button(label='Delete')
        self.mButtonDelete.connect('clicked', self.onButtonDeleteClicked)

        # La parte en donde se muestra la pagina que se visita (con scroll incluido)
        self.scroll_window = gtk.ScrolledWindow()
        self.webview = WebView()
        self.webview.connect('load-started', self.webviewStarted)
        self.webview.connect('load-finished', self.webviewFinished)
        self.scroll_window.add(self.webview)

        # Unimos todo en el vBox
        vbox.pack_start(self.url_text, fill=False, expand=False)
        vbox.pack_start(self.mTextEdit, fill=False, expand=False)
        vbox.pack_start(self.mComboBoxOutput, fill=True, expand=False)
        vbox.pack_start(self.mButtonCatch, fill=False, expand=False)
        vbox.pack_start(self.mButtonSendToServer, fill=False, expand=False)
        vbox.pack_start(self.mButtonDelete, fill=False, expand=False)

        # El expand=False al empaquetarlo es para que el entry no ocupe media pantalla

        vbox.pack_start(self.scroll_window, True, True)
        self.window.add(vbox)
        self.window.show_all()


    def webviewStarted(self, mObject, mObject2):
        self.setTitle('Loading ...')
        pass

    def webviewFinished(self, mObject, mObject2):
        self.setTitle('Finished!')
        pass

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

        return HTML.removeTags(mData)


    def onButtonSendToServerClicked(self, mButton):

        if len(self.mListItem)>0:
            self.mComboBoxOutput.set_active(0)

        if self.mComboBoxOutput.get_active() >= 0:
            mSize = len(self.mListItem)
            for mIndex in range(len(self.mListItem)):
                try:
                    self.setTitle('Sending to server %s of %s' % (mIndex + 1, mSize))
                    #sending data to server.
                    self.sendToServer(self.mComboBoxOutput.get_active())
                    #removing temp data.
                    self.mListItem.pop(self.mComboBoxOutput.get_active())
                    self.mComboBoxOutput.remove_text(self.mComboBoxOutput.get_active())
                    self.mComboBoxOutput.set_active(0)
                except:
                    pass

            self.messageBox('Finished', True)

        else:
            self.messageBox('Select one product before!')
        pass


    def onButtonCatchClicked(self, mButton):

        mLinkStartIndex = self.webview.get_html().rfind('<div id="wrap"')
        mNameStartIndex = self.webview.get_html().rfind('id="zoom"')
        mDescriptionStartIndex = self.webview.get_html().rfind('id="product_tabs_description_tabbed_contents" style="">')

        if mLinkStartIndex == -1:
            self.messageBox('Product not found!')
            return

        mLink = self.findAndGetOnHtml(self.webview.get_html(), mLinkStartIndex,
                mStartString='href="', mEndString='"', mClearBeginning=True)
        mName = self.findAndGetOnHtml(self.webview.get_html(),
                mStartIndex=mNameStartIndex, mStartString='alt="', mEndString='" style',
                mClearBeginning=True)
        mDescription = self.findAndGetOnHtml(self.webview.get_html(),
                mStartIndex=mDescriptionStartIndex, mStartString='class="std">', mEndString='</div>',
                mClearBeginning=True)


        if [mName, mLink, mDescription] in self.mListItem:
            self.messageBox('This product has already been added!')
            return

        self.mListItem.append([mName, mLink, mDescription])
        self.mComboBoxOutput.append_text(mName)
        print mName, '\n',mLink,'\n',mDescription
        self.messageBox('The product has gotten successfully!', True)
        pass


    def sendToServer(self, mIndex):

        mUrl = self.mTextEdit.get_text()
        mUrl += '/amadeli/product/add_via_short_mode?'
        import urllib2, urllib
        mData = {}
        mData['mName'] = self.mListItem[mIndex][0]
        mData['mImageUrl'] = self.mListItem[mIndex][1]
        mData['mDescription'] = self.mListItem[mIndex][3]
        mUrl += urllib.urlencode(mData)
        print urllib2.urlopen(mUrl)


    def onButtonDeleteClicked(self, mButton):

        if self.mComboBoxOutput.get_active() >= 0:
            self.mListItem.pop(self.mComboBoxOutput.get_active())
            self.mComboBoxOutput.remove_text(self.mComboBoxOutput.get_active())
            self.messageBox('Deleted successfully!', True)
        else:
            self.messageBox('Select one product before!')
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

    def setTitle(self, mData=''):
        self.window.set_title("Cracking VipFolheados - Status: %s" % mData)

    # La funcion magica que abre la url que se le pasa
    def open_url(self, url="https://vipfolheados.com.br/", mServerUrl = "http://fsi-deployment.ddns.net/amadeli"):
        # cambia el titulo de la ventana
        self.setTitle(url)
        # mostramos la direccion de la pagina abierta en el entry
        self.url_text.set_text(url)
        self.mTextEdit.set_text(mServerUrl)
        # abre la pagina
        self.webview.open(url)

if __name__ == "__main__":
    browser = Browser()
    # abrimos la pagina de inicio (opcional)
    #browser.open_url()
    browser.open_url("https://vipfolheados.com.br/anel-fundido-com-5-zirconias-aro-torcido-com-laco-03-1691.html")

    gtk.main()
