import hou
import tempfile
import types
import collections

def _attributes_to_string(obj, atrr_dict):
    for k, v in atrr_dict.items():
        if isinstance(v, bool) and v == True or v == None:
            obj.attributes_string += '%s '% k.upper()
        elif v == False:
            continue
        elif isinstance(v, (tuple, list)):
            v = list(map(str,v))
            obj.attributes_string += "%s(%s,%s) " % (k.upper(), v[0], v[1])
        else:
            obj.attributes_string += "%s(%s) " % (k.upper(), str(v))

def _randname():
    from random import choice
    from string import ascii_lowercase
    return ''.join(choice(ascii_lowercase) for x in range(4))


def findDialog(name):
    """
    Finds dialog by name. Dialog can be destroyed (destroy()) or shown (show())
    """
    uival = "%s_ui.val" % name
    def show(self):
        self.setValue(uival, 1)
    for dlg in hou.ui.dialogs():
        try:
            val = dlg.value(uival)
        except hou.OperationFailed:
            continue
        else:
            dlg.show = types.MethodType(show, dlg)
            return dlg
    return None


class HBaseContainer(object):
    def __init__(self):
        self.child_list = []
        self.attributes_string = ""
        self.attributes = dict(hstretch = True)

    def addGadget(self, gadget):
        self.child_list.append(gadget)

    def addLayout(self, layout):
        self.child_list.append(layout)

    def setAttributes(self, **kwargs):
        self.attributes.update(kwargs)


class HBaseGadget(object):
    def __init__(self, name, label):
        self.name = "%s.gad" % name
        self.label = label
        self._ui_value = "%s.val" % name
        self.attributes = dict(hstretch = True)
        self.attributes_string = ""
        self.enabled = True
        self.dialog = None
        self.init_value = None
        self.callbacks = set()

    def setAttributes(self, **kwargs):
        """
        Sets various attributes for Gadget object. Attributes are:
        size = [w,h]
        width = unit
        height = unit
        min_size/max_size = [w,h]
        min_width/max_width = unit
        min_height/max_height = unit
        stretch = bool, [w,h]
        hstretch/vstretch = bool
        margin = unit
        hmargin/vmargin = [h,v]
        spacing = unit
        spacing = [h,v]
        justify = [h,v]
        look = "plain", "line", "groove", "bevel", "beveldown"
        rmbmenu = menuref

                """
        self.attributes.update(kwargs)

    def setEnabled(self, value = True):
        self.enabled = value
        if self.dialog:
            self.dialog.enableValue(self._ui_value, value)

    def setValue(self, value):
        if self.dialog:
            self.dialog.setValue(self._ui_value, value)
        else:
            self.init_value = value


    def getValue(self):
        if self.dialog:
            return self.dialog.value(self._ui_value)
        else:
            raise ValueError('Can\'t get value for %s gadget' % self.name)

    def _set_multivalue(self, iterable):
        self.dialog.setValue(self._ui_value[0], iterable[0])
        self.dialog.setValue(self._ui_value[1], iterable[1])
        self.dialog.setValue(self._ui_value[2], iterable[2])


    def connect(self, func):
        self.callbacks.add(func)


class HRowLayout(HBaseContainer):
    def __init__(self):
        super(HRowLayout, self).__init__()

    def __repr__(self):
        _attributes_to_string(self, self.attributes)
        return 'ROW'

class HColumnLayout(HBaseContainer):
    def __init__(self):
        super(HColumnLayout, self).__init__()

    def __repr__(self):
        _attributes_to_string(self, self.attributes)
        return 'COL'


class HCollapserLayout(HBaseContainer):
    def __init__(self, label = 'Collapser', layout = 'horizontal'):
        super(HCollapserLayout, self).__init__()
        self.attributes['layout'] = layout
        self._label = label

    def __repr__(self):
        _attributes_to_string(self, self.attributes)
        return 'COLLAPSER "%s"' % self._label


class HButton(HBaseGadget):
    def __init__(self, name, label):
        super(HButton, self).__init__(name, label)

    def setAttributes(self, **kwargs):
        try:
            # For some reason setting the look attrib on a button, makes it disappear
            del kwargs['look']
        except KeyError:
            pass
        super(HButton, self).setAttributes(**kwargs)

    def __repr__(self):
        _attributes_to_string(self, self.attributes)
        _s = "ACTION_BUTTON \"{label}\" VALUE({value}) ".format(
            label = self.label, value = self._ui_value)
        _s += self.attributes_string
        _s += ';'
        return _s


