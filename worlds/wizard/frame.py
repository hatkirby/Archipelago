from pathlib import PurePath
from typing import List

import wx

from .slot import Slot
from .window import SlotWindow


class WizardFrame(wx.Frame):
    splitter_window: wx.SplitterWindow
    slot_list: wx.TreeCtrl
    slot_window: SlotWindow

    left_pane: wx.SplitterWindow
    message_pane: wx.ScrolledWindow
    message_header: wx.StaticText
    message_window: wx.StaticText

    slots: List[Slot]

    close_menu_item_id: wx.WindowIDRef

    def __init__(self):
        wx.Frame.__init__(self, None, title="Wizard")

        self.SetSize(728, 728)

        self.slots = []

        self.make_menu_bar()

        self.Bind(wx.EVT_CLOSE, self.on_close, self)

        self.splitter_window = wx.SplitterWindow(self, wx.ID_ANY)
        self.splitter_window.SetMinimumPaneSize(250)

        self.left_pane = wx.SplitterWindow(self.splitter_window, wx.ID_ANY)
        self.left_pane.SetMinimumPaneSize(150)

        self.slot_list = wx.TreeCtrl(self.left_pane, style=wx.TR_HIDE_ROOT)
        self.slot_list.AddRoot("Multislot")

        self.slot_list.Bind(wx.EVT_TREE_SEL_CHANGING, self.on_slot_selecting)
        self.slot_list.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_slot_selected)
        self.slot_list.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.on_slot_right_click)

        self.message_pane = wx.ScrolledWindow(self.left_pane, wx.ID_ANY)

        self.message_header = wx.StaticText(self.message_pane, wx.ID_ANY, "")
        self.message_header.SetFont(self.message_header.GetFont().Bold())

        self.message_window = wx.StaticText(self.message_pane, wx.ID_ANY, "")

        msg_sizer = wx.BoxSizer(wx.VERTICAL)
        msg_sizer.Add(self.message_header, wx.SizerFlags().DoubleBorder().Expand())
        msg_sizer.Add(self.message_window, wx.SizerFlags().DoubleBorder(wx.ALL & ~wx.UP).Expand())
        self.message_pane.SetSizer(msg_sizer)
        self.message_pane.Layout()

        self.left_pane.SplitHorizontally(self.slot_list, self.message_pane, -150)

        self.message_pane.SetScrollRate(0, 5)

        self.slot_window = SlotWindow(self.splitter_window)
        self.slot_window.wizard_editor.message_callback = self.show_message

        self.splitter_window.SplitVertically(self.left_pane, self.slot_window, 250)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.splitter_window, wx.SizerFlags().Proportion(1).Expand())
        self.SetSizer(sizer)

    def make_menu_bar(self):
        menu_file = wx.Menu()
        new_slot_item = menu_file.Append(wx.ID_ANY, "&New Slot\tCtrl-N")
        load_slot_item = menu_file.Append(wx.ID_ANY, "&Load Slot from File\tCtrl-O")
        save_slot_item = menu_file.Append(wx.ID_ANY, "&Save Slot\tCtrl-S")
        save_slot_as_item = menu_file.Append(wx.ID_ANY, "Save Slot As...\tCtrl-Shift-S")
        close_slot_item = menu_file.Append(wx.ID_ANY, "&Close Slot\tCtrl-W")
        exit_item = menu_file.Append(wx.ID_EXIT)

        self.close_menu_item_id = close_slot_item.GetId()

        menu_help = wx.Menu()
        about_item = menu_help.Append(wx.ID_ABOUT)

        menu_bar = wx.MenuBar()
        menu_bar.Append(menu_file, "&File")
        menu_bar.Append(menu_help, "&Help")
        self.SetMenuBar(menu_bar)

        self.Bind(wx.EVT_MENU, self.on_new_slot, new_slot_item)
        self.Bind(wx.EVT_MENU, self.on_load_slot, load_slot_item)
        self.Bind(wx.EVT_MENU, self.on_save_slot, save_slot_item)
        self.Bind(wx.EVT_MENU, self.on_save_as_slot, save_slot_as_item)
        self.Bind(wx.EVT_MENU, self.on_close_slot, close_slot_item)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        self.Bind(wx.EVT_MENU, self.on_about, about_item)

    def on_new_slot(self, event: wx.CommandEvent):
        if not self.flush_selected_slot(ask_discard=True):
            return

        self.initialize_slot(Slot())

    def on_load_slot(self, event: wx.CommandEvent):
        if not self.flush_selected_slot(ask_discard=True):
            return

        open_file_dialog = wx.FileDialog(self, "Open Slot YAML", "", "", "YAML files (*.yaml;*.yml)|*.yaml;*.yml",
                                         wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if open_file_dialog.ShowModal() == wx.ID_CANCEL:
            return

        try:
            load_slot = Slot()
            load_slot.load(open_file_dialog.GetPath())

            self.initialize_slot(load_slot)
        except Exception as ex:
            wx.MessageBox(str(ex), "Error loading slot", wx.OK, self)

    def on_save_slot(self, event: wx.CommandEvent):
        if not self.slot_list.GetSelection().IsOk() or self.slot_list.GetRootItem() == self.slot_list.GetSelection():
            return

        if not self.flush_selected_slot(ask_discard=False):
            return

        slot = self.slot_list.GetItemData(self.slot_list.GetSelection())
        self.attempt_save_slot(slot)

    def on_save_as_slot(self, event: wx.CommandEvent):
        if not self.slot_list.GetSelection().IsOk() or self.slot_list.GetRootItem() == self.slot_list.GetSelection():
            return

        if not self.flush_selected_slot(ask_discard=False):
            return

        slot = self.slot_list.GetItemData(self.slot_list.GetSelection())
        self.attempt_save_slot(slot, force_dialog=True)

    def on_close_slot(self, event: wx.CommandEvent):
        if not self.slot_list.GetSelection().IsOk() or self.slot_list.GetRootItem() == self.slot_list.GetSelection():
            return

        if not self.flush_selected_slot(ask_discard=True):
            return

        slot: Slot = self.slot_list.GetItemData(self.slot_list.GetSelection())
        if slot.dirty:
            message_pieces = ["\""]

            if slot.name == "":
                message_pieces.append("Untitled World")
            else:
                message_pieces.append(slot.name)

            if slot.game is not None:
                message_pieces.append(f" [{slot.game}]")

            message_pieces.append("\" has unsaved changes. Would you like to save them?")

            result = wx.MessageBox("".join(message_pieces), "Confirm", wx.YES_NO | wx.CANCEL, self)
            if result == wx.CANCEL:
                return
            elif result == wx.YES:
                if not self.attempt_save_slot(slot):
                    return

        self.slot_list.Delete(self.slot_list.GetSelection())
        self.slots.remove(slot)

    def on_exit(self, event: wx.CommandEvent):
        if not self.flush_all_slots():
            return

        self.Close(force=True)

    def on_close(self, event: wx.CloseEvent):
        if event.CanVeto() and not self.flush_all_slots():
            event.Veto()
            return

        self.Destroy()

    def on_about(self, event: wx.CommandEvent):
        pass

    def on_slot_selecting(self, event: wx.TreeEvent):
        if not self.flush_selected_slot(ask_discard=True):
            event.Veto()

    def on_slot_selected(self, event: wx.TreeEvent):
        if not event.GetItem().IsOk() or event.GetItem() == self.slot_list.GetRootItem():
            self.slot_window.unload_slot()
        else:
            slot: Slot = self.slot_list.GetItemData(event.GetItem())
            self.slot_window.load_slot(slot)

    def on_slot_right_click(self, event: wx.TreeEvent):
        if not event.GetItem().IsOk() or event.GetItem() == self.slot_list.GetRootItem():
            return

        popup_menu = wx.Menu()
        popup_menu.Append(self.close_menu_item_id, "&Close")

        self.PopupMenu(popup_menu, self.ScreenToClient(wx.GetMousePosition()))

    def initialize_slot(self, new_slot: Slot):
        self.slots.append(new_slot)

        root_id = self.slot_list.GetRootItem()
        new_id = self.slot_list.AppendItem(root_id, "New World", data=new_slot)

        new_slot.meta_update_callback = lambda: self.update_slot_display(new_slot, new_id)

        self.update_slot_display(new_slot, new_id)
        self.slot_list.SelectItem(new_id)

    def update_slot_display(self, slot: Slot, tree_item_id: wx.TreeItemId):
        display_pieces = []

        if slot.dirty:
            display_pieces.append("*")

        if slot.name == "":
            display_pieces.append("Untitled World")
        else:
            display_pieces.append(slot.name)

        if slot.game is not None:
            display_pieces.append(f" [{slot.game}]")

        if slot.filename is not None:
            filepath = PurePath(slot.filename)
            display_pieces.append(f" {{{filepath.name}}}")

        self.slot_list.SetItemText(tree_item_id, "".join(display_pieces))

    def show_message(self, header: str, msg: str):
        for i in range(0, 2):
            width = self.message_window.GetClientSize().GetWidth()
            self.message_header.SetLabel(header)
            self.message_header.Wrap(width)

            self.message_window.SetLabel(msg)
            self.message_window.Wrap(width)

            self.message_pane.SetSizer(self.message_pane.GetSizer())
            self.message_pane.Layout()
            self.message_pane.FitInside()
            self.message_pane.Scroll(0, 0)

    def flush_selected_slot(self, ask_discard: bool) -> bool:
        if not self.slot_list.GetSelection().IsOk() or self.slot_list.GetSelection() == self.slot_list.GetRootItem():
            return True

        try:
            self.slot_window.save_slot()
        except Exception as ex:
            msg_pieces = ["Could not save slot.\n\n", ex]

            if ask_discard:
                msg_pieces.append("\n\nWould you like to discard your changes?")

                if wx.MessageBox("".join(msg_pieces), "Failure to save slot", wx.YES_NO) == wx.NO:
                    return False
            else:
                wx.MessageBox("".join(msg_pieces), "Failure to save world")

                return False

        return True

    def flush_all_slots(self) -> bool:
        if not self.flush_selected_slot(ask_discard=True):
            return False

        for slot in self.slots:
            if slot.dirty:
                msg_pieces = ["\""]

                if slot.name == "":
                    msg_pieces.append("Untitled World")
                else:
                    msg_pieces.append(slot.name)

                if slot.game is not None:
                    msg_pieces.append(f" [{slot.game}]")

                msg_pieces.append("\" has unsaved changes. Would you like to save them before quitting?")

                result = wx.MessageBox("".join(msg_pieces), "Confirm", wx.YES_NO | wx.CANCEL, self)
                if result == wx.CANCEL:
                    return False
                elif result == wx.YES:
                    if not self.attempt_save_slot(slot):
                        return False

        return True

    def attempt_save_slot(self, slot: Slot, force_dialog: bool = False) -> bool:
        if slot.filename is None or force_dialog:
            save_file_dialog = wx.FileDialog(self, "Save Slot YAML", "", "", "YAML files (*.yaml;*.yml)|*.yaml;*.yml",
                                             wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

            if save_file_dialog.ShowModal() == wx.ID_CANCEL:
                return False

            slot.filename = save_file_dialog.GetPath()

        try:
            slot.save(slot.filename)
        except Exception as ex:
            wx.MessageBox(str(ex), "Error saving Slot", wx.OK, self)
            return False

        return True
