import os
import tkinter as tk
import tkinter.font as tkFont
import openai
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By

options = webdriver.ChromeOptions()
driver = webdriver.Chrome()
driver.get('https://desk.oneforma.com/')

# Initialize Tkinter Window
window = tk.Tk()
window.title("Translator based on OpenAI")

FONT = tkFont.Font(size=12)  # 默认大小为12

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


# Create a label and text box for OpenAI API Key
api_key_label = tk.Label(window, text="Enter OpenAI API Key：")
api_key_var = tk.StringVar()
api_key_entry = tk.Entry(window, show="*", width=50, textvariable=api_key_var)

# Read the text file to get OpenAI API Key

if os.path.isfile("apikey.txt"):
    with open("apikey.txt", "r") as f:
        api_key = f.read().strip()
    
    # If the api key is read and not empty, set the api key to variable
    if api_key:
        api_key_var.set(api_key)

api_key_label.pack()
api_key_entry.pack()

def run_translation(event):
    translate()
    copy_answer()
    clear_text()

# Create a label for text need to translate
question_label = tk.Label(window, text="Please enter text need to translate：")
question_entry = tk.Entry(window, width=50)
question_entry.bind("<Return>", run_translation)
question_label.pack()
question_entry.pack()


def clear_text():
    question_entry.delete(0, tk.END)
    
def translate():
    # get the language that user entered
    language = language_var_origin.get()
    
    #get the text user want to translate
    question = question_entry.get()
    
    #get api key from the variable
    api_key = api_key_entry.get()
    
    if(question == "") :
        return

    # set OpenAI API Key
    openai.api_key = api_key

    # calling OpenAI API to translate the word, and passing the data that required to translate    
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": f"You are a translator to translate {language} to {language_var_translate.get()}. Translate the following question with don't capitalize the first letter and don't add a full stop at the end. And you only need to show word that translated"},
        {"role": "user", "content": f"{question}"},
    ]
)
    
    # get tranlated data from the response
    reply = response.choices[0].message.content.strip()
    answer = reply.replace(".", "")
    answer = answer[0].lower() + answer[1:]

    # display the result answer to UI
    answer_label.config(text=f"Result：{answer}")
    
    if 'https://desk.oneforma.com/' in driver.current_url:
        #driver.find_element(By.TAG_NAME, "textarea").find_element(By.ID,"caption-text").send_keys(answer)
        htmlData = driver.page_source
        print(driver.current_url)
        print(f"Contain element: {'True' if 'caption-text' in htmlData else 'False'}")
        print("executed")


def copy_answer():
    answer = answer_label.cget("text")[7:]
    pyperclip.copy(answer)
    clear_text()

# Add a button to translate
translate_button = tk.Button(window, text="Translate", command=translate,font=FONT)
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