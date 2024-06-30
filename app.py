import traceback

from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, StaleElementReferenceException
from time import sleep
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from flask import Flask, render_template, request
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import undetected_chromedriver as uc

# service = Service(executable_path='chromedriver.exe')

def askGPT(requirements, skills, question, driver, actions, ind):
    # driver.switch_to.window(new_tab)
    # prompt = driver.find_element(By.ID, 'prompt-textarea')
    try:
        prompt = search_element(driver, 3, By.ID, "prompt-textarea", "chatgpt prompt textarea", False)
        actions.key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT).perform()
        actions.perform()
        prompt.send_keys(requirements)
        actions.key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT).perform()
        actions.perform()
        skills = ' '.join(skills)
        prompt.send_keys('skills required: '+skills)
        actions.key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT).perform()
        actions.perform()
        s = 'Answer the question on behalf of me in about 80 words: ' + question
        prompt.send_keys(s)
        sleep(2)
        prompt.send_keys(Keys.ENTER)
        sleep(8)
        answer = search_element(driver, 3, By.CLASS_NAME, "markdown", "Chatgpt-Answer", True)
        return answer[len(answer) - 1].text
    except Exception as e:
        traceback.print_exc()
        return None

def openChatGPT(driver):
    driver.get("https://chatgpt.com")
    sleep(5)
    try:
        # stayloggedout = driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div/div/div/a')
        stayloggedout = search_element(driver, 3, By.XPATH, '/html/body/div[3]/div/div/div/div/div/a', 'chatgpt stay logged out', False)
        if stayloggedout is not None:
            stayloggedout.click()
    except NoSuchElementException as e:
        print('stay logged out - Element not found')
    sleep(1)
    # driver.switch_to.window(old_tab)

def setupUCDriver():
    op = Options()
    op.add_argument(f"user-agent={UserAgent.random}")
    op.add_argument("user-data-dir=./")
    op.add_experimental_option("detach", True)
    op.add_experimental_option("excludeSwitches", ["enable-logging"])
    # driver = uc.Chrome(chrome_options=op)
    driver = uc.Chrome(service=Service(ChromeDriverManager().install()), chrome_options=op, version_main=125)
    driver.maximize_window()
    return driver

# driver.get("https://facebook.com")
# sleep(2)
# old_tab = driver.current_window_handle


# def askGPT(requirements, skills, question, driver, new_tab, actions):
#     driver.switch_to.window(new_tab)
#     prompt = driver.find_element(By.ID, 'prompt-textarea')
#     prompt.send_keys(requirements)
#     actions.key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT).perform()
#     actions.perform()
#     prompt.send_keys('skills required '+(' '.join(skills)))
#     actions.key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT).perform()
#     actions.perform()
#     s = 'Answer the question on behalf of me in about 100 words \n '+question
#     prompt.send_keys(s)
#     prompt.send_keys(Keys.ENTER)

# def openChatGPT(driver, old_tab):
#     driver.execute_script("window.open();")
#
#     # Switch to the new tab
#     new_tab = driver.window_handles[1]
#     driver.switch_to.window(new_tab)
#
#     # Do some work in the new tab
#     driver.get("https://chatgpt.com")
#     sleep(5)
#     stayloggedout = driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div/div/div/a')
#     stayloggedout.click()
#     sleep(1)
#     driver.switch_to.window(old_tab)
#     return new_tab

def login(driver):
    try:
        username = driver.find_element(By.NAME, "email")
        password = driver.find_element(By.NAME, "password")
        username.clear()
        password.clear()
        username.send_keys("chunduriabhi@gmail.com")
        password.send_keys("abhishek453")
    except NoSuchElementException:
        print('No input fields for email and password found')

    confirm_btn = search_element(driver, 3, By.XPATH, '//*[@id="login_submit"]', 'Login Button', False)
    confirm_btn.click()


