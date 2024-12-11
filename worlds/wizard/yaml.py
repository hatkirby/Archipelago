from typing import Optional

import wx
import wx.stc

from .slot import Slot


class YamlEditor(wx.Panel):
    editor: wx.stc.StyledTextCtrl
    slot: Optional[Slot]

    dirty: bool
    ignore_edit: bool

    def __init__(self, parent: wx.Window):
        wx.Panel.__init__(self, parent=parent)

        self.dirty = False
        self.ignore_edit = False

        self.editor = wx.stc.StyledTextCtrl(self, wx.ID_ANY)
        self.editor.SetLexer(wx.stc.STC_LEX_YAML)

        self.editor.SetMarginWidth(0, 30)
        self.editor.StyleSetForeground(wx.stc.STC_STYLE_LINENUMBER, wx.Colour(204, 204, 204))
        self.editor.StyleSetBackground(wx.stc.STC_STYLE_LINENUMBER, wx.Colour(45, 45, 45))
        self.editor.SetMarginType(0, wx.stc.STC_MARGIN_NUMBER)

        self.editor.SetWrapMode(wx.stc.STC_WRAP_WORD)
        self.editor.SetUseTabs(False)
        self.editor.SetTabWidth(2)

        font = wx.Font(14, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.editor.StyleSetFont(wx.stc.STC_STYLE_DEFAULT, font)
        self.editor.StyleSetForeground(wx.stc.STC_STYLE_DEFAULT, wx.Colour(204, 204, 204))
        self.editor.StyleSetBackground(wx.stc.STC_STYLE_DEFAULT, wx.Colour(45, 45, 45))
        self.editor.StyleClearAll()

        self.editor.StyleSetForeground(wx.stc.STC_YAML_DEFAULT, wx.Colour(204, 204, 204))
        self.editor.StyleSetForeground(wx.stc.STC_YAML_COMMENT, wx.Colour(153, 153, 153))
        self.editor.StyleSetForeground(wx.stc.STC_YAML_IDENTIFIER, wx.Colour(242, 119, 122))
        self.editor.StyleSetForeground(wx.stc.STC_YAML_KEYWORD, wx.Colour(249, 145, 87))
        self.editor.StyleSetForeground(wx.stc.STC_YAML_NUMBER, wx.Colour(249, 145, 87))
        self.editor.StyleSetForeground(wx.stc.STC_YAML_REFERENCE, wx.Colour(102, 204, 204))
        self.editor.StyleSetForeground(wx.stc.STC_YAML_DOCUMENT, wx.Colour(102, 204, 204))
        self.editor.StyleSetForeground(wx.stc.STC_YAML_TEXT, wx.Colour(153, 204, 153))
        self.editor.StyleSetForeground(wx.stc.STC_YAML_OPERATOR, wx.Colour(102, 204, 204))

        self.editor.SetCaretForeground(wx.Colour(204, 204, 204))

        self.editor.SetModEventMask(wx.stc.STC_MOD_INSERTTEXT | wx.stc.STC_MOD_DELETETEXT | wx.stc.STC_PERFORMED_USER | wx.stc.STC_PERFORMED_UNDO | wx.stc.STC_PERFORMED_REDO)
        self.editor.Bind(wx.stc.EVT_STC_CHANGE, self.on_text_edited, self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.editor, wx.SizerFlags().Proportion(1).Expand())
        self.SetSizer(sizer)

    def load_slot(self, slot: Slot):
        self.slot = slot
        self.dirty = False

        self.ignore_edit = True
        self.editor.SetText(self.slot.to_yaml())
        self.ignore_edit = False

    def save_slot(self):
        if self.dirty:
            self.slot.from_yaml(self.editor.GetText())
            self.dirty = False

    def on_text_edited(self, event: wx.stc.StyledTextEvent):
        if self.ignore_edit:
            return

        self.dirty = True
        if not self.slot.dirty:
            self.slot.dirty = True
