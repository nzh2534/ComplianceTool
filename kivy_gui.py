from kivy.app import App
from kivy.core.window import Window

from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput

from kivy.uix.button import Button

from compliance_tool import compliance_tool

class Grid(GridLayout):
    def __init__(self, **kwargs):
        super(Grid, self).__init__(**kwargs)
        self.cols = 2
        Window.bind(on_dropfile=self.on_drop_file) 

        self.final_path = "N/A"
        self.output = "Drag and drop your USAID NOFO then press Submit!"
        
        self.add_widget(Label(text=self.output))
        # self.add_widget(Label(text=self.final_path))

        self.submit_one = Button(text="Submit", font_size=30)
        self.submit_one.bind(on_press=self.pressed_one)
        self.add_widget(self.submit_one)

    def on_drop_file(self, window, file_path):
        self.final_path = file_path
        return
    
    def pressed_one(self, instance):
        if self.final_path != "N/A":
            compliance_tool(self.final_path)
        else:
            print("Pressed One")

class FH_Compliance_ToolApp(App):
    def build(self):
        return Grid()

if __name__ == '__main__':
    FH_Compliance_ToolApp().run()