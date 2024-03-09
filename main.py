from fastapi import FastAPI
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from chromedriver_py import binary_path
from time import sleep
import json, random


with open('numbers.json', 'r') as file:
    my_numbers = json.load(file)


mynumber = 'Your_Whatsap_Number_for_login_check'


######## message
f = open("messages.txt", "r", encoding="utf8")
messages = f.read().split("\n")
f.close()

def selenium_options():
    svc = Service(executable_path=binary_path)
    driver = webdriver.Chrome(service=svc)
    # driver = webdriver.Firefox()
    return driver


def get_element(driver, time, element_type, element):
    clickable_obj = WebDriverWait(driver, time).until(EC.element_to_be_clickable((element_type, element)))
    clickable_obj.click()
    sleep(1)


def check_login(driver):
    print("Check login Step")
    first_message_url = 'https://web.whatsapp.com/send?phone=' + mynumber + '&text=Artıq başlaya bilərik ;)'
    sent = False
    for i in range(3):
        if not sent:
            driver.get(first_message_url)
            try:                                                                                           
                                                                                               ######## send button xpath
                WebDriverWait(driver, 120).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[2]/button/span')))
            except Exception as err:
                print(f"{i}/3 attemp not sended. \nError: {err}")
            else:
                sleep(2)
                sent=True
                print(f"{i}/3 OK")
                return first_message_url


def check_and_get_story_elements(driver):
    ###for business
    # get_element(driver, 30, By.XPATH, '//*[@id="app"]/div/div[2]/div[3]/header/div[2]/div/span/div[3]/div')
    ###for normal whatsapp
    get_element(driver, 30, By.XPATH, '//*[@id="app"]/div/div[2]/div[3]/header/div[2]/div/span/div[2]/div')
    #### open my story
    get_element(driver, 30, By.XPATH, '//*[@id="app"]/div/div[2]/div[2]/div[1]/span/div/span/div/div/div/div[1]/div[1]/div/div/div/div/div')
    #### open my story views
    get_element(driver, 30, By.XPATH, '//*[@id="app"]/div/span[3]/div/div/div/span/div/div/div/div/div[6]/div/button/span')
    print("story elements OK")


def get_elements_set(driver):
    elements_set = set({})
    while True:
        try:
            modal = driver.find_element(By.CSS_SELECTOR, "#app > div > span:nth-child(3) > div > div > div")
            sleep(2)
            elements = modal.find_elements(By.CLASS_NAME, '_8nE1Y')
            if elements:
                # print("elements")
                break
        except:
            continue
    for element in elements:
        elements_set.add(element.text.split("\n")[0])
        sleep(0.5)
    return elements_set


def create_new_viewer_list(elements_set):
    for number_key in my_numbers.keys():
        if number_key in elements_set and number_key not in send_list:
            new_list.append(number_key)



def send_sms(driver, number, name):
    random_message = random.choice(messages).replace("{ad}",name)
    print("send sms >> ", name)
    message_url = 'https://web.whatsapp.com/send?phone=' + number + '&text='+random_message
    sent = False
    for i in range(3):
        if not sent:
            driver.get(message_url)
            try:                                                                                           
                send_button = WebDriverWait(driver, 120).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[2]/button/span')))
                sleep(2)
                if send_button:
                    send_button.click()
                    sleep(2)
                    sent=True
                    print(f"{i}/3 {name} Sended")
                    return True
            except Exception as err:
                print(f"{i}/3 attemp not sended. \nError: {err}")


def send_message_new_list(driver):
    for new in new_list:
        response = send_sms(driver, my_numbers[new], new)
        if response:
            send_list.append(new)
            new_list.remove(new)
    all = True if len(new_list) == 0 else False
    return all

    
app = FastAPI()	


send_list = []
new_list = []

@app.post("/check-and-send-message")
def check_and_send_message():
    driver = selenium_options()
    driver.get('https://web.whatsapp.com')
    try:
        first_sms = check_login(driver)
        while True:
            if first_sms:
                if len(new_list) == 0:
                    check_and_get_story_elements(driver)
                    elements_set = get_elements_set(driver)
                    create_new_viewer_list(elements_set)
                print("new_list >> ",new_list)
                send_message_new_list(driver)
                print("elements: ", elements_set)
                print("send_list >> ",send_list)
            sleep(2)
    except Exception as err:
        driver.quit()
        return {'error':err}

