huilib (Houdini UI Library)
=========

Python library for building native houdini user interfaces.

This library is a simple Python wrapper around Houdini .ui scripting language. Although it doesn't cover even a half of all available houdini UI controlls, it does provide most usefull of them, such as buttons, textFields, checkboxes, menus, etc.
The coding style is very similar to PyQt.

It was written for fun.Hope someone finds it usefull.

*See examples/all_gadgets.py*

![huilib_ui.jpg](https://bitbucket.org/repo/q9KEkp/images/3011376572-huilib_ui.jpg)

# Simple Import Dialog

    :::python
        from huilib import *
        
        class SimpleImportDialog(HDialog):
            def __init__(self, name, title):
                super(SimpleImportDialog, self).__init__(name, title)
                self.setWindowLayout('vertical')
        
                # Column Layout
                col = HColumnLayout()
                self.filefield = HFileField('geo_field', 'Geo:', type_filter = 'geo')
        
                # Buttons in row Layout
                self.importButton = HButton('import', 'Import')
                self.closeButton = HButton('close', 'Close')
                row = HRowLayout()
                row.addGadget(self.importButton)
                row.addGadget(self.closeButton)
        
                # Add file field and buttons raw layout
                col.addGadget(self.filefield)
                col.addLayout(row)
        
                # Connect button signals
                self.closeButton.connect(self.close)
                self.importButton.connect(self.cb_import)
                self.addLayout(col)
        
                # This method should ALWAYS be called last!
                self.initUI()
        
        
            def cb_import(self):
                val = self.filefield.getValue()
                if not val:
                    return
                geo = hou.node('/obj').createNode('geo')
                geo.node('file1').parm('file').set(val)
        
        
        if __name__ == '__main__':
            ui = SimpleImportDialog(name = 'import_dlg', title = 'Import Dialog')
            ui.show()


_hou.alexx@gmail.com_
