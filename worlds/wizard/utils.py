from typing import TypeVar, Generic, List, Dict, Tuple, Optional

import wx
import wx.lib.newevent

K = TypeVar('K')
V = TypeVar('V')


class OrderedBijection(Generic[K, V]):
    ordering: List[Tuple[K, V]]
    forward: Dict[K, V]
    backward: Dict[V, K]
    keys: Dict[K, int]
    values: Dict[V, int]

    def __init__(self):
        self.ordering = []
        self.forward = {}
        self.backward = {}
        self.keys = {}
        self.values = {}

    def append(self, key: K, value: V):
        self.keys[key] = len(self.ordering)
        self.values[value] = len(self.ordering)
        self.ordering.append((key, value))
        self.forward[key] = value
        self.backward[value] = key


class DoubleMap(Generic[K]):
    pass


PickNumberCommandEvent, EVT_PICK_NUMBER = wx.lib.newevent.NewCommandEvent()


class NumericPicker(wx.Panel):
    min: int
    max: int

    slider: wx.Slider
    spin_ctrl: wx.SpinCtrl

    def __init__(self, parent: wx.Window, wid: wx.WindowIDRef, min: int, max: int, default_value: int):
        wx.Panel.__init__(self, parent=parent, id=wid)

        self.min = min
        self.max = max
        self._value = default_value

        self.slider = wx.Slider(self, wx.ID_ANY, value=self.value, minValue=self.min, maxValue=self.max)
        self.slider.Bind(wx.EVT_SLIDER, self.on_slider_changed)

        self.spin_ctrl = wx.SpinCtrl(self, wx.ID_ANY, style=wx.SP_ARROW_KEYS, min=self.min, max=self.max,
                                     initial=self.value)
        self.spin_ctrl.Bind(wx.EVT_SPINCTRL, self.on_spin_changed)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.slider, wx.SizerFlags().Proportion(1).Expand())
        sizer.AddSpacer(10)
        sizer.Add(self.spin_ctrl)

        self.SetSizer(sizer)

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, v: int):
        if v != self._value:
            self._value = v

            if self.slider.GetValue() != v:
                self.slider.SetValue(v)

            if self.spin_ctrl.GetValue() != v:
                self.spin_ctrl.SetValue(str(v))

            event = PickNumberCommandEvent(self.GetId())
            event.SetInt(v)

            self.ProcessWindowEvent(event)

    def on_slider_changed(self, event: wx.CommandEvent):
        self.value = self.slider.GetValue()

    def on_spin_changed(self, event: wx.SpinEvent):
        self.value = self.spin_ctrl.GetValue()


PickItemCommandEvent, EVT_PICK_ITEM = wx.lib.newevent.NewCommandEvent()


class FilterableItemPicker(wx.Panel):
    items: List[str]

    source_filter: wx.TextCtrl
    source_list: wx.ListView

    def __init__(self, parent: wx.Window, items: List[str]):
        wx.Panel.__init__(self, parent=parent)

        self.items = items

        self.source_filter = wx.TextCtrl(self, wx.ID_ANY)
        self.source_filter.Bind(wx.EVT_TEXT, self.on_filter_edited)

        self.source_list = wx.ListView(self, wx.ID_ANY, style=wx.LC_REPORT | wx.LC_NO_HEADER | wx.LC_SINGLE_SEL)
        self.source_list.Bind(wx.EVT_LEFT_DCLICK, self.on_double_click)

        self.update_source_list()

        filter_sizer = wx.BoxSizer(wx.HORIZONTAL)
        filter_sizer.Add(wx.StaticText(self, wx.ID_ANY, "Filter:"), wx.SizerFlags().Center())
        filter_sizer.AddSpacer(10)
        filter_sizer.Add(self.source_filter, wx.SizerFlags().Proportion(1).Expand())

        add_btn = wx.Button(self, wx.ID_ANY, "Add")
        add_btn.Bind(wx.EVT_BUTTON, self.on_add_clicked)

        left_sizer = wx.BoxSizer(wx.VERTICAL)
        left_sizer.Add(filter_sizer, wx.SizerFlags().Expand())
        left_sizer.AddSpacer(10)
        left_sizer.Add(self.source_list, wx.SizerFlags().Proportion(1).Expand())
        left_sizer.AddSpacer(10)
        left_sizer.Add(add_btn, wx.SizerFlags().Center())

        self.SetSizerAndFit(left_sizer)

        self.source_list.SetColumnWidth(0, wx.LIST_AUTOSIZE)

    def get_selected(self) -> Optional[str]:
        selection = self.source_list.GetFirstSelected()
        if selection == -1:
            return None

        return self.source_list.GetItemText(selection, 0)

    def update_source_list(self):
        self.source_list.ClearAll()
        self.source_list.AppendColumn("Value")

        i = 0
        for list_item in self.items:
            if len(self.source_filter.GetValue()) > 0 and\
                    list_item.lower().find(self.source_filter.GetValue().lower()) == -1:
                continue

            self.source_list.InsertItem(i, list_item)
            i += 1

        self.source_list.SetColumnWidth(0, wx.LIST_AUTOSIZE)

    def pick_item(self):
        selected_text = self.get_selected()
        if selected_text is None:
            return

        picked_event = PickItemCommandEvent(self.GetId())
        picked_event.SetString(selected_text)

        self.ProcessWindowEvent(picked_event)

    def on_filter_edited(self, event: wx.CommandEvent):
        self.update_source_list()

    def on_add_clicked(self, event: wx.CommandEvent):
        self.pick_item()

    def on_double_click(self, event: wx.MouseEvent):
        self.pick_item()
