from typing import Callable, Optional, List

import wx

from .definitions import get_game_definitions, OptionType, SetType, OptionDefinition, OptionValue
from .random_choice_dialog import RandomChoiceDialog
from .set_dialog import OptionSetDialog
from .slot import Slot
from .utils import NumericPicker, EVT_PICK_NUMBER


class FormOption:
    parent: "WizardEditor"
    game_option: OptionDefinition

    option_label: wx.StaticText

    save_to_slot: Callable[[], None]

    def __init__(self, parent: "WizardEditor", container: wx.Window, option_name: str, sizer: wx.Sizer):
        self.parent = parent

        self.game_option = get_game_definitions().games.get(parent.slot.game).options.get(option_name)

        self.option_label = wx.StaticText(container, wx.ID_ANY, "")
        self.option_label.SetLabelText(f"{self.game_option.display_name}:")
        self.option_label.Bind(wx.EVT_ENTER_WINDOW, self.on_mouse_enter_window)
        sizer.Add(self.option_label, wx.SizerFlags().Align(wx.ALIGN_TOP | wx.ALIGN_LEFT))

    def on_mouse_enter_window(self, event: wx.MouseEvent):
        option_name = self.game_option.name
        if option_name in self.parent.slot.options and self.parent.slot.options.get(option_name).error is not None:
            self.parent.message_callback("Error", self.parent.slot.options.get(option_name).error)
        else:
            self.parent.message_callback(self.game_option.display_name, self.game_option.description)

    def get_option_value(self):
        return self.parent.slot.options.get(self.game_option.name, self.game_option.default_value)

    def populate_from_slot(self):
        ov = self.get_option_value()

        if ov.error is not None:
            self.option_label.SetForegroundColour(wx.RED)
        else:
            self.option_label.SetForegroundColour(self.option_label.GetParent().GetForegroundColour())


class RandomizableFormOption(FormOption):
    random_button: wx.ToggleButton

    setup: Callable[[wx.Window, wx.Sizer], None]

    def __init__(self, parent: "WizardEditor", container: wx.Window, option_name: str, sizer: wx.Sizer):
        FormOption.__init__(self, parent, container, option_name, sizer)

        self.setup(container, sizer)

        self.random_button = wx.ToggleButton(container, wx.ID_ANY, "\U0001F3B2", style=wx.BU_EXACTFIT)
        self.random_button.Bind(wx.EVT_TOGGLEBUTTON, self.on_random_clicked)
        sizer.Add(self.random_button)

    def on_random_clicked(self, event: wx.CommandEvent):
        ov = self.get_option_value()
        self.random_button.SetValue(ov.random)

        # open the dialogs
        if self.game_option.type == OptionType.SELECT:
            rcd = RandomChoiceDialog(self.game_option, ov)
            if rcd.ShowModal() != wx.ID_OK:
                return

            dlg_value = rcd.get_option_value()

            # If randomization was just turned off, we need to choose a value to fall back to. If the default is
            # non-random, then we can just unset the option, because that's basically the same as setting the default.
            # If the default is random, arbitrarily select the first choice.
            #
            # If randomization is still on, just copy the option value from the dialog into the world.
            if dlg_value.random:
                self.parent.slot.set_option(self.game_option.name, dlg_value)
            elif ov.random:
                if self.game_option.default_value.random:
                    dlg_value.value = self.game_option.choices.ordering[0][1]
                    self.parent.slot.set_option(self.game_option.name, dlg_value)
                else:
                    self.parent.slot.set_option(self.game_option.name, None)

        self.populate_from_slot()

    def populate_from_slot(self):
        FormOption.populate_from_slot(self)

        ov = self.get_option_value()

        if ov.error is not None:
            self.random_button.Disable()
            self.random_button.SetValue(False)
        elif ov.random:
            self.random_button.SetValue(True)
            self.random_button.Enable()
        else:
            self.random_button.SetValue(False)
            self.random_button.Enable()


class LiteralFormOption(FormOption):
    setup: Callable[[wx.Window, wx.Sizer], None]

    def __init__(self, parent: "WizardEditor", container: wx.Window, option_name: str, sizer: wx.Sizer):
        FormOption.__init__(self, parent, container, option_name, sizer)

        self.setup(container, sizer)

        sizer.Add(0, 0)


