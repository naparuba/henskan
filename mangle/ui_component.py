class UIComponent:
    def __init__(self, id, dom_element):
        self._id = id
        self._dom_element = dom_element
    
    
    def __find_child(self, obj, look_name):
        if obj.objectName() == look_name:
            return obj
        for child in obj.children():
            result = self.__find_child(child, look_name)
            if result:
                return result
        return None
    
    
    def _find_child_id(self, dom_id):
        return self.__find_child(self._dom_element, dom_id)
    
    
    def disable(self):
        self._dom_element.setProperty('enabled', False)
    
    
    def enable(self):
        self._dom_element.setProperty('enabled', True)


class UIInput(UIComponent):
    def __init__(self, id, dom_element):
        super().__init__(id, dom_element)
        
        self._value = ''
    
    
    def disable(self):
        super().disable()
        self._dom_element.setProperty("color", "grey")
        self._dom_element.setProperty("placeholderTextColor", "grey")
    
    
    def enable(self):
        super().enable()
        self._dom_element.setProperty("color", "white")
        self._dom_element.setProperty("placeholderTextColor", "red")
    
    
    def got_no_value(self):
        self.enable()
    
    
    def set_value(self, s):
        # type: (str) -> None
        print(f'UIInput:: {self._id} => set_value: {s}')
        self._value = s
        if not self._value:
            self.got_no_value()
        else:
            self._dom_element.setProperty("text", s)
            self._dom_element.setProperty("color", "green")
            self._dom_element.setProperty("placeholderTextColor", "purple")


class UIButton(UIComponent):
    ACTIVE_COLOR = 'green'
    NOT_ACTIVE_COLOR = 'grey'
    
    
    def __init__(self, id, dom_element):
        super().__init__(id, dom_element)
    
    
    def disable(self):
        super().disable()
        self._dom_element.setProperty("color", self.NOT_ACTIVE_COLOR)
    
    
    def set_active(self):
        self._dom_element.setProperty("color", self.ACTIVE_COLOR)
    
    
    def set_not_active(self):
        self._dom_element.setProperty("color", self.NOT_ACTIVE_COLOR)


class UIRectButton(UIButton):
    pass


class UIRectButtonConvert(UIRectButton):
    def _change_image(self, image_path):
        img = self._find_child_id('col_convert_img')
        print(f'img: {img}')
        if img:
            img.setProperty("source", image_path)
        else:
            print(f'Cannot find image {image_path}')
    
    
    def disable(self):
        super().disable()
        self._change_image('../img/shock_off.png')
    
    
    def enable(self):
        super().enable()
        self._change_image('../img/shock_on.png')


class UIComboBox(UIComponent):
    def __init__(self, id, dom_element):
        super().__init__(id, dom_element)
    
    
    def disable(self):
        super().disable()
        self._dom_element.setProperty("color", "grey")
    
    
    def enable(self):
        super().enable()
        self._dom_element.setProperty("color", "green")
    
    
    def set_value(self, s, index):
        # type: (str, int) -> None
        print(f'UIComboBox:: {self._id} => set_value: {s} {index}')
        self._dom_element.setProperty("currentIndex", index)


class UIProgressBar(UIComponent):
    def __init__(self, id, dom_element):
        super().__init__(id, dom_element)
    
    
    def disable(self):
        super().disable()
        self._dom_element.setProperty("color", "grey")
    
    
    def enable(self):
        super().enable()
        self._dom_element.setProperty("color", "green")
