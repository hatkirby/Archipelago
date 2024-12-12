from typing import Set

import wx
import wx.dataview

from .definitions import Game, OptionDefinition
from .utils import FilterableItemPicker, EVT_PICK_ITEM
from .value import OptionValue


class OptionSetDialog(wx.Dialog):
    game: Game
    game_option: OptionDefinition

    item_picker: FilterableItemPicker
    chosen_list: wx.dataview.DataViewListCtrl

    picked: Set[str]

    def __init__(self, game: Game, option_name: str, option_value: OptionValue):
        wx.Dialog.__init__(self, parent=None, title="Value Picker")

        self.game = game
        self.game_option = game.options.get(option_name)
        self.picked = set()

        # Initialize the form.
        top_sizer = wx.BoxSizer(wx.VERTICAL)

        desc_panel = wx.Panel(self, wx.ID_ANY)
        desc_sizer = wx.StaticBoxSizer(wx.VERTICAL, desc_panel, "Option Description")

        option_header = wx.StaticText(desc_sizer.GetStaticBox(), wx.ID_ANY, "")
        option_header.SetFont(option_header.GetFont().Bold())

        option_description = wx.StaticText(desc_sizer.GetStaticBox(), wx.ID_ANY, "")

        desc_sizer.Add(option_header, wx.SizerFlags().Expand())
        desc_sizer.AddSpacer(10)
        desc_sizer.Add(option_description, wx.SizerFlags().Expand())
        desc_panel.SetSizer(desc_sizer)

        top_sizer.Add(desc_panel, wx.SizerFlags().DoubleBorder().Expand())

        # Set up the source list.
        lists_panel = wx.Panel(self, wx.ID_ANY)
        lists_sizer = wx.StaticBoxSizer(wx.HORIZONTAL, lists_panel, "Option Values")

        self.item_picker = FilterableItemPicker(lists_sizer.GetStaticBox(),
                                                self.game.get_option_set_elements(self.game_option))

        self.item_picker.Bind(EVT_PICK_ITEM, self.on_item_picked)

        lists_sizer.Add(self.item_picker, wx.SizerFlags().DoubleBorder().Proportion(1).Expand())

        # Set up the chosen list.
        self.chosen_list = wx.dataview.DataViewListCtrl(lists_sizer.GetStaticBox(), wx.ID_ANY)
        self.chosen_list.AppendTextColumn("Value")

        option_set = self.game.get_option_set_elements(self.game_option)
        for set_item in option_value.value:
            str_val = option_set[set_item]
            self.chosen_list.AppendItem([str_val])
            self.picked.add(str_val)

        remove_btn = wx.Button(lists_sizer.GetStaticBox(), wx.ID_ANY, "Remove")
        remove_btn.Bind(wx.EVT_BUTTON, self.on_remove_clicked)

        right_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer.Add(self.chosen_list, wx.SizerFlags().Proportion(1).Expand())
        right_sizer.AddSpacer(10)
        right_sizer.Add(remove_btn, wx.SizerFlags().Center())

        lists_sizer.Add(right_sizer, wx.SizerFlags().DoubleBorder().Proportion(1).Expand())

        lists_panel.SetSizerAndFit(lists_sizer)
        top_sizer.Add(lists_panel, wx.SizerFlags().DoubleBorder().Expand())
        top_sizer.Add(self.CreateButtonSizer(wx.OK | wx.CANCEL), wx.SizerFlags().Expand())

        # Finish up the form.
        self.SetSizer(top_sizer)
        self.Layout()
        self.SetMinSize(self.GetSize())
        self.Fit()

        width = option_header.GetClientSize().GetWidth()
        option_header.SetLabel(self.game_option.display_name)
        option_header.Wrap(width)

        option_description.SetLabel(self.game_option.description)
        option_description.Wrap(width)

        self.Fit()
        self.CentreOnParent()

    def get_option_value(self) -> OptionValue:
        option_set = self.game.get_option_set_elements(self.game_option)

        option_value = OptionValue()
        option_value.value = [option_set.index(set_item) for set_item in self.picked]

        return option_value

    def on_item_picked(self, event: wx.CommandEvent):
        if event.GetString() in self.picked:
            return

        self.chosen_list.AppendItem([event.GetString()])
        self.picked.add(event.GetString())

    def on_remove_clicked(self, event: wx.CommandEvent):
        selection = self.chosen_list.GetSelectedRow()
        if selection == wx.NOT_FOUND:
            return

        self.picked.remove(self.chosen_list.GetTextValue(selection, 0))
        self.chosen_list.DeleteItem(selection)