class SelectFormOption(RandomizableFormOption):
    combo_box: wx.Choice

    def setup(self, container: wx.Window, sizer: wx.Sizer):
        self.combo_box = wx.Choice(container, wx.ID_ANY)

        for value_display in self.game_option.choice_names:
            self.combo_box.Append(value_display)

        self.combo_box.Bind(wx.EVT_CHOICE, self.on_select_changed)
        sizer.Add(self.combo_box, wx.SizerFlags().Expand())

    def on_select_changed(self, event: wx.CommandEvent):
        self.save_to_slot()

    def populate_from_slot(self):
        RandomizableFormOption.populate_from_slot(self)

        ov = self.get_option_value()

        if ov.error is not None or ov.random:
            self.combo_box.Disable()
        else:
            self.combo_box.SetSelection(self.game_option.choices.values.get(ov.value))
            self.combo_box.Enable()

    def save_to_slot(self):
        new_value = OptionValue()
        new_value.value = self.game_option.choices.ordering[self.combo_box.GetSelection()][1]

        self.parent.slot.set_option(self.game_option.name, new_value)


class RangeFormOption(RandomizableFormOption):
    numeric_picker: NumericPicker

    def setup(self, container: wx.Window, sizer: wx.Sizer):
        self.numeric_picker = NumericPicker(container, wx.ID_ANY, self.game_option.min_value,
                                            self.game_option.max_value, self.game_option.min_value)
        self.numeric_picker.Bind(EVT_PICK_NUMBER, self.on_range_picker_changed)

        sizer.Add(self.numeric_picker, wx.SizerFlags().Expand())

    def on_range_picker_changed(self, event: wx.CommandEvent):
        self.save_to_slot()

    def populate_from_slot(self):
        RandomizableFormOption.populate_from_slot(self)

        ov = self.get_option_value()

        if ov.error is not None or ov.random:
            self.numeric_picker.Disable()
        else:
            self.numeric_picker.Enable()
            self.numeric_picker.value = ov.value

    def save_to_slot(self):
        new_value = OptionValue()
        new_value.value = self.numeric_picker.value

        self.parent.slot.set_option(self.game_option.name, new_value)


class NamedRangeFormOption(RandomizableFormOption):
    numeric_picker: NumericPicker
    combo_box: wx.Choice

    def setup(self, container: wx.Window, sizer: wx.Sizer):
        self.numeric_picker = NumericPicker(container, wx.ID_ANY, self.game_option.min_value,
                                            self.game_option.max_value, self.game_option.default_value.value)
        self.numeric_picker.Bind(EVT_PICK_NUMBER, self.on_range_picker_changed)

        self.combo_box = wx.Choice(container, wx.ID_ANY)

        for value_value, value_name in self.game_option.value_names.ordering:
            self.combo_box.Append(value_name.title())
        self.combo_box.Append("Custom")

        self.combo_box.Bind(wx.EVT_CHOICE, self.on_named_range_changed)

        named_sizer = wx.BoxSizer(wx.VERTICAL)
        named_sizer.Add(self.combo_box, wx.SizerFlags().Expand())
        named_sizer.AddSpacer(5)
        named_sizer.Add(self.numeric_picker, wx.SizerFlags().Expand())

        sizer.Add(named_sizer, wx.SizerFlags().Expand())

    def on_range_picker_changed(self, event: wx.CommandEvent):
        selection = self.combo_box.GetCount() - 1
        if self.numeric_picker.value in self.game_option.value_names.keys:
            selection = self.game_option.value_names.keys.get(self.numeric_picker.value)

        if self.combo_box.GetSelection() != selection:
            self.combo_box.SetSelection(selection)

        self.save_to_slot()

    def on_named_range_changed(self, event: wx.CommandEvent):
        if self.combo_box.GetSelection() in range(0, len(self.game_option.value_names.ordering)):
            result = self.game_option.value_names.ordering[self.combo_box.GetSelection()][0]

            if result != self.numeric_picker.value:
                self.numeric_picker.value = result

                self.save_to_slot()

    def populate_from_slot(self):
        RandomizableFormOption.populate_from_slot(self)

        ov = self.get_option_value()

        if ov.error is not None or ov.random:
            self.numeric_picker.Disable()
            self.combo_box.Disable()
        else:
            self.numeric_picker.Enable()
            self.numeric_picker.value = ov.value

            self.combo_box.Enable()
            if ov.value in self.game_option.value_names.keys:
                self.combo_box.SetSelection(self.game_option.value_names.keys.get(ov.value))
            else:
                self.combo_box.SetSelection(self.combo_box.GetCount() - 1)

    def save_to_slot(self):
        new_value = OptionValue()
        new_value.value = self.numeric_picker.value

        self.parent.slot.set_option(self.game_option.name, new_value)


