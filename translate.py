import os
import json
import tkinter as tk
import tkinter.font as tkFont
import tkinter.messagebox as messagebox
from asyncio import get_event_loop
import pyperclip
import asyncio
from EdgeGPT import Chatbot, ConversationStyle
from selenium import webdriver
from selenium.webdriver.common.by import By
import concurrent.futures
import threading

class EntryWithMenu(tk.Entry):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)

        # create a right click menu
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label='cut', command=self.cut)
        self.menu.add_command(label='copy', command=self.copy)
        self.menu.add_command(label='paste', command=self.paste)
        self.menu.add_command(label='paste as plain text', command=self.paste_plain_text)
        self.menu.add_separator()
        self.menu.add_command(label='select all', command=self.select_all)

        # bind right click
        self.bind('<Button-3>', self.show_menu)

    def show_menu(self, event):
        self.menu.post(event.x_root, event.y_root)

    def cut(self):
        self.event_generate('<<Cut>>')

    def copy(self):
        self.event_generate('<<Copy>>')

    def paste(self):
        self.event_generate('<<Paste>>')

    def paste_plain_text(self):
        try:
            text = self.clipboard_get()
            self.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.insert(tk.INSERT, text)
        except tk.TclError:
            messagebox.showwarning('Notice', 'Copy item is empty and cannot be pasted')

    def select_all(self):
        self.selection_range(0, tk.END)

options = webdriver.ChromeOptions()
driver = webdriver.Chrome()
driver.get('https://desk.oneforma.com/')

# Initialize Tkinter Window
window = tk.Tk()
window.title("Translator based on New Bing")

# default font was 12
FONT = tkFont.Font(size=12)  

# multiply 1.2 to the default font size, used for bigger the button and word
FONT.config(size=int(FONT['size'] * 1.2))

window.option_add("*Font", FONT)

# Create a array of languages
languages = ["Chinese", "French", "German", "Spanish", "Italian", "Japanese", "Korean", "English"]

#Initialize selected language
language_var_origin = tk.StringVar(value=languages[0])
language_var_translate = tk.StringVar(value=languages[7])

language_label = tk.Label(window, text="Select used language：")
language_option = tk.OptionMenu(window, language_var_origin, *languages)

language_label_tr = tk.Label(window, text="Select targeted langauge：")
language_option_tr = tk.OptionMenu(window, language_var_translate, *languages)

language_label.pack()
language_option.pack()
language_label_tr.pack()
language_option_tr.pack()

bot_instance = None
bot_called_num = 0

async def main(bot_instance,bot_called_num):
    #Nothing happen when no question entered
    if(question_entry.get() == "") :
        return
    
    #Check forr the number of calling in this API, If reach 19 times, make a new calling(20 is maximum number of call)
    if(bot_called_num > 18):
        bot_called_num = 0
        bot_instance = None
        close_bot(bot_instance)
    
    if(bot_called_num == 0):
        bot = Chatbot(cookiePath='./cookies.json')
    
    if bot_instance == None:
        bot_instance = bot
    
    response = await bot.ask(prompt=f"You need to act as a translator to translate {language_var_origin.get()} to {language_var_translate.get()}. Translate the following question with don't capitalize the first letter and don't add a full stop at the end. And you only need to show word that translated, here are the sentences, '{question_entry.get()}'", conversation_style=ConversationStyle.precise, wss_link="wss://sydney.bing.com/sydney/ChatHub")
    bot_called_num += 1
    #await bot.close()

    json_string = json.dumps(response)
    data = json.loads(json_string)
    answer = data['item']['messages'][1]['text']
    
    print(answer)
    
    answer_label.config(text=f"Result：{answer}")
    window.update_idletasks()
        
    if 'https://desk.oneforma.com/' in driver.current_url:
        switch_iFrame()
        #If there is the second request, previous answer will be removed from the textarea
        driver.find_element(By.ID,"caption-text").clear()
        #When inside the iFrame there is a textarea with id: caption-text, try to fill in the answer generated
        driver.find_element(By.ID,"caption-text").send_keys(answer)

# Create a label for text need to translate
question_label = tk.Label(window, text="Please enter text need to translate：")
question_entry = EntryWithMenu(window, width=50)
question_entry.bind("<Return>", lambda event: run_main_in_thread(bot_instance, bot_called_num))
question_label.pack()
question_entry.pack()

async def close_bot(bot):
    await bot.close()

def on_closing():
    loop = get_event_loop()
    loop.create_task(close_bot(bot_instance))
    window.destroy()

def switch_iFrame():
        #trying switch to iFrame with id: webapp_frame, *except* is used for second request, change to default and change iFrame again
        try:
            driver.switch_to.frame("webapp_frame")
        except:
            driver.switch_to.default_content()
            driver.switch_to.frame("webapp_frame")

def clear_text():
    question_entry.delete(0, tk.END)

#Copy the answer and clear the text field
def copy_answer():
    answer = answer_label.cget("text")[7:]
    pyperclip.copy(answer)
    clear_text()

def run_main_in_thread(bot_instance, bot_called_num):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(main, bot_instance, bot_called_num)

def run_main_in_thread_with_threading(bot_instance, bot_called_num):
    threading.Thread(target=asyncio.run, args=(main(bot_instance, bot_called_num),)).start()
    
# Add a button to translate
translate_button = tk.Button(window, text="Translate", command=lambda: run_main_in_thread_with_threading(bot_instance, bot_called_num),font=FONT)
translate_button.pack()

# add a label to show a translated result
answer_label = tk.Label(window, text="Result：")
answer_label.pack()

# Create a Frame to placing Copy and Clear button
button_frame = tk.Frame(window)

#Add copy button
copy_button = tk.Button(button_frame, text="Copy", command=copy_answer)
copy_button.pack(side=tk.LEFT, padx=30)

#Add clear text button
clear_button = tk.Button(button_frame, text="Clear", command=clear_text)
clear_button.pack(side=tk.RIGHT, padx=30)

# makes button_frame added to the main window
button_frame.pack(pady=30)

# Make the Tkinter Window is keeping looping unless program is closed
window.mainloop()