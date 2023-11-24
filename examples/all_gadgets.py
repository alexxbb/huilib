import hou
from random import random
import huilib
import importlib
importlib.reload(huilib)

class TestDialog(huilib.HDialog):
    def __init__(self, name, title):
        super(TestDialog, self).__init__(name, title)
        self.setWindowLayout('vertical')
        self.setWindowAttributes(stretch = True, margin = 0.1, spacing = 0.1, min_width = 5)
        self.toggleEnable = huilib.HCheckbox('enable_fields', 'Enable All Fields')

        self.geoFileField = huilib.HFileField('geo_field', 'Geo:', type_filter = 'geo')
        self.imgFileField = huilib.HFileField('img_field', 'Img:', type_filter = 'pic')
        self.geoFileField.setEnabled(False)
        self.imgFileField.setEnabled(False)

        rowL = huilib.HRowLayout()
        slidersLayout = huilib.HColumnLayout()
        buttonLayout = huilib.HColumnLayout()
        rowL.addLayout(slidersLayout)
        rowL.addLayout(buttonLayout)

        ## Sliders And Button
        self.slider1 = huilib.HFloatSlider('slider1', 'Float Slider 1')
        self.slider1.setRange((0,1))
        self.slider1.setValue(0.4)
        self.slider1.lockRange()

        self.slider2 = huilib.HFloatSlider('slider2', 'Float Slider 2')
        self.slider2.setRange((0.001, 0.1 ))

        self.chkBTN1 = huilib.HButton('check_btn1', 'Check 1')
        self.chkBTN1.setAttributes(vstretch = True)
        self.chkBTN2 = huilib.HButton('check_btn2', 'Check 2')
        self.chkBTN2.setAttributes(vstretch = True)
        slidersLayout.addGadget(self.slider1)
        slidersLayout.addGadget(self.slider2)
        buttonLayout.addGadget(self.chkBTN1)
        buttonLayout.addGadget(self.chkBTN2)



        ###
        self.stringField = huilib.HStringField('field', 'Text Field')
        self.stringField.setEnabled(False)
        self.colorSelector = huilib.HColorSelector('clr_selector', 'Color')
        self.colorSelector.setValue([0.2, 0, 1])
        self.addGadget(self.toggleEnable)
        self.addGadget(self.geoFileField)
        self.addGadget(self.imgFileField)
        self.addGadget(self.stringField)
        self.addGadget(self.colorSelector)

        self.btn1 = huilib.HButton('btn1','List Nodes')
        self.btn2 = huilib.HButton('btn2','Rand Color')
        self.btn3 = huilib.HButton('btn3','Button 3')

        rowLayout = huilib.HRowLayout()
        rowLayout.addGadget(self.btn1)
        rowLayout.addGadget(self.btn2)
        rowLayout.addGadget(self.btn3)

        ### CollapserLayout
        collapser = huilib.HCollapserLayout(layout = 'vertical')
        collapser.addLayout(rowLayout)

        self.addLayout(collapser)
        self.addLayout(rowL)

        self.label1 = huilib.HLabel('This is Label 1. Any Text can be here')
        self.label2 = huilib.HLabel('This is Label 2. Any Text can be here')
        self.vec1 = huilib.HVectorField('vec1', 'Vector Field 1')
        self.vec2 = huilib.HVectorField('vec2', 'Vector Field 2')

        self.addGadget(self.label1)
        self.addGadget(self.label2)
        self.addGadget(self.vec1)
        self.addGadget(self.vec2)


        # Menus
        self.menuRow = huilib.HRowLayout()
        self.menu1 = huilib.HStringMenu('menu1', 'Menu 1', ['item1', 'item2', 'item3'])
        self.menu2 = huilib.HStringMenu('menu2', 'Menu 2')
        self.menu2.setMenuItems(['Saint-Petersburg', 'Moscow', 'Kamchatka'])
        self.menuRow.addGadget(self.menu1)
        self.menuRow.addGadget(self.menu2)
        self.addLayout(self.menuRow)

        # Close Button
        self.closeBTN = huilib.HButton('close', 'Close')
        bottomRow = huilib.HRowLayout()
        bottomRow.addGadget(self.closeBTN)

        # Separator
        sep = huilib.HSeparator()
        sep.setAttributes(look = 'bevel')
        self.addGadget(sep)
        self.addLayout(bottomRow)
        self.addGadget(sep)

        # Connect callbacks
        self.toggleEnable.connect(self.cb_enable_fields)
        self.btn1.connect(self.cb_listNodes)
        self.closeBTN.connect(self.close)
        self.btn2.connect(self.cb_randomizeColor)
        self.btn3.connect(self.cb_printStringFields)

        # This method should always be called last!!
        self.initUI()


    def cb_listNodes(self):
        nodes = [node.name() for node in hou.node('/obj').children()]
        self.menu1.setMenuItems(nodes)

    def cb_randomizeColor(self):
        self.colorSelector.setValue([random(), random(), random()])


    def cb_printStringFields(self):
        self.geoFileField.getValue()


    def cb_enable_fields(self):
        val = self.toggleEnable.isChecked()
        if val:
            self.geoFileField.setEnabled(True)
            self.imgFileField.setEnabled(True)
            self.colorSelector.setEnabled(True)
            self.stringField.setEnabled(True)
        else:
            self.geoFileField.setEnabled(False)
            self.imgFileField.setEnabled(False)
            self.colorSelector.setEnabled(False)
            self.stringField.setEnabled(False)

    def cb_getColor(self):
        clr = self.colorSelector.getValue()
        print(clr)


if __name__ == '__main__':
    ui = TestDialog(name = 'test', title = 'Test UI')
    ui.show()
