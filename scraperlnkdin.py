from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time

# Шлях до chromedriver
chromedriver_path = '/usr/bin/chromedriver'

# Створення екземпляру браузера
options = webdriver.ChromeOptions()
options.binary_location = "/usr/bin/google-chrome-stable"
options.add_argument(f"webdriver.chrome.driver={chromedriver_path}")
driver = webdriver.Chrome(options=options)

# Перехід на сторінку входу в LinkedIn
driver.get("https://www.linkedin.com/login")

# Автоматичне введення облікових даних для входу в акаунт
email_input = driver.find_element(By.ID, 'username')
email_input.send_keys("xxx@xxxxxxxx")
password_input = driver.find_element(By.ID, 'password')
password_input.send_keys("xxxxxxxxxxxxxxxxxxxxxxxx")
login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
login_button.click()

# Очікування завантаження сторінки LinkedIn
WebDriverWait(driver, 10).until(EC.title_contains("LinkedIn"))

# Перехід на сторінку з дописами LinkedIn вказаного користувача
driver.get("https://www.linkedin.com/in/cybermolfar/recent-activity/all/")

# Автоматичне прокручування сторінки
def scroll_to_bottom():
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # Зачекайте, поки loader не зникне
    WebDriverWait(driver, 10).until_not(EC.visibility_of_element_located((By.XPATH, '//div[@class="artdeco-loader"]')))
    # Почекайте, поки не завантажаться нові дописи
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "feed-shared-update-v2")]')))

# Початкова кількість дописів перед спробою прокрутки
initial_post_count = len(driver.find_elements(By.XPATH, '//div[contains(@class, "feed-shared-update-v2")]'))

# Лічильник помилок при спробах прокрутки
error_count = 0

# Таймаут для завершення прокрутки після виявлення, що нові дописи не завантажуються
timeout = 100  # Можете задати свій бажаний таймаут

# Прокрутка сторінки для завантаження нових дописів
while True:
    try:
        scroll_to_bottom()
        current_post_count = len(driver.find_elements(By.XPATH, '//div[contains(@class, "feed-shared-update-v2")]'))
        if current_post_count == initial_post_count:
            error_count += 1
            if error_count > 2:
                break  # Якщо не завантажено нових дописів протягом кількох спроб, вийти з циклу
        else:
            initial_post_count = current_post_count
            error_count = 0  # Скидання лічильника помилок при кожному новому дописі

            # Пройдемося по кожному допису та скопіюємо посилання
            posts = driver.find_elements(By.XPATH, '//div[contains(@class, "feed-shared-update-v2")]')
            for post in posts:
                # Знаходимо елемент меню керування для кожного допису
                control_menu = post.find_element(By.XPATH, './/div[contains(@class, "feed-shared-update-v2__control-menu")]')

                # Спробуємо клікнути на меню керування за допомогою ActionChains
                ActionChains(driver).move_to_element(control_menu).click().perform()

                # Зачекати, щоб меню з'явилося (опційно, ви можете адаптувати таймаут)
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, './/div[contains(@class, "feed-shared-update-v2__control-menu")]')))

                # Знаходимо кнопку "Copy link to post"
                copy_link_button = post.find_element(By.XPATH, './/button[contains(@aria-label, "Copy link to post")]')

                # Спробуємо клікнути на кнопку "Copy link to post" за допомогою ActionChains
                ActionChains(driver).move_to_element(copy_link_button).click().perform()

                # Зачекати, щоб меню зникло (опційно, ви можете адаптувати таймаут)
                WebDriverWait(driver, 5).until_not(EC.presence_of_element_located((By.XPATH, './/div[contains(@class, "feed-shared-update-v2__control-menu")]')))

    except Exception as e:
        pass  # Продовжити спроби прокрутки навіть у разі помилок

# Отримати HTML сторінки з дописами
html_content = driver.page_source

# Зберегти HTML у файл
with open("linkedin_posts.html", "w", encoding="utf-8") as file:
    file.write(html_content)

# Закриття браузера після завершення
driver.quit()
