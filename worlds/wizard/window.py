from typing import Optional

import wx

from .slot import Slot
from .wizard import WizardEditor
from .yaml import YamlEditor


class SlotWindow(wx.Notebook):
    wizard_editor: WizardEditor
    yaml_editor: YamlEditor

    slot: Optional[Slot]

    def __init__(self, parent: wx.Window):
        wx.Notebook.__init__(self, parent=parent)

        self.slot = None

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.on_page_changing)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_page_changed)

        self.wizard_editor = WizardEditor(self)
        self.yaml_editor = YamlEditor(self)

        self.load_pages()
        self.unload_pages()

    def load_slot(self, slot: Slot):
        if self.slot is None:
            self.load_pages()

        self.slot = slot

        self.wizard_editor.load_slot(self.slot)

        if self.GetSelection() == 1:
            self.yaml_editor.load_slot(self.slot)

    def unload_slot(self):
        if self.slot is not None:
            self.slot = None

            self.unload_pages()

    def save_slot(self):
        if self.GetSelection() == 1:
            self.yaml_editor.save_slot()

    def load_pages(self):
        self.AddPage(self.wizard_editor, "Wizard", True)
        self.AddPage(self.yaml_editor, "YAML", False)

    def unload_pages(self):
        self.RemovePage(1)
        self.RemovePage(0)

    def on_page_changing(self, event: wx.BookCtrlEvent):
        if self.slot is None:
            return

        if event.GetOldSelection() == 1:
            try:
                self.yaml_editor.save_slot()
            except Exception as ex:
                msg = "".join(["Could not process YAML.\n\n", ex, "\n\nWould you like to discard your changes?"])

                if wx.MessageBox(msg, "Invalid YAML", wx.YES_NO) == wx.NO:
                    event.Veto()

    def on_page_changed(self, event: wx.BookCtrlEvent):
        if self.slot is None:
            return

        if self.GetSelection() == 0:
            self.wizard_editor.reload()
        elif self.GetSelection() == 1:
            self.yaml_editor.load_slot(self.slot)