class HIconButton(HBaseGadget):
    def __init__(self, name, icon):
        super(HIconButton, self).__init__(name, "")
        self._icon = icon
        self.attributes = {"hstretch" : False}

    def setIcon(self, iconpath):
        self._icon = iconpath

    def __repr__(self):
        _attributes_to_string(self, self.attributes)
        _s = "ACTION_ICONBUTTON \"{icon}\" VALUE({value}) ".format(
            icon = self._icon, value = self._ui_value)
        _s += self.attributes_string
        _s += ';'
        return _s


class HCheckbox(HBaseGadget):
    def __init__(self, name, label):
        super(HCheckbox, self).__init__(name, label)

    def isChecked(self):
        return self.getValue()

    def __repr__(self):
        _attributes_to_string(self, self.attributes)
        _s = "TOGGLE_BUTTON \"{label}\" VALUE({value}) ".format(
            label = self.label, value = self._ui_value)
        _s += self.attributes_string
        _s += ';'
        return _s


class HSeparator(HBaseGadget):
    def __init__(self):
        super(HSeparator, self).__init__("", "")

    def __repr__(self):
        _attributes_to_string(self, self.attributes)
        return "SEPARATOR %s;" % self.attributes_string


class HRadioButton(HBaseGadget):
    def __init__(self, name, label):
        super(HRadioButton, self).__init__(name, label)

    def isChecked(self):
        return self.getValue()

    def __repr__(self):
        _attributes_to_string(self, self.attributes)
        _s = "RADIO_BUTTON \"{label}\" VALUE({value}) ".format(
            label = self.label, value = self._ui_value)
        _s += self.attributes_string
        _s += ';'
        return _s


class HLabel(HBaseGadget):
    def __init__(self, label):
        super(HLabel, self).__init__(name = "label_%s" % _randname(), label = label)

    def setEnabled(self, value = True):
        pass

    def __repr__(self):
        _attributes_to_string(self, self.attributes)
        _s = "LABEL \"{label}\" ".format(label = self.label)
        _s += self.attributes_string
        _s += ';'
        return _s

class HStringField(HBaseGadget):
    def __init__(self, name, label):
        super(HStringField, self).__init__(name, label)

    def __repr__(self):
        _attributes_to_string(self, self.attributes)
        _s = "STRING_FIELD \"{label}\" VALUE({value}) ".format(
            label = self.label, value = self._ui_value)
        _s += self.attributes_string
        _s += ';'
        return _s

class HFloatSlider(HBaseGadget):
    def __init__(self, name, label, noInputField = False):
        super(HFloatSlider, self).__init__(name, label)
        self.no_field = noInputField

    def setRange(self, srange):
        self.range = srange

    def lockRange(self):
        self.lock_range = True

    def __repr__(self):
        _attributes_to_string(self, self.attributes)
        if self.no_field:
            slidertype = 'FLOAT_SLIDER'
        else:
            slidertype = 'FLOAT_SLIDER_FIELD'
        _s = "{slider}  \"{label}\" VALUE({value}) {attrs} ".format(
                label = self.label, value = self._ui_value, attrs = self.attributes_string, slider = slidertype)

        if hasattr(self, 'range'):
            _s += "RANGE(%f, %f) " % (self.range[0], self.range[1])
        if hasattr(self, 'lock_range'):
            _s += "LOCK_RANGE "
        _s += ';'
        return _s


class HIntSlider(HBaseGadget):
    def __init__(self, name, label, range = (1, 10), noInputField = False):
        super(HIntSlider, self).__init__(name, label)
        self.no_field = noInputField
        self.range = range

    def setRange(self, srange):
        self.range = srange

    def lockRange(self):
        self.lock_range = True

    def __repr__(self):
        _attributes_to_string(self, self.attributes)
        if self.no_field:
            slidertype = 'INT_SLIDER'
        else:
            slidertype = 'INT_SLIDER_FIELD'
        _s = "{name} = {slider} \"{label}\" VALUE({value}) {attrs} ".format(
                name = self.name, label = self.label, value = self._ui_value,
                attrs = self.attributes_string, slider = slidertype)

        if hasattr(self, 'range'):
            _s += "RANGE(%d, %d) " % (self.range[0], self.range[1])
        if hasattr(self, 'lock_range'):
            _s += "LOCK_RANGE "
        _s += ';'
        return _s