def apply(username, password, limit, profile, location, wfh):
    # chrome_options = Options()
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    driver.get("https://internshala.com/login/user")
    sleep(3)
    ucdriver = setupUCDriver()
    try:
        login(driver)
        sleep(2)
        driver.get("https://internshala.com/internships")
        sleep(2)

        if wfh: url = 'https://internshala.com/internships/'+'work-from-home-'+profile+'-internships-in-'+location
        else: url = 'https://internshala.com/internships/' + profile + '-internships-in-' + location
        driver.get(url)
        sleep(4)

        try:
            # Scraping internships
            # internships = driver.find_elements(By.CLASS_NAME, "individual_internship")
            # internships = internships[:4]
            # print(len(internships))
            # old_tab = driver.current_window_handle
            openChatGPT(ucdriver)
            sleep(4)
            # actions = ActionChains(driver)

            # for ind, e in enumerate(internships):
            inumber = 1
            applied = 0
            page = 1
            internshipsApplied = []
            while applied < int(limit):
                internships = driver.find_elements(By.CLASS_NAME, "individual_internship")
                if len(internships) <= 2:
                    break
                if inumber >= len(internships):
                    page = page + 1
                    inumber = 1
                    driver.get(url+'/page-'+str(page))
                    internships = driver.find_elements(By.CLASS_NAME, "individual_internship")
                    if len(internships) <= 1:
                        break
                e = internships[inumber]
                # if ind == 0:
                # continue
                try:
                    e.click()
                    sleep(1)
                    internshipName = search_element(driver, 3, By.ID, 'easy_apply_profile', 'Internship name', False)
                    companyName = search_element(driver, 3, By.ID, 'easy_apply_company', 'Company name', False)
                    requirements = search_element(driver, 3, By.CSS_SELECTOR, '.text-container', 'Job Requirements', False)
                    skills = search_element(driver, 3, By.CLASS_NAME, 'round_tabs', 'Required Skills', True)
                    continue_btn = search_element(driver, 3, By.ID, 'continue_button', 'Continue button', False)

                    if skills is not None: skills = [s.text for s in skills]
                    if companyName is not None: print(companyName.text)
                    if requirements is not None: print(requirements.text)
                    if skills is not None: print(skills)
                    continue_btn.click()
                    print('continue button clicked...')
                    sleep(1)

                    question = search_element(driver, 3, By.CLASS_NAME, 'assessment_question', 'cover_letter', True)
                    actions = ActionChains(ucdriver)
                    if question is None:
                        inumber = inumber + 1
                    else:
                        print('no of assessment questions: ' + str(len(question)))
                        if len(question) > 1:
                            inumber = inumber + 1
                            closeDialog(driver)
                            continue
                        answer = askGPT(requirements.text, skills, question[0].text, ucdriver, actions, 1)
                        if answer is None:
                            continue
                        print(answer)

                        coverletter_textarea = search_element(driver, 3, By.ID, 'cover_letter', "cover letter textarea",
                                                              False)
                        if coverletter_textarea is None: continue
                        driver.execute_script('arguments[0].style.display = "inline";', coverletter_textarea)
                        sleep(5)
                        coverletter_textarea.click()
                        coverletter_textarea.send_keys(answer)
                        sleep(5)
                        print('cover letter input entered...')
                    relocate = search_element(driver, 3, By.XPATH,
                                              '/html/body/div[1]/div[21]/div/div/div[2]/div[2]/div[2]/div[2]/form/div/div[2]/div[3]/div/div[2]/div[2]/div/label',
                                              'relocate checkbox', False)
                    if relocate is not None:
                        relocate.click()
                        sleep(1)
                    submit = search_element(driver, 3, By.ID, 'submit', 'submit button', False)
                    submit.click()
                    applied = applied + 1
                    internshipsApplied.append('Internship Name: '+internshipName.text+' | Company Name: '+companyName.text)
                    sleep(5)
                    driver.get(url+'/page-'+str(page))
                    sleep(5)

                    # closeDialog(driver)

                    print('=======================================================')
                except Exception as error:
                    traceback.print_exc()
                    print('hello error how are you?')
        except NoSuchElementException as e:
            print('Element not found')
            traceback.print_exc()

        print(internshipsApplied)

        return internshipsApplied
    except Exception as e:
        traceback.print_exc()
        return internshipsApplied
    finally:
        driver.get("https://internshala.com/logout")
        driver.quit()
        ucdriver.quit()

def search_element(driver, time, mode, path, name, multiple):
    try:
        if multiple:
            element = WebDriverWait(driver, time).until(
                EC.presence_of_all_elements_located((mode, path))
            )
            return element
        else:
            element = WebDriverWait(driver, time).until(
                EC.presence_of_element_located((mode, path))
            )
            return element
    except Exception as e:
        print('****** '+name+' ******')
        print(e)
        return None

def closeDialog(driver):
    close_btn = search_element(driver, 3, By.ID, 'easy_apply_modal_close', 'Close button', False)

    close_btn.click()
    print('close button clicked...')
    sleep(1)

    confirm_btn = search_element(driver, 3, By.ID, 'easy_apply_modal_close_confirm_exit', 'Confirm Exit button', False)

    confirm_btn.click()
    print('confirm close clicked...')
    sleep(2)

app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'GET':
        return render_template('input.html')
    if request.method == 'POST':
        applied = apply(request.form['email'], request.form['password'], request.form['limit'], request.form['profile'], request.form['location'], request.form.get('wfh'))
        if len(applied) <= 0:
            return 'No internships available. Try again'
        else:
            return render_template('result.html', result_list=applied)


if __name__ == '__main__':
    app.run()
