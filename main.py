from telegram.ext import Application, CommandHandler, Updater
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import threading
import os


BOT_TOKEN = os.environ.get("track_bot_token")


def track_item(link):
    details = {}
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)
    driver.get("https://pricehistory.app/")
    element = wait.until(EC.visibility_of_element_located((By.ID, "search")))
    driver.find_element(By.ID, "search").send_keys(link)
    driver.find_element(By.ID, "search-submit").click()
    try:
        element = wait.until(
            EC.visibility_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "body > div > div:nth-child(6) > div.col-12.px-0.py-2.all-time-price-overview.small > div",
                )
            )
        )
    except TimeoutException:
        try:
            element = wait.until(
                EC.visibility_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "#search-message > div",
                    )
                )
            )
            if element.text == "":
                return "Invalid Link!!! \n \nPlease provide a link to a product from websites like Amazon, Flipkart, etc. If the problem persists, please report it to username.praveen.email@gmail.com."
            else:
                return "Failed to fetch! This product maybe new or try again after some time!"
        except:
            return "Invalid Link!!! \n \nPlease provide a link to a product from websites like Amazon, Flipkart, etc. If the problem persists, please report it to username.praveen.email@gmail.com."
        return "Invalid Link!!! \n \nPlease provide a link to a product from websites like Amazon, Flipkart, etc. If the problem persists, please report it to username.praveen.email@gmail.com."
    container = driver.find_elements(
        By.CSS_SELECTOR,
        "body > div > div:nth-child(6) > div.col-12.px-0.py-2.all-time-price-overview.small > div > div",
    )
    for item in container:
        divs = item.find_elements(By.TAG_NAME, "span")
        details[divs[0].text] = divs[1].text
    current_price = driver.find_element(
        By.CSS_SELECTOR,
        "body > div > div:nth-child(6) > div.col-md-12.col-lg-5.col-xl-4.ph-pricing.mt-2.mb-2.border.shadow-sm.p-2.bg-light > div.ph-pricing-pricing",
    ).text
    details["Current Price: "] = current_price
    driver.close()
    return details


def run_in_thread(function, link):

    class ResultHolder:
        def __init__(self):
            self.result = None

    result_holder = ResultHolder()

    def wrapper():
        result_holder.result = function(link)

    thread = threading.Thread(target=wrapper)
    thread.start()
    thread.join()  # Wait for the thread to finish

    return result_holder.result


def formatter(dic):
    if isinstance(dic, dict):
        result = "Price Tracking of your item is :- \n"
        for key, value in dic.items():
            result += f"{key} {value} \n"
        return result
    else:
        return dic


async def help(update, context):
    text = "Hello, this is a bot that tracks the prices of products on e-commerce websites. You can track the price of items from websites like Amazon, Flipkart, etc. To track the price of an item, just type /track followed by the link to the product. Thanks for checking out this bot! Created By - username.praveen.email@gmail.com"
    await update.message.reply_text(text)


async def track(update, context):
    item_link = str(update.message.text).replace("/track", "").strip()
    if item_link == "":
        await update.message.reply_text(
            r"Please provide a link after /track. Example:- /track {link}"
        )
        return
    result = run_in_thread(track_item, item_link)
    await update.message.reply_text(str(formatter(result)))


async def error(update, context):
    print(f"Update {update} caused error:- {context.error}")


def main():
    updater = Updater(BOT_TOKEN, True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("help", help))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    print("Staringt bot....")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("track", track))
    app.add_error_handler(error)

    print("Starting Polling...")
    app.run_polling(poll_interval=3)
