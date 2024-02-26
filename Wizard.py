from typing import List

import kivy

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import BooleanProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.scrollview import ScrollView
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.uix.switch import Switch
from kivy.uix.textinput import TextInput

import Options
from worlds.AutoWorld import AutoWorldRegister

handled_in_js = {"start_inventory", "local_items", "non_local_items", "start_hints", "start_location_hints",
                 "exclude_locations", "priority_locations"}


class SelectableWorldListLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    pass


class SelectableLabel(RecycleDataViewBehavior, Label):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))

            App.get_running_app().world_changed(self.index)
        else:
            print("selection removed for {0}".format(rv.data[index]))


class WorldList(RecycleView):
    def __init__(self, **kwargs):
        super(WorldList, self).__init__(**kwargs)

    def refresh(self, worlds):
        self.data = [{"text": game_name} for game_name in worlds]


class OptionsPane(ScrollView):
    pass


class Wizard(App):
    base_title: str = "Archipelago Wizard"
    scrollview: OptionsPane
    grid: GridLayout
    container: BoxLayout
    world_list: WorldList

    configured_worlds: List[str]

    def build_options_pane(self, game_name):
        self.container.remove_widget(self.scrollview)

        self.grid = GridLayout(cols=2, padding=50, spacing=30, size_hint_y=None)

        world = AutoWorldRegister.world_types[game_name]
        for option_name, option in world.options_dataclass.type_hints.items():
            if option_name in handled_in_js:
                continue

            display_name = option.display_name if hasattr(option, "display_name") else option_name

            option_label = Label(text=f"{display_name}:", valign="top", halign="left", size_hint_x=None)
            option_label.bind(texture_size=option_label.setter('size'))
            option_label.bind(texture_size=option_label.setter('text_size'))
            self.grid.add_widget(option_label)

            if issubclass(option, Options.Toggle):
                self.grid.add_widget(Switch(active=option.default))

            elif issubclass(option, Options.Range):
                range_label = Label(text=str(option.default), size_hint_x=None)
                range_label.bind(texture_size=range_label.setter('size'))
                range_label.bind(texture_size=range_label.setter('text_size'))

                range_slider = Slider(min=option.range_start, max=option.range_end, value=option.default, step=1)
                range_slider.range_label = range_label
                range_slider.bind(value=self.range_changed)

                range_layout = BoxLayout(orientation='horizontal')
                range_layout.add_widget(range_slider)
                range_layout.add_widget(range_label)

                if issubclass(option, Options.NamedRange):
                    all_options = []
                    default_option = "Custom"
                    for key, val in option.special_range_names.items():
                        all_options.append(key)
                        if val == option.default:
                            default_option = key
                    all_options.append("Custom")

                    range_spinner = Spinner(text=default_option, values=all_options)
                    range_slider.range_spinner = range_spinner

                    upper_layout = BoxLayout(orientation="vertical", size_hint_y=None)
                    upper_layout.add_widget(range_spinner)
                    upper_layout.add_widget(range_layout)
                    self.grid.add_widget(upper_layout)

                else:
                    self.grid.add_widget(range_layout)

            elif issubclass(option, Options.Choice):
                default_option = ""
                all_choices = []
                for sub_option_id, sub_option_name in option.name_lookup.items():
                    if sub_option_name == "random":
                        continue

                    if sub_option_id == option.default:
                        default_option = option.get_option_name(sub_option_id)

                    all_choices.append(option.get_option_name(sub_option_id))

                self.grid.add_widget(Spinner(text=default_option, values=all_choices, size_hint_y=None, height=50,
                                             pos_hint={'center_x': .5, 'center_y': .5}, halign="left"))

            else:
                self.grid.add_widget(TextInput())

        self.grid.bind(minimum_height=self.grid.setter("height"))
        self.scrollview = OptionsPane(size_hint=(1, 1))
        #self.scrollview.bind(height=self.container.setter('height'))
        self.scrollview.add_widget(self.grid)
        self.container.add_widget(self.scrollview)

    def build(self):
        self.grid = GridLayout(cols=2, padding=50, spacing=30)
        self.scrollview = OptionsPane()

        self.configured_worlds = [game_name for game_name in AutoWorldRegister.world_types.keys()]
        self.world_list = WorldList()
        self.world_list.refresh(self.configured_worlds)

        self.container = BoxLayout(orientation="horizontal")
        self.container.add_widget(self.world_list)
        self.container.add_widget(self.scrollview)
        return self.container

    @staticmethod
    def range_changed(range: Slider, value: float):
        range.range_label.text = str(int(value))

    def world_changed(self, index):
        print(index)
        self.build_options_pane(self.configured_worlds[index])


if __name__ == '__main__':
    Builder.load_string('''
<SelectableLabel>:
    size_hint_x: None
    text_size: self.size
    halign: "left"
    # Draw a background to indicate selection
    canvas.before:
        Color:
            rgba: (.0, 0.9, .1, .3) if self.selected else (0, 0, 0, 1)
        Rectangle:
            pos: self.pos
            size: self.size
<WorldList>:
    size_hint_x: 0.5
    viewclass: 'SelectableLabel'
    SelectableWorldListLayout:
        padding: 20
        default_size: None, dp(32)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
        multiselect: False
''')

    Wizard().run()
