from typing import TypeVar, Generic, List, Dict, Tuple

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
