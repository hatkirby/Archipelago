from typing import Optional, Tuple, Callable, NamedTuple

import wx

from .definitions import OptionDefinition
from .utils import NumericPicker, PickNumberCommandEvent, EVT_PICK_NUMBER
from .value import RandomValueType, OptionValue


class RrdValue(NamedTuple):
    static_value: Optional[int]
    random_type: Optional[RandomValueType]
    range: Optional[Tuple[int, int]]

    @classmethod
    def from_option_value(cls, option_value: OptionValue):
        if option_value.random:
            return cls(None, option_value.range_random_type, option_value.range_subset)
        else:
            return cls(option_value.value, None, None)

    @classmethod
    def from_static_value(cls, static_value: int):
        return cls(static_value, None, None)

    @classmethod
    def from_complex_value(cls, random_type: RandomValueType, random_range: Optional[Tuple[int, int]]):
        return cls(None, random_type, random_range)

    def to_option_value(self) -> OptionValue:
        result = OptionValue()

        if self.static_value is not None:
            result.value = self.static_value
        else:
            result.random = True
            result.range_random_type = self.random_type
            result.range_subset = self.range
            result.weighting = None

        return result

    def to_string(self, game_option: OptionDefinition):
        if self.static_value is not None:
            if game_option.named_range and self.static_value in game_option.value_names.keys:
                return f"{game_option.value_names.forward.get(self.static_value).title()} ({self.static_value})"
            else:
                return str(self.static_value)
        elif self.range is not None:
            if self.random_type == RandomValueType.UNIFORM:
                return f"{self.range[0]} to {self.range[1]}"
            elif self.random_type == RandomValueType.LOW:
                return f"{self.range[0]} to {self.range[1]} Low"
            elif self.random_type == RandomValueType.MIDDLE:
                return f"{self.range[0]} to {self.range[1]} Middle"
            elif self.random_type == RandomValueType.HIGH:
                return f"{self.range[0]} to {self.range[1]} High"
        elif self.random_type == RandomValueType.UNIFORM:
            return f"Random"
        elif self.random_type == RandomValueType.LOW:
            return f"Random Low"
        elif self.random_type == RandomValueType.MIDDLE:
            return f"Random Middle"
        elif self.random_type == RandomValueType.HIGH:
            return f"Random High"


class WeightRow:
    dialog: "RandomRangeDialog"
    value: RrdValue

    row_slider: NumericPicker
    header_label: wx.StaticText
    delete_button: wx.Button

    weight: int

    def __init__(self, dialog: "RandomRangeDialog", value: RrdValue, default_weight: int = 0, deletable: bool = True):
        self.dialog = dialog
        self.value = value
        self.weight = default_weight

        self.row_slider = NumericPicker(dialog.weighted_box_sizer.GetStaticBox(), wx.ID_ANY, 0, 50, default_weight)
        self.row_slider.Bind(EVT_PICK_NUMBER, self.on_pick_number)

        self.header_label = wx.StaticText(dialog.weighted_box_sizer.GetStaticBox(), wx.ID_ANY,
                                          value.to_string(dialog.game_option))

        dialog.weighted_sizer.Add(self.header_label)
        dialog.weighted_sizer.Add(self.row_slider, wx.SizerFlags().Expand())

        if deletable:
            self.delete_button = wx.Button(dialog.weighted_box_sizer.GetStaticBox(), wx.ID_ANY, "X",
                                           style=wx.BU_EXACTFIT)
            self.delete_button.Bind(wx.EVT_BUTTON, self.on_delete_clicked)

            dialog.weighted_sizer.Add(self.delete_button)
        else:
            dialog.weighted_sizer.Add(0, 0)

    def on_pick_number(self, event: PickNumberCommandEvent):
        self.weight = event.GetInt()

    def on_delete_clicked(self, event: wx.CommandEvent):
        del self.dialog.weights[self.value]

        self.row_slider.Destroy()
        self.header_label.Destroy()
        self.delete_button.Destroy()

        self.dialog.Layout()
        self.dialog.Fit()


