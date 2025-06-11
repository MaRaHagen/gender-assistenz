import uno
import json
import urllib.request
# uno
import unohelper
from com.sun.star.awt import Selection, XDialogEventHandler
from com.sun.star.awt.FontWeight import NORMAL as W_NORMAL, BOLD as W_BOLD
from com.sun.star.awt.FontSlant import NONE as SL_NONE, ITALIC as SL_ITALIC
from com.sun.star.awt.FontUnderline import NONE as UL_NONE, SINGLE as UL_SINGLE
from com.sun.star.awt.MessageBoxType import ERRORBOX, INFOBOX
from com.sun.star.beans import PropertyValue
from com.sun.star.container import ElementExistException
from com.sun.star.document import XUndoAction
from com.sun.star.drawing.FillStyle import SOLID as FS_SOLID  # , NONE as FS_NONE
from com.sun.star.lang import Locale
from com.sun.star.sheet.CellFlags import STRING as CF_STRING
from com.sun.star.task import XJobExecutor
from com.sun.star.xml import AttributeData
from com.sun.star.task import XJobExecutor
from com.sun.star.awt.MessageBoxButtons import BUTTONS_YES_NO
from com.sun.star.awt.MessageBoxType import MESSAGEBOX


class GenderAssist(unohelper.Base, XJobExecutor):
    def __init__(self, ctx):
        try:
            self.ctx = ctx
            self.sm = ctx.ServiceManager
            self.desktop = self.ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.frame.Desktop", self.ctx)
            self.doc = self.desktop.getCurrentComponent()
            self.selection = None
            self.frame = self.doc.CurrentController.Frame
        except Exception:
            print(Exception)
            print("GenderAssist Wurde nicht initialisiert")


    def trigger(self, arg):
        doc = self.doc
        if not doc or not hasattr(doc, "Text"):
            self.msgbox("Kein Text")
            return
        try:
            getattr(self, 'do_' + arg)()
        except Exception:
            print(Exception.__cause__)
            print(f"Error triggering < self.do_{arg}() > function:")
            raise
        
        
    def msgbox(self, message, boxtype=ERRORBOX, title="Error"):
        '''Simple UNO message box for notifications at user.'''
        win = self.frame.ContainerWindow
        box = win.Toolkit.createMessageBox(win, boxtype, 1, title, message)
        return box.execute()

    def do_highlight(self):
        doc = self.doc
        text = doc.Text.getString()
        if not text:
            self.msgbox("Kein Text")
            return
        # 2. Anfrage an lokalen Server
        url = "http://localhost:8080/analyze"
        req = urllib.request.Request(
            url,
            data=text.encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req) as response:
                response_data = json.loads(response.read().decode("utf-8"))
                infos = response_data.get("infos", "")
                print(str(infos))
        except Exception:
            self.msgbox(f"Fehler bei der Serververbidnung")
            raise Exception
        corrections_to_apply = []

        for eintrag in infos:
            if eintrag.get("possibleCorrections"):
                first_corr = eintrag["possibleCorrections"][0]
                for change in first_corr["changes"]:
                    corrections_to_apply.append({
                        "word": eintrag["word"],
                        "from": change["from"],
                        "to": change["to"],
                        "replacement": change["replace_with"].replace("?I", "*i").replace('?','*')
                    })

        # Sortierung nach 'from' absteigend, um Ersetzungen von hinten nach vorne vorzunehmen
        corrections_to_apply.sort(key=lambda x: x["from"], reverse=False)

        offset = 0
        # Text anpassen
        for c in corrections_to_apply:
            text = text[:c["from"]] + c["replacement"] + text[c["to"]:]
            if self.highlight_and_confirm(c["from"]+offset, c["to"]+offset, c["replacement"]):
                offset += len(c["replacement"]) - (c["to"] - c["from"])



        # In Dokument einfügen
        text_range = doc.Text.End
        text_range.setString("\n\n--- Gender-Assistent Vorschlag ---\n" + text)
        return

    def ask_user_confirmation(self, title, message):
        """Zeigt ein Ja/Nein-Fenster und gibt True bei Ja, False bei Nein zurück."""
        window = self.frame.ContainerWindow
        toolkit = window.getToolkit()
        box = toolkit.createMessageBox(
            window,
            MESSAGEBOX,
            BUTTONS_YES_NO,
            title,
            message
        )
        result = box.execute()
        return result == 2

    def replace_text_range(self, start_idx, end_idx, replacement):
        text = self.doc.Text
        cursor = text.createTextCursor()

        # Cursor auf Anfangsposition setzen und dann erweitern
        cursor.goRight(start_idx, False)  # gehe auf Startposition
        cursor.goRight(end_idx - start_idx, True)  # markiere bis Endposition

        cursor.setString(replacement)

    def highlight_and_confirm(self, start_idx, end_idx, replacement):
        text = self.doc.Text
        cursor = text.createTextCursor()
        view_cursor = self.doc.CurrentController.getViewCursor()

        # Gehe zum Startindex
        cursor.goRight(start_idx, False)
        cursor.goRight(end_idx - start_idx, True)

        # Markiere das zu ersetzende Wort
        current_word = cursor.getString()

        view_cursor.gotoRange(cursor.getStart(), False)
        view_cursor.gotoRange(cursor.getEnd(), True)

        # Fenster und Toolkit für MessageBox
        frame = self.frame
        win = frame.ContainerWindow
        toolkit = win.getToolkit()

        # Erzeuge die MessageBox
        message = f"Möchten Sie '{current_word}' durch '{replacement}' ersetzen?"
        box = toolkit.createMessageBox(
            win,  # Parent window
            4,  # Type 4 = QUERYBOX
            3,  # Buttons 3 = YES_NO
            "Gender-Vorschlag",  # Titel
            message  # Nachricht
        )

        result = box.execute()

        # Button 2 = Ja
        if result ==  2:
            cursor.setString(replacement)
            return True
        else:
            return False




# Component registration
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(
   GenderAssist, "ooo.ext.gender-assist.impl", ("ooo.ext.gender-assist",),)