import threading
from threading import Thread
import color

from kivy.lang.builder import Builder
from kivy.clock import mainthread
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from scrolllabel import ScrollLabel
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.recycleview import RecycleView


class ThreadSafePopup:
    POPUP_KV = """
Popup:
    id: ts_popup_control
    title: 'SET TITLE'
    auto_dismiss: False
    content: ts_popup_content
    size: (450, 250)
    size_hint: (None, None)
    #on_open: controltofocus.focus = True
    GridLayout:
        cols: 1
        orientation: 'vertical'
        id: ts_popup_content
        #size_hint: (.9, .9)
        #canvas.before:
        #    Color:
        #        rgba: 1, 0, 0, 1
        #    Rectangle:
        #        size: self.size
        #        pos: self.pos
        Label:
            text: ' '
            #text_size: self.size
            markup: True
            shorten: True
            shorten_from: 'center'
            ellipses_options: { 'color':(1,.5,.5,1),'underline':True }
            id: ts_message
            size_hint_y: 0.5
            wrap: True
            halign: 'left'
        ProgressBar:
            id: ts_progress
            size_hint_y: 0.05
            visible: True
            size_hint_y: 0.15 if self.visible else 0
            size_hint_x: 1 if self.visible else 0
            opacity: 1 if self.visible else 0
            disabled: not self.visible
        Button:
            id: ts_cancel
            text: 'Cancel'
            #text_size: self.size
            on_press: ts_popup_control.dismiss()
            visible: True
            size_hint_y: 0.15 if self.visible else 0
            size_hint_x: 1 if self.visible else 0
            opacity: 1 if self.visible else 0
            disabled: not self.visible
        Button:
            id: ts_ok
            text: "OK"
            #text_size: self.size
            on_press: ts_popup_control.dismiss() # ts_cancel.visible=False; #  ts_content._trigger_layout() #ts_control.dismiss()
            visible: True
            size_hint_y: 0.15 if self.visible else 0
            size_hint_x: 1 if self.visible else 0
            opacity: 1 if self.visible else 0
            disabled: not self.visible


    """
    KV_FILE = None
    
    def __init__(self, output_label=None):
        self.popup_control = None
        self.output_control = None

        self.init_popup()
        pass
    
    @mainthread
    def init_popup(self):
        if self.popup_control is None:
            # Create a new popup control
            self.popup_control = Builder.load_string(ThreadSafePopup.POPUP_KV)

        pass

    @mainthread
    def open(self):
        # Show the popup
        if self.popup_control is None:
            self.p("}}rnNo popup control set - canceling open}}xx")
            return False
        
        self.popup_control.open()
        #self.popup_control.ids.ts_popup_content._trigger_layout()
    
    @mainthread
    def dismiss(self):
        if self.popup_control is None:
            self.p("}}rnNo popup control set - canceling dismiss}}xx")
            return False
        
        self.popup_control.dismiss()
    
    @mainthread
    def set_title(self, text):
        if self.popup_control is None:
            self.p("}}rnNo popup control set - canceling set_title}}xx")
            return False
        
        self.popup_control.title = text

    @mainthread
    def set_message(self, text, clear_previous_text=False):
        # Do this in the main thread so that it doesn't mess with kivy
        if self.popup_control is not None:
            if clear_previous_text is True:
                self.popup_control.ids.ts_message.text = text
            else:
                self.popup_control.ids.ts_message.text += text
        else:
            self.p("}}rnNo popup control set - canceling set message}}xx")
    
    @mainthread
    def set_text(self, text_control, text, clear_previous_text=False):
        # Do this in the main thread so that it doesn't mess with kivy
        if text_control is not None:
            if clear_previous_text is True:
                text_control.text = text
            else:
                text_control.text += text
        else:
            p("}}rnNo popup control set - canceling set text}}xx")

    @mainthread
    def hide_ok(self, hide=True):
        if self.popup_control is not None:
            self.popup_control.ids.ts_ok.visible = not hide
        pass

    @mainthread
    def hide_cancel(self, hide=True):
        if self.popup_control is not None:
            self.popup_control.ids.ts_cancel.visible = not hide
        pass

    @mainthread
    def hide_progress(self, hide=True):
        if self.popup_control is not None:
            self.popup_control.ids.ts_progress.visible = not hide
        pass

    def p(self, msg="", end=True, out=None, debug_level=0):
        if self.output_control is None:
            color.p(msg, end=end, out=out, debug_level=debug_level)
            return

        # Convert color codes?
        msg = color.translate_color_codes_to_markup(msg)

        if end is True:
            end = "\n"
        # Print to the label
        self.set_text(self.output_control, msg + end)
        #self.output_label.text += msg + end