class ChecklistFormOption(LiteralFormOption):
    list_box: wx.CheckListBox

    def setup(self, container: wx.Window, sizer: wx.Sizer):
        self.list_box = wx.CheckListBox(container, wx.ID_ANY)

        for name in self.game_option.custom_set:
            self.list_box.Append(name)

        self.list_box.Bind(wx.EVT_CHECKLISTBOX, self.on_list_item_changed)

        sizer.Add(self.list_box, wx.SizerFlags().Expand())

    def on_list_item_changed(self, event: wx.CommandEvent):
        self.save_to_slot()

    def populate_from_slot(self):
        FormOption.populate_from_slot(self)

        ov = self.get_option_value()

        if ov.error is not None:
            self.list_box.Disable()
        else:
            self.list_box.Enable()

            for i in range(0, self.list_box.GetCount()):
                self.list_box.Check(i, i in ov.value)

    def save_to_slot(self):
        new_value = OptionValue()
        new_value.value = [i for i in range(0, self.list_box.GetCount()) if self.list_box.IsChecked(i)]

        self.parent.slot.set_option(self.game_option.name, new_value)


class OptionSetFormOption(LiteralFormOption):
    open_choice_btn: wx.Button

    def setup(self, container: wx.Window, sizer: wx.Sizer):
        self.open_choice_btn = wx.Button(container, wx.ID_ANY, "Edit option")
        self.open_choice_btn.Bind(wx.EVT_BUTTON, self.on_option_set_clicked)

        sizer.Add(self.open_choice_btn, wx.SizerFlags().Expand())

    def on_option_set_clicked(self, event: wx.CommandEvent):
        osd = OptionSetDialog(get_game_definitions().games.get(self.parent.slot.game), self.game_option.name,
                              self.get_option_value())
        if osd.ShowModal() != wx.ID_OK:
            return

        self.parent.slot.set_option(self.game_option.name, osd.get_option_value())

    def populate_from_slot(self):
        FormOption.populate_from_slot(self)

        ov = self.get_option_value()

        if ov.error:
            self.open_choice_btn.Disable()
        else:
            self.open_choice_btn.Enable()

    def save_to_slot(self):
        pass


class ItemDictFormOption(LiteralFormOption):
    open_choice_btn: wx.Button

    def setup(self, container: wx.Window, sizer: wx.Sizer):
        self.open_choice_btn = wx.Button(container, wx.ID_ANY, "Edit option")
        self.open_choice_btn.Bind(wx.EVT_BUTTON, self.on_item_dict_clicked)

        sizer.Add(self.open_choice_btn, wx.SizerFlags().Expand())

    def on_item_dict_clicked(self, event: wx.CommandEvent):
        pass

    def populate_from_slot(self):
        FormOption.populate_from_slot(self)

        ov = self.get_option_value()

        if ov.error:
            self.open_choice_btn.Disable()
        else:
            self.open_choice_btn.Enable()

    def save_to_slot(self):
        pass


class YamlOnlyFormOption(LiteralFormOption):
    def setup(self, container: wx.Window, sizer: wx.Sizer):
        sizer.Add(wx.StaticText(container, wx.ID_ANY, "YAML-only option."), wx.SizerFlags().Expand())


def make_form_option_for_option(parent: "WizardEditor", container: wx.Window, option_name: str, sizer: wx.Sizer):
    game_option = get_game_definitions().games.get(parent.slot.game).options.get(option_name)

    if game_option.type == OptionType.SELECT:
        return SelectFormOption(parent, container, option_name, sizer)
    elif game_option.type == OptionType.RANGE:
        if game_option.named_range:
            return NamedRangeFormOption(parent, container, option_name, sizer)
        else:
            return RangeFormOption(parent, container, option_name, sizer)
    elif game_option.type == OptionType.SET and game_option.set_type == SetType.CUSTOM and\
            len(game_option.custom_set) <= 15:
        return ChecklistFormOption(parent, container, option_name, sizer)
    elif game_option.type == OptionType.SET:
        return OptionSetFormOption(parent, container, option_name, sizer)
    elif game_option.type == OptionType.DICT:
        return ItemDictFormOption(parent, container, option_name, sizer)
    else:
        return YamlOnlyFormOption(parent, container, option_name, sizer)


