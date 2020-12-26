from selenium.webdriver import Chrome, Firefox
from pages.sign_in_page import SignInPage
from pages.result_page import ResultPage
from pages.product_page import ProductPage
from pages.cart_page import CartPage
from smtplib import SMTP
from src import config
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import csv
import os


def get_grocery_list():
    curr_path = os.path.dirname(os.path.realpath(__file__))
    grocery_list_path = os.path.join(curr_path, 'src', 'grocery_list.csv')

    rows = []
    dataFile = open(grocery_list_path, "r")
    reader = csv.reader(dataFile)
    next(reader)

    for row in reader:
        rows.append(row)
    return rows


def open_browser(browser="chrome", wait_time=10):
    if browser == 'chrome':
        driver = Chrome()
    elif browser == 'firefox':
        driver = Firefox()
    else:
        raise Exception(f"Unsupported browser: {browser}")
    BASE_URL = 'https://www.walmart.com'
    driver.maximize_window()
    driver.get(BASE_URL)
    driver.implicitly_wait(wait_time)
    return driver


def close_browser(driver):
    driver.quit()


def send_mail():
    msg = MIMEMultipart()
    msg['Subject'] = 'Your Items are waiting in Your Cart'

    text = 'Your items are waiting in your cart. \n' \
           'Log in to complete your order: https://www.walmart.com/account/login'
    msg.attach(MIMEText(text))

    root = os.path.dirname(os.path.abspath(__file__))
    screenshot_path = os.path.join(root, "screenshots", "cart_screenshot.png")
    with open(screenshot_path, "rb") as f:
        part = MIMEApplication(
            f.read(),
            Name=os.path.basename(screenshot_path)
        )
    part['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(screenshot_path)
    msg.attach(part)
    server = SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(config.EMAIL, config.PASSWORD)
    server.sendmail(config.EMAIL, config.EMAIL, msg.as_string())
    server.close()


def main():
    driver = open_browser()
    sign_in = SignInPage(driver)
    res = ResultPage(driver)
    cart = CartPage(driver)
    product_page = ProductPage(driver)

    sign_in.goto()
    sign_in.sign_in(config.EMAIL, config.PASSWORD)
    cart.goto()
    cart.clear_cart()
    grocery_list = get_grocery_list()

    for line in grocery_list:
        name, quantity, max_price = line
        sign_in.search(name)
        r = res.choose_product(max_price)
        if r:
            product_page.add_to_cart(quantity)

    cart.goto()
    sign_in.take_screenshot()
    close_browser(driver)
    send_mail()


if __name__ == '__main__':
    main()