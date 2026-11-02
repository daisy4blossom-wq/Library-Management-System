import wx
import os
import urllib.parse as url
import webbrowser as web
import datetime as DT
import test_practice
from test_practice import LoginDialog
from dotenv import load_dotenv
load_dotenv()
import cloudinary
import cloudinary.uploader
import cloudinary.api
import time
import psycopg2
import requests
MAX_BORROWED = 5
LOAN_DAYS = 14
DUE_SOON = 2
connection = psycopg2.connect(dbname="library", user="postgres", password="chinenye_onyeka@2009", host="localhost", port=5432)

class LibraryFrame(wx.Frame):
    def __init__(self, user_id):
        super().__init__(None, title="Digital Library", size=(800, 600))
        #LoginDialog.ShowModal()
        self.panel = LibraryPanel(self, user_id)
        self.Show()

class LibraryPanel(wx.Panel):
    def __init__(self, parent, user_id):
        super().__init__(parent)
        self.current_user_id = user_id
        self.cursor = connection.cursor() 
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        h_sixer = wx.BoxSizer(wx.HORIZONTAL)
        top_bar_hsizer = wx.BoxSizer(wx.HORIZONTAL)
        side_panel_sixer = wx.BoxSizer(wx.VERTICAL)
        self.content_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        
        top_bar = wx.Panel(self)
        body_panel = wx.Panel(self)
        body_panel.SetBackgroundColour("grey")
        top_bar.SetBackgroundColour(wx.Colour("#654321"))
        top_bar.SetMinSize((-1, 50))
        self.search_text = wx.TextCtrl(top_bar, size=(200, -1), style=wx.TE_PROCESS_ENTER)
        self.search_text.SetHint("Search Library..")
        self.search_text.Bind(wx.EVT_TEXT_ENTER, self.on_search_enter)
        side_panel = wx.Panel(body_panel)
        side_panel.SetBackgroundColour(wx.Colour("#814510"))
        side_panel.SetMinSize((80, -1))
        self.content_panel = wx.Panel(body_panel)
        self.content_panel.SetBackgroundColour(wx.Colour("#031D31"))
        side_button = wx.Button(side_panel, label="Home")
        side_button.Bind(wx.EVT_BUTTON, self.on_click, side_button)
        my_button = wx.Button(side_panel, label="My Books")
        my_button.Bind(wx.EVT_BUTTON, self.on_click,my_button)
        due_btn = wx.Button(side_panel, label="Due Books")
        due_btn.Bind(wx.EVT_BUTTON, self.on_click,due_btn)
                
                
        self.home_page = HomePage(self.content_panel, user_id=self.current_user_id)
        self.my_page = MyBooks(self.content_panel, self.home_page, user_id=self.current_user_id)
        self.home_page.my_page = self.my_page
        self.due_page = DueBooks(self.content_panel, user_id=self.current_user_id)
        self.home_page.search_text = self.search_text
                
        
      
        main_sizer.Add(top_bar, proportion=0, flag=wx.EXPAND)
        main_sizer.Add(body_panel, proportion=1, flag=wx.EXPAND)
        h_sixer.Add(side_panel, proportion=0, flag=wx.EXPAND)
        h_sixer.Add(self.content_panel, proportion=1, flag=wx.EXPAND)
        top_bar_hsizer.Add(self.search_text, proportion=1, flag=wx.ALL | wx.EXPAND, border=10)          
        side_panel_sixer.Add(side_button, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        side_panel_sixer.Add(my_button, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        side_panel_sixer.Add(due_btn, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
                
        
        self.content_panel_sizer.Add(self.home_page, proportion=1, flag=wx.EXPAND)
        self.content_panel_sizer.Add(self.my_page, proportion=1, flag=wx.EXPAND)
        self.content_panel_sizer.Add(self.due_page, proportion=1, flag=wx.EXPAND)

        self.home_page.Show()
        #Hides these pages on startup
        self.my_page.Hide()
        self.due_page.Hide()

        side_panel.SetSizer(side_panel_sixer)
        self.content_panel.SetSizer(self.content_panel_sizer)
        body_panel.SetSizer(h_sixer)
        top_bar.SetSizer(top_bar_hsizer)
        
        self.SetSizer(main_sizer)
        self.Layout()

    def on_click(self, event):
        button_click = event.GetEventObject().GetLabel()
        print(f"You clicked on {button_click}")
        self.home_page.Hide()
        self.my_page.Hide()
        self.due_page.Hide()
        if button_click == "Home":
            #self.home_page.Show()
            self.search_text.ChangeValue("")
            self.on_search_enter(None)

        elif button_click == "My Books":
            self.my_page.load_library()
            self.my_page.Show()

        elif button_click == "Due Books":
            self.due_page.overdue_books()
            self.due_page.Show()
        else:
            return
       
        self.content_panel.Layout()

    def on_search_enter(self, event):
        self.my_page.Hide()
        self.due_page.Hide()
        self.home_page.Show()
        self.content_panel.Layout()
        self.home_page.on_search_books()


class HomePage(wx.Panel):
    def __init__(self, parent, user_id):
        super().__init__(parent)
        self.cursor = connection.cursor()
        self.user_id = user_id
        self.SetBackgroundColour(wx.Colour("#654321"))
        home_sizer = wx.BoxSizer(wx.VERTICAL)
        self.h_sizer = wx.WrapSizer(wx.HORIZONTAL, flags=0)
       

        self.scrolled = wx.ScrolledWindow(self, style=wx.VSCROLL)
        home_sizer.Add(self.scrolled, proportion=1, flag=wx.ALL | wx.EXPAND, border=10)
        self.scrolled.SetScrollRate(5, 5)
        self.SetSizer(home_sizer)
        self.scrolled.SetSizer(self.h_sizer)
        self.load_cards()
        self.GetParent().Layout()

    def image_books(self, image_path, label_text, label_author, copies, item_id):
        card = wx.Panel(self.scrolled)
        card.SetBackgroundColour(wx.Colour("#FFFFFF"))
        card.SetMinSize((130, 230))
        card.SetMaxSize((130, 230))
        card_sizer = wx.BoxSizer(wx.VERTICAL)
        book_image = wx.Image(image_path, wx.BITMAP_TYPE_ANY)
        if book_image.IsOk():
            book_image = book_image.Scale(110, 160, quality=wx.IMAGE_QUALITY_HIGH)
            book_img = wx.Bitmap(book_image)
        else:
            book_img = wx.Bitmap(110, 160)
        btp_item = wx.StaticBitmap(card, bitmap=book_img)
        card.item_id = item_id
        card.title = label_text
        btp_item.Bind(wx.EVT_RIGHT_DOWN, lambda event, item_id=item_id: self.borrow_function(item_id))
        btp_text = wx.StaticText(card, label=label_text, size=(110, -1), style=wx.ST_ELLIPSIZE_END | wx.ALIGN_CENTER_HORIZONTAL)
        btp_text.Bind(wx.EVT_RIGHT_DOWN, lambda event, item_id=item_id: self.borrow_function(item_id))
        aut_text =  wx.StaticText(card, label=label_author, size=(110, -1), style=wx.ST_ELLIPSIZE_END | wx.ALIGN_CENTER_HORIZONTAL)
        aut_text.Bind(wx.EVT_RIGHT_DOWN, lambda event, item_id=item_id: self.borrow_function(item_id))
        tip = f"{label_text}\n{label_author}\n{copies} copies available"
        btp_item.SetToolTip(tip)
        btp_text.SetToolTip(tip)
        aut_text.SetToolTip(tip)
        btp_text.SetForegroundColour(wx.Colour("#000000"))
        aut_text.SetForegroundColour(wx.Colour("#000000"))
        card_sizer.Add(btp_item, proportion=0, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border=5)
        card_sizer.Add(btp_text, proportion=0, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border=5)
        card_sizer.Add(aut_text, proportion=0, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border=5)
        card.SetSizer(card_sizer)
        self.h_sizer.Add(card, proportion=0, flag=wx.ALL, border=10)
        

    def load_cards(self, rows=None):
        #to avoid flickering of my book panels
        self.Freeze()
        try:
            self.h_sizer.Clear(delete_windows=True)
            if rows is None:
                self.cursor = connection.cursor()
                self.cursor.execute("""SELECT id, title, author, book_image, available_copies FROM mini_library""")
                rows = self.cursor.fetchall()
                self.cursor.close()
            base_dir = os.path.dirname(os.path.abspath(__file__))
            cover_dir = os.path.join(base_dir, "covers")
            placeholder = os.path.join(cover_dir, "placeholder.jpg")
            #view book covers
            for item_id, title, author, book_image, available_copies  in rows:
                image_path = placeholder
                if book_image:
                    candidate = os.path.join(cover_dir, book_image)
                    if os.path.exists(candidate):
                        image_path = candidate
                    else:
                        print("missing image file:", candidate)
                self.image_books(image_path, title, author, available_copies, item_id)

            self.scrolled.FitInside()
            self.scrolled.Layout()
            self.Layout()
            self.GetParent().Layout()
            self.scrolled.Refresh()
        finally:
            self.Thaw()

    def borrow_function(self, item_id):
        if not self.loan_count():
            return
        self.cursor = connection.cursor()
        self.cursor.execute("SELECT title, author, available_copies, book_image FROM mini_library WHERE id = %s", (item_id,))
        title, author, copies, book_image = self.cursor.fetchone()
        if copies <= 0:
            wx.MessageBox("Sorry, no copies are available", "Borrow", wx.OK | wx.ICON_WARNING)
            return
        answer = wx.MessageBox(message=f"Borrow '{title}'?", caption="Borrow Confirmation", style=wx.YES_NO | wx.ICON_WARNING)
        if answer == wx.NO:
            print("No books borrowed")
            return
        try:
            self.cursor.execute("UPDATE mini_library SET available_copies = available_copies - 1 WHERE id= %s AND available_copies > 0", (item_id,))
            if self.cursor.rowcount == 0:
                connection.rollback()
                wx.MessageBox("Sorry, the last copy was just taken", "Borrow", wx.OK | wx.ICON_WARNING)
                return
            self.cursor.execute("INSERT INTO loans(book_id, borrower_name, borrow_date, user_id, due_date) VALUES (%s, %s, NOW(), %s, CURRENT_DATE + %s)", (item_id, self.user_id, self.user_id, LOAN_DAYS))
            connection.commit()
        except Exception as e:
            connection.rollback()
            wx.MessageBox(str(e), "Could not borrow this book", wx.OK | wx.ICON_ERROR)
            return
        base_dir = os.path.dirname(os.path.abspath(__file__))
        cover_dir = os.path.join(base_dir, "covers")
        image_path = os.path.join(cover_dir, "placeholder.jpg")
        if book_image and os.path.exists(os.path.join(cover_dir, book_image)):
            image_path = os.path.join(cover_dir, book_image)
        
        #wx.CallAfter(self.load_cards)
        wx.CallAfter(self.library_display, image_path, item_id, title, author)
    def library_display(self, image_path, id, label_text, label_author):
        print("Library display called!", image_path)
        self.my_page.load_library()

    def loan_count(self): 
        self.cursor = connection.cursor()   
        self.cursor.execute("SELECT COUNT(*) FROM loans WHERE user_id = %s AND return_date IS NULL", (self.user_id,) )
        activeloans = self.cursor.fetchone()[0]
        if activeloans >= 5:
            wx.MessageBox("Borrower has reached their borrow limit", "Borrow Limit")
            self.cursor.close()
            return False
        self.cursor.execute("SELECT COUNT(*) FROM loans WHERE user_id = %s AND return_date IS NULL AND due_date < CURRENT_DATE", (self.user_id,) )
        pastcount = self.cursor.fetchone()[0]
        if pastcount > 0:
                wx.MessageBox("Borrower has overdue debts", "Clear debts")
                self.cursor.close()
                return False
        self.cursor.close()
        return True

    def on_search_books(self, event=None):
        print("on search called")
        self.cursor = connection.cursor()
        query = self.search_text.GetValue().strip()
        try:
            if query:
                search_query = "%" + query + "%"
                self.cursor.execute("SELECT id, title, author, book_image, available_copies FROM mini_library WHERE title ILIKE %s OR author ILIKE %s", (search_query, search_query))
            else:
                self.cursor.execute("SELECT id, title, author, book_image, available_copies FROM mini_library")
            rows = self.cursor.fetchall()
            print("search rows", len(rows), repr(query))
            self.cursor.close()
            self.load_cards(rows)
            if query and not rows:
                wx.MessageBox("No items match search word", "Search", wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            connection.rollback()
            print("Search failed", e)
        

class MyBooks(wx.Panel):
    def __init__(self, parent, home_page, user_id):
        super().__init__(parent)
        self.cursor = connection.cursor()
        self.user_id = user_id
        self.home_page = home_page
        self.SetBackgroundColour(wx.Colour("#031D31"))

        self.shelf_sizer = wx.BoxSizer(wx.VERTICAL)
        self.book_shelf = wx.ScrolledWindow(self, style=wx.VSCROLL)
        self.book_shelf.SetScrollRate(5, 5)
        self.shelf_wrap = wx.WrapSizer(wx.HORIZONTAL, flags=0)

        self.book_shelf.SetSizer(self.shelf_wrap)
        self.shelf_sizer.Add(self.book_shelf, proportion=1, flag=wx.ALL |wx.EXPAND, border=10)
        self.SetSizer(self.shelf_sizer)
        self.load_library()
       

    def add_images_library(self, image_path, label_text, label_author, item_id):
        img = wx.Image(image_path, wx.BITMAP_TYPE_ANY)
        if img.IsOk():
            img = img.Scale(110, 160, quality=wx.IMAGE_QUALITY_HIGH)  
            test_img = wx.Bitmap(img)
        else:
            test_img = wx.Bitmap(110, 160)
        #image panel
        card = wx.Panel(self.book_shelf)
        card.SetBackgroundColour(wx.Colour("#FFFFFF"))
        card.SetMinSize((130, 200))
        card.SetMaxSize((130, 200))
        #card panel sizer
        card_sizer = wx.BoxSizer(wx.VERTICAL)
        cover = wx.StaticBitmap(card, bitmap=test_img)
        #add book link  
        cover.Bind(wx.EVT_LEFT_DCLICK, lambda event, item_id=item_id: self.double_click(item_id))
        cover.Bind(wx.EVT_RIGHT_DOWN, lambda event, item_id=item_id: self.returned_books(item_id))
        title_text = wx.StaticText(card, label=label_text, size=(110, -1), style=wx.ST_ELLIPSIZE_END | wx.ALIGN_CENTER_HORIZONTAL)
        title_text.Bind(wx.EVT_LEFT_DCLICK, lambda event, item_id=item_id: self.double_click(item_id))
        title_text.Bind(wx.EVT_RIGHT_DOWN, lambda event, item_id=item_id: self.returned_books(item_id))
        aut_text =  wx.StaticText(card, label=label_author, size=(110, -1), style=wx.ST_ELLIPSIZE_END | wx.ALIGN_CENTER_HORIZONTAL)
        aut_text.Bind(wx.EVT_LEFT_DCLICK, lambda event, item_id=item_id: self.double_click(item_id))
        aut_text.Bind(wx.EVT_RIGHT_DOWN, lambda event, item_id=item_id: self.returned_books(item_id))

        card_sizer.Add(cover, proportion=0, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border=5)
        card_sizer.Add(title_text, proportion=0, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border=5)
        card_sizer.Add(aut_text, proportion=0, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border=5)
        card.SetSizer(card_sizer)
        self.shelf_wrap.Add(card, proportion=0, flag=wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_TOP, border=10)
        self.book_shelf.Fit()
        self.Fit()
        self.book_shelf.Layout()
        self.shelf_wrap.Layout()
        self.Layout()
        self.book_shelf.Refresh()

#save current books in my library
    def load_library(self):
            self.shelf_wrap.Clear(delete_windows=True)
            #view book covers
            base_dir = os.path.dirname(os.path.abspath(__file__))
            cover_dir = os.path.join(base_dir, "covers")
            placeholder = os.path.join(cover_dir, "placeholder.jpg")
            self.cursor = connection.cursor()
            self.cursor.execute("""SELECT DISTINCT mini_library.id, mini_library.title, mini_library.author, mini_library.book_image, mini_library.available_copies
                                 FROM mini_library
                                INNER JOIN loans ON mini_library.id = loans.book_id
                                WHERE loans.user_id = %s AND loans.return_date IS NULL
                                ORDER BY mini_library.id""", (self.user_id,))
            rows = self.cursor.fetchall()
            print("my books rows:", len(rows), "for user", self.user_id)
            self.cursor.close()
            
            for item_id, title, author, book_image, available_copies  in rows:
                image_path = placeholder
                if book_image:
                    candidate = os.path.join(cover_dir, book_image)
                    if os.path.exists(candidate):
                        image_path = candidate
                else:
                    print("could not load image", candidate)
                self.add_images_library(image_path, title, author, item_id)
            self.book_shelf.Layout()
            self.book_shelf.FitInside()
            self.shelf_wrap.Layout()
            self.Layout()
            self.GetParent().Layout()
            self.Refresh()
    
    def returned_books(self, item_id):
        self.cursor = connection.cursor()
        answer = wx.MessageBox(message="Return?", caption="Return Confirmation", style=wx.YES_NO)
        if answer == wx.NO:
            print("No books returned")
            return
        else:
            self.cursor.execute("""UPDATE loans
                                SET return_date = CURRENT_TIMESTAMP 
                                WHERE book_id= %s AND return_date IS NULL""", (item_id,))

            self.cursor.execute("""UPDATE mini_library
                                SET available_copies = available_copies + 1
                                WHERE id= %s""", (item_id,))
            connection.commit()
            wx.MessageBox("Book returned succesfully", "Returns", style=wx.OK | wx.ICON_INFORMATION)
            wx.CallAfter(self.load_library)
            #self.Layout()
            #self.Refresh()
    

    def double_click(self, item_id):
        reader = wx.Frame(None,title="Book Content", size=(700, 600))
        self.output_view = wx.TextCtrl(reader, style= wx.TE_MULTILINE | wx.TE_READONLY)
        self.cursor = connection.cursor()
        self.cursor.execute("SELECT book_link FROM mini_library WHERE id = %s", (item_id,))
        rows = self.cursor.fetchone()
        self.cursor.close()
        for link in rows:
            parsed_url = url.urlparse(link)
            if parsed_url.scheme == "https" and parsed_url.netloc:
                web.open(link, new=0, autoraise=True)
            else:
                clicked_url = cloudinary.utils.cloudinary_url(link, type="authenticated", resource_type="raw", sign_url=True, secure=True)[0]
                print(clicked_url)
                try:
                    response = requests.get(clicked_url, timeout=15)
                    response.raise_for_status()
                    if response.status_code == 200:
                        response.encoding = "utf-8"
                        data = response.text
                        self.output_view.SetValue(data)
                except requests.RequestException as error:
                    wx.MessageBox(message="Book content not found", caption="Book unable to load", style=wx.ICON_ERROR)
                
        reader.Show()
        return rows

class DueBooks(wx.Panel):
    def __init__(self, parent, user_id):
        super().__init__(parent)
        self.cursor = connection.cursor()
        self.SetBackgroundColour(wx.Colour("#031D31"))
        self.user_id = user_id
        self.rchild_panel = wx.Panel(self)
        self.rchild_panel.SetBackgroundColour(wx.Colour("#031D31"))
        
        
        self.r_sizer = wx.BoxSizer(wx.VERTICAL)
        self.dchild_sizer = wx.WrapSizer(wx.HORIZONTAL, 0)
        
        self.r_sizer.Add(self.rchild_panel, proportion=1, flag=wx.ALL | wx.EXPAND)
        self.SetSizer(self.r_sizer)
        self.rchild_panel.SetSizer(self.dchild_sizer)

    def overdue_books(self):
        self.dchild_sizer.Clear(delete_windows=True)
        self.cursor = connection.cursor()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        cover_dir = os.path.join(base_dir, "covers")
        placeholder = os.path.join(cover_dir, "placeholder.jpg")
        self.cursor.execute("""SELECT DISTINCT mini_library.id, mini_library.title, mini_library.book_image, loans.due_date
                                        FROM mini_library
                                        INNER JOIN loans ON mini_library.id = loans.book_id
                                        WHERE loans.user_id = %s AND loans.return_date IS NULL
                                        ORDER BY due_date""", (self.user_id,))
        rows = self.cursor.fetchall()
        self.cursor.close()
                    
        for item_id, title, book_image, due_date  in rows:
            image_path = placeholder
            if book_image:
                candidate = os.path.join(cover_dir, book_image)
                if os.path.exists(candidate):
                    image_path = candidate
                else:
                    print("could not load image", candidate)
            self.add_due_cards(image_path, title, due_date)
        self.dchild_sizer.Layout()
        self.rchild_panel.Layout()
        self.r_sizer.Layout()
        self.Layout()

    def add_due_cards(self, image_path, title, due_date):
        select_date = DT.date.today()
        if due_date == None:
            status_code = "No due date"
            color = wx.Colour("grey")
        else:
            if isinstance(due_date, DT.datetime):
                due_date = due_date.date()
            days_remain = (due_date - select_date).days
            word = "day" if abs(days_remain) == 1 else "days"

            if days_remain < 0:
                status_code = f"{-days_remain} {word} overdue"
                color = wx.Colour("#FF0000")

            elif days_remain ==  0:
                status_code = "Due Today"
                color = wx.Colour("#ee882f")

            elif days_remain <= DUE_SOON:
                status_code = f"Due in {days_remain} {word}"
                color = wx.Colour("#d1670b")

            else:
                status_code = f"Due {due_date.strftime('%d %b')}"
                color = wx.Colour("#000000")

        img = wx.Image(image_path, wx.BITMAP_TYPE_ANY)
        if img.IsOk():
            img = img.Scale(110, 160, quality=wx.IMAGE_QUALITY_HIGH)  
            test_img = wx.Bitmap(img)
        else:
            test_img = wx.Bitmap(110, 160)
                #image panel
        card = wx.Panel(self.rchild_panel)
        card.SetBackgroundColour(wx.Colour("#FFFFFF"))
        card.SetMinSize((130, 230))
        card.SetMaxSize((130, 230))
                #card panel sizer
        card_sizer = wx.BoxSizer(wx.VERTICAL)
        cover = wx.StaticBitmap(card, bitmap=test_img)      
        title_text = wx.StaticText(card, label=title, size=(110, -1), style=wx.ST_ELLIPSIZE_END | wx.ALIGN_CENTER_HORIZONTAL)
        title_text.SetToolTip(title)
        status_text = wx.StaticText(card, label=status_code, size=(110, -1), style=wx.ST_ELLIPSIZE_END | wx.ALIGN_CENTER_HORIZONTAL)
        status_text.SetToolTip(status_code)
        status_text.SetForegroundColour(color)
        
        card_sizer.Add(cover, proportion=0, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border=5)
        card_sizer.Add(title_text, proportion=0, flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, border=5)
        card_sizer.Add(status_text, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5 )
        card.SetSizer(card_sizer)
        self.dchild_sizer.Add(card, proportion=0, flag=wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_TOP, border=10)
        
            


if __name__ == '__main__':
    app = wx.App(redirect=False)
    dlg = test_practice.LoginDialog()
    interface = dlg.ShowModal()
    user_id = dlg.user_id
    dlg.Destroy()
    if interface == wx.ID_OK and user_id is not None:
        frame = LibraryFrame(user_id)
        app.MainLoop()
