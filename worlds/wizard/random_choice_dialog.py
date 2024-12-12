from typing import Dict, Callable

import wx

from .definitions import OptionDefinition
from .utils import NumericPicker, PickNumberCommandEvent, EVT_PICK_NUMBER
from .value import OptionValue


class RandomChoiceDialog(wx.Dialog):
    weights: Dict[str, int]

    modes_box: wx.RadioBox
    weighted_panel: wx.Panel

    def __init__(self, game_option: OptionDefinition, option_value: OptionValue):
        wx.Dialog.__init__(self, parent=None, title="Randomization Settings")

        # Load the weights from the option value.
        if option_value.random and option_value.weighting is not None:
            self.weights = {weight_value.value: weight_value.weight for weight_value in option_value.weighting}
        else:
            self.weights = {}

        for option_id, option_name in game_option.choices.ordering:
            if option_name in self.weights:
                continue

            if option_value.random and len(option_value.weighting or []) == 0 and\
                    option_name == game_option.default_value.value:
                self.weights[option_name] = 50
            else:
                self.weights[option_name] = 0

        if "random" in self.weights:
            del self.weights["random"]

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

        # Mode selector.
        self.modes_box = wx.RadioBox(self, wx.ID_ANY, label="Randomization Mode", choices=["Off", "On", "Weighted"])

        if option_value.random:
            if option_value.weighting is not None:
                self.modes_box.SetSelection(2)
            else:
                self.modes_box.SetSelection(1)
        else:
            self.modes_box.SetSelection(0)

        self.modes_box.Bind(wx.EVT_RADIOBOX, self.on_mode_changed)
        top_sizer.Add(self.modes_box, wx.SizerFlags().DoubleBorder().Expand())

        # Set up the weighting form.
        self.weighted_panel = wx.Panel(self, wx.ID_ANY)
        weighted_sizer = wx.StaticBoxSizer(wx.VERTICAL, self.weighted_panel, "Weighted Randomization Options")

        rows_sizer = wx.FlexGridSizer(2, 10, 10)
        rows_sizer.AddGrowableCol(1)

        for i, (option_id, option_name) in enumerate(game_option.choices.ordering):
            row_input = NumericPicker(weighted_sizer.GetStaticBox(), wx.ID_ANY, 0, 50, self.weights[option_name])
            row_input.Bind(EVT_PICK_NUMBER, self.make_on_pick_number_lambda(option_name))

            rows_sizer.Add(wx.StaticText(weighted_sizer.GetStaticBox(), wx.ID_ANY, game_option.choice_names[i]))
            rows_sizer.Add(row_input, wx.SizerFlags().Expand())

        weighted_sizer.Add(rows_sizer, wx.SizerFlags().Proportion(1).Expand())
        self.weighted_panel.SetSizer(weighted_sizer)

        top_sizer.Add(self.weighted_panel, wx.SizerFlags().DoubleBorder().Expand())
        top_sizer.Add(self.CreateButtonSizer(wx.OK | wx.CANCEL), wx.SizerFlags().Expand())

        if not option_value.random or option_value.weighting is None:
            self.weighted_panel.Disable()

        self.SetSizer(top_sizer)
        self.Layout()
        self.SetMinSize(self.GetSize())
        self.Fit()

        width = option_header.GetClientSize().GetWidth()
        option_header.SetLabel(game_option.display_name)
        option_header.Wrap(width)

        option_description.SetLabel(game_option.description)
        option_description.Wrap(width)

        self.Fit()
        self.CentreOnParent()

    def get_option_value(self) -> OptionValue:
        result = OptionValue()

        if self.modes_box.GetSelection() == 1:
            result.random = True
            result.weighting = None
        elif self.modes_box.GetSelection() == 2:
            result.random = True
            result.weighting = []

            for option_value, weight in self.weights.items():
                if weight == 0:
                    continue

                sub_option = OptionValue()
                sub_option.weight = weight

                if option_value == "random":
                    sub_option.random = True
                else:
                    sub_option.value = option_value

                result.weighting.append(sub_option)

        return result

    def on_mode_changed(self, event: wx.CommandEvent):
        if event.GetSelection() == 2:
            self.weighted_panel.Enable()
        else:
            self.weighted_panel.Disable()

    def make_on_pick_number_lambda(self, option_name: str) -> Callable[[PickNumberCommandEvent], None]:
        def on_pick_number(event: PickNumberCommandEvent):
            self.weights[option_name] = event.GetInt()
        return on_pick_number
