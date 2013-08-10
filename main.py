from __future__ import division
from collections import Counter

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import *
from kivy.properties import (ObjectProperty, ListProperty, NumericProperty,
        BooleanProperty, ReferenceListProperty, BoundedNumericProperty)
from kivy.uix.scatter import ScatterPlane
from kivy.uix.slider import Slider

from kivy.garden.tickmarker import TickMarker

import life

BLACK = (0, 0, 0)
BLUE = (0, 0, 1)
CYAN = (0, 1, 1)

class TickSlider(Slider, TickMarker):
    pass

class LifeBoard(ScatterPlane):
    cells = ObjectProperty(Counter())
    dead_colour = ListProperty()
    alive_colour = ListProperty()
    aged_cell_colour = ListProperty()
    run_time = NumericProperty()

    cell_width = NumericProperty(10)
    cell_size = ReferenceListProperty(cell_width, cell_width)
    draw = BooleanProperty(False)
    erase = BooleanProperty(False)

    def update_cells(self, *args):
        self.cells = life.next_iteration(self.cells)

    def on_cells(self, instance, value):
        self.canvas.clear()
        with self.canvas:
            for cell, age in value.items():
                pos = [cell[0]*self.cell_width, cell[1]*self.cell_width]
                Color(*self.interpolate_colour(age))
                Rectangle(size=self.cell_size, pos=pos)

    def interpolate_colour(self, cell_age):
        new_colour = self.aged_cell_colour
        old_colour = self.alive_colour
        age = min(cell_age - 1, 16)
        delta = [(new - old)*age/16 for new, old in zip(new_colour, old_colour)]
        colour = [old + d for old, d in zip(old_colour, delta)]
        return colour

    def toggle_draw(self, value):
        self.draw = value == 'down'

    def toggle_erase(self, value):
        self.erase = value == 'down'

    def toggle_run(self, value):
        if value == 'down':
            self.update_cells()
            Clock.schedule_interval(self.update_cells, self.run_time)
        else:
            Clock.unschedule(self.update_cells)

    def on_touch_down(self, touch):
        if self.draw or self.erase:
            self.edit_cells(touch)
        else:
            super(LifeBoard, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.draw or self.erase:
            self.edit_cells(touch)
        else:
            super(LifeBoard, self).on_touch_move(touch)

    def edit_cells(self, touch):
        cells = self.cells
        cell_width = self.cell_width

        x, y = self.to_local(*touch.pos)

        pos = (int(x//cell_width), int(y//cell_width))
        cell_pos = (pos[0]*cell_width, pos[1]*cell_width)

        if self.draw and not cells[pos]:
            cells[pos] = 1
            self.canvas.add(Color(*self.alive_colour))
        elif self.erase and cells[pos]:
            cells[pos] = 0
            self.canvas.add(Color(*self.dead_colour))
        else:
            return

        self.canvas.add(Rectangle(size=self.cell_size, pos=cell_pos))

        self.cells = cells

class LifeApp(App):
    run_time = BoundedNumericProperty(1, min=0.016, max=1)
    dead_colour = ListProperty()
    alive_colour = ListProperty()
    aged_colour = ListProperty()

    def build_config(self, config):
        config.setdefaults('life', {
            'run_time': 0.3,
            'dead_colour': BLACK,
            'alive_colour': BLUE,
            'aged_colour': CYAN,
            })

    def on_config_change(self, config, section, key, value):
        if config is self.config:
            if section == 'life':
                if key == 'run_time':
                    self.run_time = value
                elif key == 'dead_colour':
                    self.dead_colour = value
                elif key == 'alive_colour':
                    self.alive_colour = value
                elif key == 'aged_colour':
                    self.aged_colour = value

    def build(self):
        config = self.config
        self.run_time = config.getfloat('life', 'run_time')
        self.dead_colour = config.get('life', 'dead_colour')
        self.alive_colour = config.get('life', 'alive_colour')
        self.aged_colour = config.get('life', 'aged_colour')

if __name__ == '__main__':
    LifeApp().run()