class WizardEditor(wx.ScrolledWindow):
    slot: Optional[Slot]
    cur_game: Optional[str]
    first_time: bool

    name_box: wx.TextCtrl
    description_box: wx.TextCtrl
    game_box: wx.Choice
    preset_label: wx.StaticText
    preset_box: wx.Choice
    other_options: Optional[wx.Panel]
    common_options_pane: Optional[wx.CollapsiblePane]
    top_sizer: wx.BoxSizer

    form_options: List[FormOption]

    message_callback: Callable[[str, str], None]

    def __init__(self, parent: wx.Window):
        wx.ScrolledWindow.__init__(self, parent=parent)

        self.slot = None
        self.cur_game = None
        self.first_time = True
        self.other_options = None
        self.common_options_pane = None
        self.form_options = []
        self.message_callback = lambda header, msg: None

        self.name_box = wx.TextCtrl(self, wx.ID_ANY)
        self.name_box.Bind(wx.EVT_TEXT, self.on_change_name)

        self.description_box = wx.TextCtrl(self, wx.ID_ANY)
        self.description_box.Bind(wx.EVT_TEXT, self.on_change_description)

        self.game_box = wx.Choice(self, wx.ID_ANY)

        self.game_box.Append("")
        game_names = list(get_game_definitions().games.keys())
        game_names.sort()
        for game_name in game_names:
            self.game_box.Append(game_name)

        self.game_box.Bind(wx.EVT_CHOICE, self.on_change_game)

        self.preset_label = wx.StaticText(self, wx.ID_ANY, "Preset:")
        self.preset_label.Hide()

        self.preset_box = wx.Choice(self, wx.ID_ANY)
        self.preset_box.Bind(wx.EVT_CHOICE, self.on_change_preset)
        self.preset_box.Hide()

        form_sizer = wx.FlexGridSizer(2, 10, 10)
        form_sizer.AddGrowableCol(1)

        form_sizer.Add(wx.StaticText(self, -1, "Name:"), wx.SizerFlags().Align(wx.ALIGN_TOP | wx.ALIGN_LEFT))
        form_sizer.Add(self.name_box, wx.SizerFlags().Expand())
        form_sizer.Add(wx.StaticText(self, -1, "Description:"), wx.SizerFlags().Align(wx.ALIGN_TOP | wx.ALIGN_LEFT))
        form_sizer.Add(self.description_box, wx.SizerFlags().Expand())
        form_sizer.Add(wx.StaticText(self, -1, "Game:"), wx.SizerFlags().Align(wx.ALIGN_TOP | wx.ALIGN_LEFT))
        form_sizer.Add(self.game_box, wx.SizerFlags().Expand())
        form_sizer.Add(self.preset_label, wx.SizerFlags().Align(wx.ALIGN_TOP | wx.ALIGN_LEFT))
        form_sizer.Add(self.preset_box, wx.SizerFlags().Expand())

        self.top_sizer = wx.BoxSizer(wx.VERTICAL)
        self.top_sizer.Add(form_sizer, wx.SizerFlags().DoubleBorder().Expand())
        self.top_sizer.Add(wx.StaticLine(self))

        self.SetScrollRate(0, 20)

        self.rebuild()

    def load_slot(self, slot: Slot):
        self.slot = slot
        self.rebuild()

    def reload(self):
        self.rebuild()

    def rebuild(self):
        next_game = None
        if self.slot is not None and self.slot.game is not None:
            next_game = self.slot.game

        if not self.first_time and self.cur_game == next_game:
            self.populate()
            self.Layout()
            return

        self.first_time = False

        if self.other_options is not None:
            self.other_options.Destroy()
            self.other_options = None

            if self.common_options_pane is not None:
                self.common_options_pane.Destroy()
                self.common_options_pane = None

            self.form_options.clear()

        if self.slot is not None and self.slot.game is not None:
            self.other_options = wx.Panel(self, wx.ID_ANY)

            game = get_game_definitions().games.get(self.slot.game)

            options_form_sizer = wx.FlexGridSizer(3, 10, 10)
            options_form_sizer.AddGrowableCol(1)

            common_options = []
            for game_option in game.options.values():
                if game_option.common:
                    common_options.append(game_option)
                else:
                    self.form_options.append(make_form_option_for_option(self, self.other_options, game_option.name,
                                                                         options_form_sizer))

            self.other_options.SetSizerAndFit(options_form_sizer)
            self.top_sizer.Add(self.other_options, wx.SizerFlags().DoubleBorder().Expand())

            if len(common_options) > 0:
                self.common_options_pane = wx.CollapsiblePane(self, wx.ID_ANY, "Advanced Options",
                                                              style=wx.CP_DEFAULT_STYLE | wx.CP_NO_TLW_RESIZE)
                self.common_options_pane.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, lambda event: self.fix_size())

                common_options_sizer = wx.FlexGridSizer(3, 10, 10)
                common_options_sizer.AddGrowableCol(1)

                for game_option in common_options:
                    self.form_options.append(make_form_option_for_option(self, self.common_options_pane.GetPane(),
                                                                         game_option.name, common_options_sizer))

                self.common_options_pane.GetPane().SetSizerAndFit(common_options_sizer)
                self.top_sizer.Add(self.common_options_pane, wx.SizerFlags().DoubleBorder().Proportion(0).Expand())

            if len(game.presets) > 0:
                self.preset_box.Clear()
                self.preset_box.Append("")

                for preset_name in game.presets.keys():
                    self.preset_box.Append(preset_name)

                self.preset_label.Show()
                self.preset_box.Show()
            else:
                self.preset_label.Hide()
                self.preset_box.Hide()
        else:
            self.preset_label.Hide()
            self.preset_box.Hide()

        self.populate()
        self.fix_size()

        self.cur_game = next_game

    def populate(self):
        if self.slot is not None:
            self.name_box.ChangeValue(self.slot.name)
            self.description_box.ChangeValue(self.slot.description)
        else:
            self.name_box.ChangeValue("")
            self.description_box.ChangeValue("")

        if self.slot is not None and self.slot.game is not None:
            self.game_box.SetSelection(self.game_box.FindString(self.slot.game))

            for form_option in self.form_options:
                form_option.populate_from_slot()
        else:
            self.game_box.SetSelection(0)

    def fix_size(self):
        self.SetSizer(self.top_sizer)
        self.Layout()
        self.FitInside()

        frame: wx.Window = wx.GetTopLevelParent(self)
        frame.SetMinSize(frame.GetSize())
        frame.Fit()
        frame.SetMinSize(wx.Size(728, int(728 / 2)))

    def on_change_name(self, event: wx.CommandEvent):
        self.slot.name = self.name_box.GetValue()

    def on_change_description(self, event: wx.CommandEvent):
        self.slot.description = self.description_box.GetValue()

    def on_change_game(self, event: wx.CommandEvent):
        if self.slot.has_set_options():
            if wx.MessageBox("This slot has options set on it. Changing the game will clear those options. Are you "
                             "sure you want to proceed?", "Confirm", wx.YES_NO, self) == wx.NO:
                self.game_box.SetSelection(self.game_box.FindString(self.slot.game))
                return

        if self.game_box.GetSelection() == 0:
            self.slot.game = None
        else:
            self.slot.game = self.game_box.GetString(self.game_box.GetSelection())

        self.rebuild()

    def on_change_preset(self, event: wx.CommandEvent):
        if self.preset_box.GetSelection() == 0:
            return

        if self.slot.has_set_options():
            if wx.MessageBox("This slot has options set on it. Using a preset will clear these options. Are you sure "
                             "you want to proceed?", "Confirm", wx.YES_NO, self) == wx.NO:
                self.preset_box.SetSelection(0)
                return

        self.slot.clear_options()

        game = get_game_definitions().games.get(self.slot.game)
        preset = game.presets.get(self.preset_box.GetString(self.preset_box.GetSelection()))

        for option_name, option_value in preset.items():
            self.slot.set_option(option_name, option_value)

        self.populate()
        self.Layout()