class RandomRangeDialog(wx.Dialog):
    game_option: OptionDefinition

    modes_box: wx.RadioBox

    regular_panel: wx.Panel
    chosen_random_type: RandomValueType
    enable_range_subset: wx.CheckBox
    subset_min: NumericPicker
    subset_max: NumericPicker
    add_regular_button: wx.Button

    weighted_panel: wx.Panel
    weighted_box_sizer: wx.StaticBoxSizer
    weighted_sizer: wx.FlexGridSizer

    add_static_spin: wx.SpinCtrl

    weights: dict[RrdValue, WeightRow]

    def __init__(self, game_option: OptionDefinition, option_value: OptionValue):
        wx.Dialog.__init__(self, parent=None, title="Randomization Settings")

        self.game_option = game_option
        self.weights = {}

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
        self.modes_box.Bind(wx.EVT_RADIOBOX, self.on_mode_changed)
        top_sizer.Add(self.modes_box, wx.SizerFlags().DoubleBorder().Expand())

        # Regular randomization settings.
        self.regular_panel = wx.Panel(self, wx.ID_ANY)
        regular_box_sizer = wx.StaticBoxSizer(wx.VERTICAL, self.regular_panel, "Regular Randomization Options")

        uniform_button = wx.RadioButton(regular_box_sizer.GetStaticBox(), wx.ID_ANY, "Uniform", style=wx.RB_GROUP)
        low_button = wx.RadioButton(regular_box_sizer.GetStaticBox(), wx.ID_ANY, "Low")
        middle_button = wx.RadioButton(regular_box_sizer.GetStaticBox(), wx.ID_ANY, "Middle")
        high_button = wx.RadioButton(regular_box_sizer.GetStaticBox(), wx.ID_ANY, "High")

        uniform_button.Bind(wx.EVT_RADIOBUTTON, self.make_on_choose_random_type_lambda(RandomValueType.UNIFORM))
        low_button.Bind(wx.EVT_RADIOBUTTON, self.make_on_choose_random_type_lambda(RandomValueType.LOW))
        middle_button.Bind(wx.EVT_RADIOBUTTON, self.make_on_choose_random_type_lambda(RandomValueType.MIDDLE))
        high_button.Bind(wx.EVT_RADIOBUTTON, self.make_on_choose_random_type_lambda(RandomValueType.HIGH))

        regular_affinity_sizer = wx.BoxSizer(wx.VERTICAL)
        regular_affinity_sizer.Add(uniform_button)
        regular_affinity_sizer.AddSpacer(5)
        regular_affinity_sizer.Add(low_button)
        regular_affinity_sizer.AddSpacer(5)
        regular_affinity_sizer.Add(middle_button)
        regular_affinity_sizer.AddSpacer(5)
        regular_affinity_sizer.Add(high_button)

        if option_value.random and option_value.weighting is None:
            self.chosen_random_type = option_value.range_random_type

            if self.chosen_random_type == RandomValueType.UNIFORM:
                uniform_button.SetValue(True)
            elif self.chosen_random_type == RandomValueType.LOW:
                low_button.SetValue(True)
            elif self.chosen_random_type == RandomValueType.MIDDLE:
                middle_button.SetValue(True)
            elif self.chosen_random_type == RandomValueType.HIGH:
                high_button.SetValue(True)
        else:
            uniform_button.SetValue(True)

        # Range subset form for regular randomization.
        subset_sizer = wx.FlexGridSizer(2, 10, 10)
        subset_sizer.AddGrowableCol(1)

        effective_subset = (game_option.min_value, game_option.max_value)
        if option_value.random and option_value.weighting is None and option_value.range_subset is not None:
            effective_subset = option_value.range_subset

        self.subset_min = NumericPicker(regular_box_sizer.GetStaticBox(), wx.ID_ANY, game_option.min_value,
                                        game_option.max_value, effective_subset[0])

        subset_sizer.Add(wx.StaticText(regular_box_sizer.GetStaticBox(), wx.ID_ANY, "Minimum:"))
        subset_sizer.Add(self.subset_min, wx.SizerFlags().Expand())

        self.subset_max = NumericPicker(regular_box_sizer.GetStaticBox(), wx.ID_ANY, game_option.min_value,
                                        game_option.max_value, effective_subset[1])

        subset_sizer.Add(wx.StaticText(regular_box_sizer.GetStaticBox(), wx.ID_ANY, "Maximum:"))
        subset_sizer.Add(self.subset_max, wx.SizerFlags().Expand())

        self.enable_range_subset = wx.CheckBox(regular_box_sizer.GetStaticBox(), wx.ID_ANY, "Restrict to sub-range")
        self.enable_range_subset.Bind(wx.EVT_CHECKBOX, self.on_range_restrict_toggled)

        if option_value.random and option_value.weighting is None and option_value.range_subset is not None:
            self.enable_range_subset.SetValue(True)
        else:
            self.subset_min.Disable()
            self.subset_max.Disable()

        second_column = wx.BoxSizer(wx.VERTICAL)
        second_column.Add(self.enable_range_subset)
        second_column.AddSpacer(10)
        second_column.Add(subset_sizer, wx.SizerFlags().Proportion(1).Expand())

        regular_box_columns = wx.BoxSizer(wx.HORIZONTAL)
        regular_box_columns.Add(regular_affinity_sizer, wx.SizerFlags().Proportion(1).Expand())
        regular_box_columns.Add(second_column, wx.SizerFlags().Proportion(1).Expand())

        self.add_regular_button = wx.Button(regular_box_sizer.GetStaticBox(), wx.ID_ANY, "Add to weights")
        self.add_regular_button.Bind(wx.EVT_BUTTON, self.on_add_complex_value_to_weights)

        regular_box_sizer.Add(regular_box_columns, wx.SizerFlags().Proportion(1).Expand())
        regular_box_sizer.AddSpacer(10)
        regular_box_sizer.Add(self.add_regular_button, wx.SizerFlags().Right())

        self.regular_panel.SetSizer(regular_box_sizer)
        top_sizer.Add(self.regular_panel, wx.SizerFlags().DoubleBorder().Expand())

        # Set up the weighting form.
        self.weighted_panel = wx.Panel(self, wx.ID_ANY)
        self.weighted_box_sizer = wx.StaticBoxSizer(wx.VERTICAL, self.weighted_panel, "Weighted Randomization Options")

        self.weighted_sizer = wx.FlexGridSizer(3, 10, 10)
        self.weighted_sizer.AddGrowableCol(1)

        # Add a control for adding static value rows.
        self.add_static_spin = wx.SpinCtrl(self.weighted_box_sizer.GetStaticBox(), wx.ID_ANY, "",
                                           style=wx.SP_ARROW_KEYS, min=game_option.min_value, max=game_option.max_value,
                                           initial=game_option.min_value)

        add_static_button = wx.Button(self.weighted_box_sizer.GetStaticBox(), wx.ID_ANY, "Add")
        add_static_button.Bind(wx.EVT_BUTTON, self.on_add_static_value_to_weights)

        self.weighted_sizer.Add(self.add_static_spin, wx.SizerFlags().Expand())
        self.weighted_sizer.Add(add_static_button)
        self.weighted_sizer.Add(0, 0)

        self.weighted_box_sizer.Add(self.weighted_sizer, wx.SizerFlags().Proportion(1).Expand())
        self.weighted_panel.SetSizer(self.weighted_box_sizer)

        top_sizer.Add(self.weighted_panel, wx.SizerFlags().DoubleBorder().Expand())
        top_sizer.Add(self.CreateButtonSizer(wx.OK | wx.CANCEL), wx.SizerFlags().Expand())

        # Load the weights from the option value.
        if option_value.random and option_value.weighting is not None:
            for weight_value in option_value.weighting:
                self.add_weight_row(RrdValue.from_option_value(weight_value), default_weight=weight_value.weight)

        # Add a default row if there isn't already one.
        if not game_option.default_value.random:
            default_rrd_value = RrdValue.from_static_value(game_option.default_value.value)

            if default_rrd_value not in self.weights:
                default_weight = 0
                if not option_value.random or len(option_value.weighting or []) == 0:
                    default_weight = 50

                self.add_weight_row(default_rrd_value, default_weight=default_weight)

        # Bring in default values for the weighting table.
        if not game_option.named_range:
            def add_static_random_row(rvt: RandomValueType):
                static_rrd_value = RrdValue.from_complex_value(rvt, None)

                if static_rrd_value in self.weights:
                    return

                default_weight = 0
                if game_option.default_value.random and game_option.default_value.range_random_type == rvt:
                    default_weight = 50

                self.add_weight_row(static_rrd_value, default_weight=default_weight, deletable=False)

            add_static_random_row(RandomValueType.UNIFORM)
            add_static_random_row(RandomValueType.LOW)
            add_static_random_row(RandomValueType.MIDDLE)
            add_static_random_row(RandomValueType.HIGH)
        else:
            for value, name in game_option.value_names.ordering:
                rrd_value = RrdValue.from_static_value(value)

                if rrd_value in self.weights:
                    continue

                self.add_weight_row(rrd_value, default_weight=0, deletable=False)

        # Enable the form based on the option value.
        if option_value.random:
            if option_value.weighting is None:
                self.modes_box.SetSelection(1)

                self.regular_panel.Enable()
                self.weighted_panel.Disable()
                self.add_regular_button.Hide()
            else:
                self.modes_box.SetSelection(2)

                self.regular_panel.Enable()
                self.weighted_panel.Enable()
                self.add_regular_button.Show()
        else:
            self.modes_box.SetSelection(0)

            self.regular_panel.Disable()
            self.weighted_panel.Disable()
            self.add_regular_button.Hide()

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

        self.Bind(wx.EVT_BUTTON, self.on_ok, id=wx.ID_OK)

    def get_option_value(self) -> OptionValue:
        result = OptionValue()

        if self.modes_box.GetSelection() == 1:
            result.random = True
            result.weighting = None
            result.range_random_type = self.chosen_random_type

            if self.enable_range_subset.GetValue():
                result.range_subset = (self.subset_min.value, self.subset_max.value)
            else:
                result.range_subset = None
        elif self.modes_box.GetSelection() == 2:
            result.random = True
            result.weighting = []

            for rrd_value, weight in self.weights.items():
                if weight.weight == 0:
                    continue

                sub_option = rrd_value.to_option_value()
                sub_option.weight = weight.weight

                result.weighting.append(sub_option)

        return result

    def on_ok(self, event: wx.CommandEvent):
        if self.modes_box.GetSelection() == 1 and self.enable_range_subset.GetValue():
            if self.subset_min.value >= self.subset_max.value:
                wx.MessageBox("The range subset maximum must be greater than the range minimum.")
                return

            if self.subset_min.value < 0:
                wx.MessageBox("Random ranges with negative bounds are not supported.")
                return

        if self.modes_box.GetSelection() == 2:
            num_nonzero = sum(1 for weight in self.weights.values() if weight.weight > 0)
            if num_nonzero < 2:
                wx.MessageBox("There must be at least two values with a non-zero weight to use weighted randomization.")
                return

        self.EndModal(wx.ID_OK)

    def on_mode_changed(self, event: wx.CommandEvent):
        if event.GetSelection() == 0:
            self.regular_panel.Disable()
            self.weighted_panel.Disable()
            self.add_regular_button.Hide()
        elif event.GetSelection() == 1:
            self.regular_panel.Enable()
            self.weighted_panel.Disable()
            self.add_regular_button.Hide()
        elif event.GetSelection() == 2:
            self.regular_panel.Enable()
            self.weighted_panel.Enable()
            self.add_regular_button.Show()

        self.Layout()
        self.Fit()

    def make_on_choose_random_type_lambda(self, random_type: RandomValueType) -> Callable[[wx.CommandEvent], None]:
        def on_choose_random_type(event: wx.CommandEvent):
            self.chosen_random_type = random_type
        return on_choose_random_type

    def on_range_restrict_toggled(self, event: wx.CommandEvent):
        self.subset_min.Enable(self.enable_range_subset.GetValue())
        self.subset_max.Enable(self.enable_range_subset.GetValue())

    def on_add_static_value_to_weights(self, event: wx.CommandEvent):
        rrd_value = RrdValue.from_static_value(self.add_static_spin.GetValue())

        if rrd_value in self.weights:
            wx.MessageBox("This option is already in the form.")
            return

        self.add_weight_row(rrd_value)

        self.Layout()
        self.Fit()

    def on_add_complex_value_to_weights(self, event: wx.CommandEvent):
        rrd_value: RrdValue

        if self.enable_range_subset.GetValue():
            rrd_value = RrdValue.from_complex_value(self.chosen_random_type,
                                                    (self.subset_min.value, self.subset_max.value))

            if rrd_value.range[0] >= rrd_value.range[1]:
                wx.MessageBox("The range maximum must be greater than the range minimum.")
                return

            if rrd_value.range[0] < 0:
                wx.MessageBox("Random ranges with negative bounds are not supported.")
                return
        else:
            rrd_value = RrdValue.from_complex_value(self.chosen_random_type, None)

        if rrd_value in self.weights:
            wx.MessageBox("This option is already in the form.")
            return

        self.add_weight_row(rrd_value)

        self.Layout()
        self.Fit()

    def add_weight_row(self, value: RrdValue, default_weight: int = 0, deletable: bool = True):
        self.weights[value] = WeightRow(self, value, default_weight, deletable)
