class UIComponent:
    def __init__(self, id, dom_element):
        self._id = id
        self._dom_element = dom_element
    
    
    def disable(self):
        self._dom_element.setProperty('enabled', False)
    
    
    def enable(self):
        self._dom_element.setProperty('enabled', True)


class UIInput(UIComponent):
    def __init__(self, id, dom_element):
        super().__init__(id, dom_element)
        
        self._value = None
    
    
    def disable(self):
        super().disable()
        self._dom_element.setProperty("color", "grey")
        self._dom_element.setProperty("placeholderTextColor", "grey")


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


class UIComboBox(UIComponent):
    def __init__(self, id, dom_element):
        super().__init__(id, dom_element)
    
    
    def disable(self):
        super().disable()
        self._dom_element.setProperty("color", "grey")


class UIProgressBar(UIComponent):
    def __init__(self, id, dom_element):
        super().__init__(id, dom_element)
        
        self._value = None
    
    
    def disable(self):
        super().disable()
        self._dom_element.setProperty("color", "grey")