# class HIntSpinner(HBaseGadget):
#     def __init__(self, name, label, increment = 1):
#         super(HIntSpinner, self).__init__(name, label)
#         self.incrementsize = increment
# 
#     def setRange(self, srange):
#         self.range = srange
# 
#     def lockRange(self):
#         self.lock_range = True
# 
#     def __repr__(self):
#         _attributes_to_string(self, self.attributes)
#         _s = "INT_SPINNER_FIELD({increment}) \"{label}\" VALUE({value}) {attrs} ".format(
#                 label = self.label, value = self._ui_value,
#                 attrs = self.attributes_string, increment = self.incrementsize)
# 
#         if hasattr(self, 'range'):
#             _s += "RANGE(%d, %d) " % (self.range[0], self.range[1])
#         if hasattr(self, 'lock_range'):
#             _s += "LOCK_RANGE "
#         _s += ';'
#         return _s

class HFileField(HBaseGadget):
    def __init__(self, name, label, type_filter = 'all'):
        super(HFileField, self).__init__(name, label)
        self.type_filter = type_filter

    def __repr__(self):
        _attributes_to_string(self, self.attributes)
        _s = "FILENAME_FIELD({filter}) \"{label}\" VALUE({value}) {attrs}; ".format(
                filter = self.type_filter, label = self.label, value = self._ui_value,
                attrs = self.attributes_string)
        return _s


class HColorSelector(HBaseGadget):
    def __init__(self, name, label):
        super(HColorSelector, self).__init__(name, label)
        self._ui_value = ["%s.%s" % (self.name, comp) for comp in 'rgb']

    def getValue(self):
        if self.dialog:
            return hou.Color([self.dialog.value(v) for v in self._ui_value])


    def setValue(self, color_value):
        if self.dialog:
            if isinstance(color_value, hou.Color):
                values = color_value.rgb()
            elif isinstance(color_value, collections.Iterable):
                values = tuple(color_value)
            self._set_multivalue(values)
        else:
            self.init_value = color_value


    def setEnabled(self, value = True):
        self.enabled = value
        if self.dialog:
            for val in self._ui_value:
                self.dialog.enableValue(val, value)

    def __repr__(self):
        _attributes_to_string(self, self.attributes)
        _s = "COLOR_FIELD \"{label}\" VALUE({val}) {attrs}".format(
                label = self.label, val = ", ".join(self._ui_value), attrs = self.attributes_string)
        _s += ';'
        return _s

class HVectorField(HBaseGadget):
    def __init__(self, name, label, size = 3):
        assert 2 < size <= 4, "HVectorField size can be 2, 3 or 4"
        super(HVectorField, self).__init__(name, label)
        self._size = size
        valcomponent = "xyzw"[:self._size]
        self._ui_value = ["%s.%s" % (self._ui_value, comp) for comp in valcomponent]
        self._vecclass = {2: hou.Vector2, 3: hou.Vector3, 4: hou.Vector4}[size]

    def getValue(self):
        if self.dialog:
            val = [0.0 for i in range(self._size)]
            tmp = [self.dialog.value(v) for v in self._ui_value]
            for i,v in enumerate(tmp):
                if v:
                    val[i] = float(v)
            return val

    def setValue(self, new_value):
        if not isinstance(new_value, (list, tuple, self._vecclass)):
            raise ValueError("Value type should be list, tuple or hou.Vector%d" % self._size)
        values = list(new_value)
        if self.dialog:
            self._set_multivalue(values)
        else:
            self.init_value = values

    def setEnabled(self, value = True):
        self.enabled = value
        if self.dialog:
            for val in self._ui_value:
                self.dialog.enableValue(val, value)

    def __repr__(self):
        _s = "FLOAT_VECTOR_FIELD({size}) \"{label}\" VALUE({value}) {attrs};".format(
                size = self._size, label = self.label,
                value = ", ".join(self._ui_value),
                attrs = self.attributes_string)
        return _s

class _HBaseMenu(HBaseGadget):
    def __init__(self, name, label, items):
        super(_HBaseMenu, self).__init__(name, label)
        self.items = items

    def menuItems(self):
        if self.dialog:
            return self.dialog.menuItems(self._ui_value)

    def setMenuItems(self, items):
        self.items = items
        if self.dialog:
            self.dialog.setMenuItems(self._ui_value, self.items)

    def menuDefString(self):
        _s = "%s = SELECT_MENU\n{\n" % self._ui_value
        for i in self.items:
            _s += '\t"%s"\n' % str(i)
        _s += "}"
        return _s

    def __repr__(self):
        return ""


class HStringMenu(_HBaseMenu):
    def __init__(self, name, label, items = []):
        super(HStringMenu, self).__init__(name, label, items)

    def __repr__(self):
        _attributes_to_string(self, self.attributes)
        _s = super(HStringMenu, self).__repr__()
        _s += '\nSELECT_MENU_BUTTON "%s:" ' % self.label
        _s += "MENU(%s);" % self._ui_value
        return _s


