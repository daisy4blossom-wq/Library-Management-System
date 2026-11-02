import wx
import psycopg2
connection = psycopg2.connect(dbname="library", user="postgres", password="chinenye_onyeka@2009", host="localhost", port=5432)
cursor = connection.cursor()
class LoginDialog(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, None, title="Login")
        self.user_id = None
        self.Center()
        
        user_sizer = wx.BoxSizer(wx.HORIZONTAL)
        user_text = wx.StaticText(self, label="Username:")
        user_sizer.Add(user_text, 0, wx.ALL| wx.ALIGN_CENTER, 5)
        self.user = wx.TextCtrl(self)
        user_sizer.Add(self.user, 0, wx.ALL, 5)

        pass_sizer = wx.BoxSizer(wx.HORIZONTAL)
        pass_text = wx.StaticText(self, label="Password:")
        pass_sizer.Add(pass_text, 0, wx.ALL | wx.CENTER, 5)
        self.password = wx.TextCtrl(self, style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER)
        self.password.Bind(wx.EVT_TEXT_ENTER, self.onLogin)
        pass_sizer.Add(self.password, 0, wx.ALL, 5)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(user_sizer, 0, wx.ALL, 5)
        main_sizer.Add(pass_sizer, 0, wx.ALL, 5)

        l_btn = wx.Button(self, label="Login")
        l_btn.Bind(wx.EVT_BUTTON, self.onLogin)
        main_sizer.Add(l_btn, 0, wx.ALL | wx.CENTER, 5)

        self.SetSizer(main_sizer)

    def onLogin(self, event):
        current_user = self.user.GetValue()
        cursor.execute("SELECT id, password FROM roles WHERE username = %s", (current_user,))
        rows = cursor.fetchone()
        user_password = self.password.GetValue()
        if rows is not None:
            user_id, saved_password = rows
            if user_password == saved_password:
                self.user_id = user_id
                print("You are logged in")
                self.EndModal(wx.ID_OK)
                return
        wx.MessageBox("Username or Password is incorrect", "Login Denied", style=wx.ICON_INFORMATION)

class MyPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Main app")
        panel = MyPanel(self)
        dlg = LoginDialog()
        dlg.ShowModal()

if __name__ == '__main__':
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()                
