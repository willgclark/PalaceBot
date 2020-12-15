import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import requests
from difflib import SequenceMatcher
from requests_html import HTMLSession
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from tkinter import *
from tkinter import ttk
from tkinter import messagebox as mb
import tkinter as tk
import imp

class supreme_bot:
    
    def __init__(self):
        self.option = webdriver.ChromeOptions()
        # self.option.add_argument('--disable-blink-features=AutomationControlled')
        # self.option.add_argument('start-maximized')
        # self.option.add_experimental_option("excludeSwitches", ["enable-automation"])
        # self.option.add_experimental_option('useAutomationExtension', False)
        # agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x32) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
        # self.option.add_argument(f"user-agent={agent}")
        ###
        self.base_url = 'https://www.supremenewyork.com/'
        self.new_items_url = f'{self.base_url}/shop/new'
        self.desired_item = 'box logo'
        self.desired_item_colour = None
        self.desired_item_size = None
        self.basket = []
        self.item_urls = []
        self.size_list = ['Small', 'Medium', 'Large', 'XLarge']
        self.product_found = False
        self.session = HTMLSession()
        self.timeout = time.time() + (60 * 5) #5 = 5 minute timeout
        
        f = open('config.txt')
        self.config = imp.load_source('data', '', f)
        f.close()
        
    def add_product_to_basket(self):
        response = self.session.get(self.new_items_url)
        products = response.html.find('.inner-article')
        for product in products:
            product_url = product.find('a', first=True).attrs['href']
            response = self.session.get(f"{self.base_url}{product_url}")
            product_name = response.html.find('h1[itemprop=name]', first=True).text
            colour = response.html.find('p[itemprop=model]', first=True).text
            if self.desired_item.lower() in product_name.lower() and self.desired_item_colour.lower() in colour.lower():
                self.basket.append(f"{self.base_url}{product_url}")
                self.product_found = True
                break
                
    def execute_bot_buffer(self):
        if len(self.desired_item_colour.get('1.0', END)) == 1 or len(self.desired_item.get('1.0', END)) == 1 or self.desired_item_size.get() == "":
            mb.showwarning('Error', "Please enter values for item, size and colour.")
        else:
            self.desired_item_colour = self.desired_item_colour.get('1.0', END) .strip()
            self.desired_item = self.desired_item.get('1.0', END) .strip()
            self.desired_item_size = self.desired_item_size.get().strip()
            self.execute_bot()
        
    def execute_bot(self):
        self.driver = webdriver.Chrome(executable_path="chromedriver.exe", chrome_options=self.option)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        while not self.product_found and time.time() < self.timeout:
            self.add_product_to_basket()
         
        if not self.product_found:
            mb.showwarning('Timeout', "Product not found. Bot timed out.")
        else:
            self.driver.get(self.basket[0])

            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//select[@name='size']/option[text()='{self.desired_item_size}']"))).click()
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='add to basket']"))).click()
            time.sleep(.3)
            self.driver.get(f'{self.base_url}/checkout')

            self.driver.find_element_by_id('order_billing_name').send_keys(self.config.NAME)
            self.driver.find_element_by_id('order_email').send_keys(self.config.EMAIL)
            self.driver.find_element_by_id('order_tel').send_keys(self.config.PHONE)

            self.driver.find_element_by_id('bo').send_keys(self.config.ADDRESS)
            self.driver.find_element_by_id('oba3').send_keys(self.config.ADDRESS_2)
            self.driver.find_element_by_id('order_billing_address_3').send_keys(self.config.ADDRESS_3)
            self.driver.find_element_by_id('order_billing_zip').send_keys(self.config.POSTCODE)

            self.driver.find_element_by_id('order_billing_city').send_keys(self.config.CITY)

            self.driver.find_element_by_id('cnb').send_keys(self.config.CARD_NO)
            self.driver.find_element_by_xpath(f"//select[@id='credit_card_month']/option[text()={self.config.EXPIRY_MONTH}]").click()
            self.driver.find_element_by_xpath(f"//select[@id='credit_card_year']/option[text()={self.config.EXPIRY_YEAR}]").click()
            self.driver.find_element_by_id('vval').send_keys(self.config.SECURITY_CODE)

            self.driver.find_elements_by_tag_name('ins')[1].click()
            self.driver.find_element_by_xpath("//input[@type='submit' and @value='process payment']").click()
            
    def create_gui(self):
        window = Tk()
        window.configure(background='#FFEFDB')
        window.title("BogoCop 1.0")
        window.geometry("300x175")
        text = Label(window, bg='#FFEFDB', font=('courier', 12, 'bold'), text="BogoCop 1.0")
        text.pack()
                
        #Item Selection
        item_selection = Label(window, bg='#FFEFDB', text='Select an ITEM:')
        item_selection.place(x=0, y=42)
        self.desired_item = Text(window, height=1, width=10)
        self.desired_item.place(x=100, y=42)

        #Size Selection
        size_selection = Label(window, bg='#FFEFDB', text='Select a SIZE:')
        size_selection.place(x=0, y=72)
        self.desired_item_size = ttk.Combobox(window, values=self.size_list, width = 15)
        self.desired_item_size.place(x=100, y=72)
        
        #Colour Selection
        colour_prompt = Label(window, bg='#FFEFDB', text='Enter a Colour:')
        colour_prompt.place(x=0, y=102)
        self.desired_item_colour=Text(window, height=1, width=10)
        self.desired_item_colour.place(x=100, y=102)
        
        #Submit
        cop_button = Button(window, text="COP", command=self.execute_bot_buffer)
        cop_button.config(height=2, width=40)
        cop_button.place(x=5, y=130)
        window.mainloop()

if __name__ == "__main__":
    sb = supreme_bot()
    sb.create_gui()