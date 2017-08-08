from kivy.core.text import Label as CoreLabel
from kivy.uix.recycleview import RecycleView
from kivy.properties import (NumericProperty, StringProperty, OptionProperty,
                             BooleanProperty, AliasProperty)
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.clock import Clock

Builder.load_string("""
<ScrollLabel>:
    RecycleView:
        id: rv
        pos: root.pos
        size: root.size
        key_viewclass: "viewclass"
        key_size: "height"
        viewclass: 'Label'
        RecycleBoxLayout:
            default_size: None, dp(56)
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height
            orientation: 'vertical'
    

<-ScrollLabelPart>:
    canvas:
        Color:
            rgba: (1, 1, 1, 1)
        Rectangle:
            pos: self._rect_x, self.y
            size: self.texture_size
            texture: root.texture
""")


class ScrollLabelPart(Label):
    def _get_rect_x(self):
        if self.halign == "left":
            return 0
        elif self.halign == "center":
            ret = (self.width - self.texture_size[0]) / 2.
        else:
            ret = self.width - self.texture_size[0]
        return int(ret)
    _rect_x = AliasProperty(_get_rect_x, bind=("texture_size", "x", "width"))


class ScrollLabel(Widget):

    text = StringProperty()
    font_size = NumericProperty("14sp")
    font_name = StringProperty("Roboto")
    halign = OptionProperty("center", options=("left", "center", "right"))
    line_height = NumericProperty()
    markup = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(ScrollLabel, self).__init__(**kwargs)
        self._trigger_refresh_label = Clock.create_trigger(self.refresh_label)
        self.bind(
            text=self._trigger_refresh_label,
            font_size=self._trigger_refresh_label,
            font_name=self._trigger_refresh_label,
            halign=self._trigger_refresh_label,
            width=self._trigger_refresh_label,
            markup=self._trigger_refresh_label)
        self._trigger_refresh_label()

    def refresh_label(self, *args):
        lcls = CoreLabel
        label = lcls(text=self.text,
                     text_size=(self.width, None),
                     halign=self.halign,
                     font_size=self.font_size,
                     font_name=self.font_name,
                     markup=self.markup)
        label.resolve_font_name()
        label.render()

        # get lines
        font_name = self.font_name
        font_size = self.font_size
        halign = self.halign
        markup = self.markup
        data = ({
            "index": index,
            "viewclass": "ScrollLabelPart",
            "text": " ".join([word.text for word in line.words]),
            "font_name": font_name,
            "font_size": font_size,
            "height": line.h,
            "size_hint_y": None,
            "halign": halign,
            "markup": markup,
        } for index, line in enumerate(label._cached_lines))
        self.ids.rv.data = data
        self.ids.rv.scroll_y = 0

if __name__ == "__main__":
    from kivy.base import runTouchApp
    LOREM = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur nec arcu accumsan, lacinia libero sed, cursus nisi. Curabitur volutpat mauris id ornare finibus. Cras dignissim arcu viverra, bibendum est congue, tempor elit. Vivamus luctus sapien sapien, id tincidunt eros molestie vitae. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut commodo eget purus vel efficitur. Duis facilisis ex dolor, vel convallis odio pharetra quis. Vivamus eu suscipit tortor. Proin a tellus a nisl iaculis aliquam. Nam tristique ipsum dui, ut faucibus libero lacinia id. Pellentesque eget rhoncus justo, quis interdum eros. Suspendisse felis lorem, gravida in orci ac, auctor malesuada turpis. Fusce dapibus urna dolor, id viverra enim semper a. Proin dignissim neque quis ante commodo feugiat.
Duis dictum sagittis urna nec dapibus. Vestibulum ac elit vel nunc euismod lobortis. Vivamus sit amet tortor in diam consectetur ultrices vitae vulputate leo. Aenean vehicula orci leo, eget fringilla enim condimentum eget. Sed sapien lacus, vulputate nec ligula eget, luctus feugiat risus. Nullam ultricies quam ac metus imperdiet, eget scelerisque dolor commodo. Ut nec elementum orci. Cras massa lacus, consectetur varius est a, congue pulvinar magna. Proin nec sapien facilisis, tristique turpis vel, malesuada leo. Phasellus faucibus justo vel risus tristique, in laoreet ligula vestibulum. Vestibulum varius eget nibh nec convallis. Morbi eu diam at turpis mollis hendrerit. Aenean sed turpis lectus.
Suspendisse pharetra ligula nec faucibus mattis. Aliquam et felis eget augue efficitur aliquam viverra ut tellus. Aliquam sagittis ut sapien venenatis condimentum. Quisque in turpis ac nisi vehicula commodo vel porttitor erat. Maecenas lobortis, sapien dictum congue gravida, nulla urna ultricies lorem, at tincidunt ex arcu nec eros. Maecenas egestas a augue sit amet euismod. Praesent ut sapien metus. Curabitur lorem erat, consectetur quis rhoncus quis, tristique ac ligula. Suspendisse justo magna, cursus id mauris et, lacinia egestas neque.
Suspendisse bibendum sit amet est eget ullamcorper. Duis pellentesque tristique nisi. Donec id dolor eget arcu lobortis sollicitudin vel et justo. Vivamus vel risus eget felis condimentum tempus ac sed dui. Donec placerat risus quis metus auctor sagittis. Pellentesque vel sem dolor. Praesent erat eros, facilisis placerat ultrices et, interdum quis risus. Donec eleifend risus dapibus, laoreet felis ut, fermentum neque. Aenean purus elit, congue non tempus quis, dictum quis metus. Maecenas finibus rutrum bibendum. Ut vestibulum dapibus felis vel luctus. Aliquam vitae consequat eros, quis ultricies tortor. Quisque eu accumsan erat, id commodo nisi.
Etiam nec risus porttitor, placerat est et, facilisis diam. Etiam vel feugiat ligula. Aliquam at quam congue, lacinia velit nec, congue nibh. In varius quis elit vel sollicitudin. Vivamus molestie elementum ipsum et vehicula. Etiam non augue quis tortor ultrices maximus. Etiam vel blandit nibh. Nullam facilisis posuere erat vel mattis. Vestibulum mattis condimentum purus efficitur vehicula. Aliquam consequat interdum eros eu semper. Etiam feugiat, erat at tempor tincidunt, odio eros maximus sapien, sit amet lacinia nibh tortor quis dui. In hac habitasse platea dictumst.
"""

    runTouchApp(ScrollLabel(text=LOREM))