class HIconMenu(_HBaseMenu):
    def __init__(self, name, label, items = []):
        super(HIconMenu, self).__init__(name, label, items)


    def __repr__(self):
        _attributes_to_string(self, self.attributes)
        _s = super(HIconMenu, self).__repr__()
        _s += '\nACTION_MENU_BUTTON "%s:" ' % self.label
        _s += "MENU(%s);" % self._ui_value
        return _s


class HBaseWindow(object):
    def __init__(self, name, title):
        self.name = name
        self.type = 'WINDOW'
        self.title = title
        self._ui_value = "%s_ui.val" % name
        self.ui_str = ""
        self.attributes = dict(hstretch = True, value = self._ui_value, look = 'plain')
        self.attributes_string = ""
        self.items_list = []
        self._gadgets_flatten_list = []
        self._menu_definitions = ""
        self.dialog = None

    def _indentWrite(self, string):
        self.ui_str += " "*4 + string + '\n'

    def setWindowAttributes(self, **kwargs):
        self.attributes.update(kwargs)


    def addGadget(self, gadget):
        self.items_list.append(gadget)

    def addLayout(self, layout):
        self.items_list.append(layout)

    def setWindowLayout(self, layout):
        if layout not in ('vertical', 'horizontal', 'cell'):
            raise ValueError('Unknown layout: %s' % layout)
        self.attributes_string += "LAYOUT(%s) " % layout

    def _write_menus(self):
        ## Menus definition must be written erlier in the script
        def traverse_layout(item):
            if isinstance(item, _HBaseMenu):
                self._indentWrite(item.menuDefString())
            elif isinstance(item, HBaseContainer):
                for sub in item.child_list:
                    traverse_layout(sub)
        for item in self.items_list:
            traverse_layout(item)

    def _write_gadget(self, gadget):
        self._indentWrite(gadget.__repr__())

    def _write_layouts(self):
        _attributes_to_string(self, self.attributes)
        def traverse_layout(item):
            if isinstance(item, HBaseGadget):
                self._write_gadget(item)
                self._gadgets_flatten_list.append(item)

            elif isinstance(item, HBaseContainer):
                self._indentWrite(item.__repr__())
                self._indentWrite('{')
                self._indentWrite(item.attributes_string)
                for sub_item in item.child_list:
                    traverse_layout(sub_item)
                self._indentWrite('}\n')

        for item in self.items_list:
            traverse_layout(item)


    def _make_ui_string(self):
        _attributes_to_string(self, self.attributes)
        self.ui_str = "{name} = {dtype} \"{title}\"".format(
            name = self.name, dtype = self.type, title = self.title)
        self.ui_str += "\n{\n"
        self._indentWrite(self.attributes_string)
        self._write_menus()
        self._write_layouts()
        self.ui_str += "\n}"

    def initUI(self):
        self._make_ui_string()
        tmp_f = tempfile.mktemp(suffix ='huilib')
        with open(tmp_f, 'w') as f:
            f.write(self.ui_str)
        try:
            self.dialog = hou.ui.createDialog(tmp_f)
            self.dialog.name = self.name
        except hou.OperationFailed as e:
            print("{a:#^50}\n{ui_str}\n{a:#^50}".format(error = e, ui_str = self.ui_str, a = '#'))
            raise e
        finally:
            from os import remove
            remove(tmp_f)

        # Pass dialog instance to gadget objects , also set Enabled/Disable attr
        for item in self._gadgets_flatten_list:
            item.dialog = self.dialog

            # Set init values
            if item.init_value:
                item.setValue(item.init_value)

            # Add callbacks
            if item.callbacks:
                for cb in item.callbacks:
                    if hasattr(cb, '__call__'):
                        if isinstance(item._ui_value, list):
                            for valuecomp in item._ui_value:
                                self.dialog.addCallback(valuecomp, cb)
                        else:
                            self.dialog.addCallback(item._ui_value, cb)


            # Set enable/disable
            try:
                item.setEnabled(item.enabled)
            except hou.OperationFailed as e:
                pass

    def show(self):
        self.dialog.setValue(self._ui_value, True)

    def close(self):
        self.dialog.setValue(self._ui_value, False)

    def _print(self):
        if not self.ui_str:
            self._make_ui_string()
        print(self.ui_str)


class HDialog(HBaseWindow):
    def __init__(self, name, title):
        super(HDialog, self).__init__(name, title)
        self.type = 'DIALOG'
