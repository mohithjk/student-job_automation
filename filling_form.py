import selenium 
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless=new")  # run without UI (new mode for Chrome 109+)
chrome_options.add_argument("--no-sandbox")    # required in some server environments
chrome_options.add_argument("--disable-dev-shm-usage")  

# Load Excel file
df = pd.read_excel("student_data.xlsx")  # You can also specify sheet_name="Sheet1" if needed

# Save as CSV
df.to_csv("student_data.csv", index=False)
# Read the CSV file
df = pd.read_csv("student_data.csv")

# Iterate over rows
for index, row in df.iterrows():
    name = row['Name']         
    email = row['Email']  
    Job_Description=row["Job Description"]
    gender = row["Gender"].strip().lower()  

    driver=webdriver.Chrome()
    driver.maximize_window()
    driver.get("https://docs.google.com/forms/d/e/1FAIpQLSeIW5eSx9aDf9dUfwjP4HD8YliQ-VrrphljgHLXZKNTdpp4KQ/viewform?pli=1")
    input_field = driver.find_elements(By.XPATH, '//input[@jsname="YPqjbf"]')
    time.sleep(2)
    input_field[0].send_keys(f"{name}")

    input_field[1].send_keys(f"{email}")
    
    time.sleep(2)

       # Gender selection logic
    if gender == "male":
        driver.find_element(By.ID, "i24").click()
    elif gender == "female":
        driver.find_element(By.ID, "i19").click()
    time.sleep(2)

    # submit = driver.find_element(By.XPATH, '//input[@jsname="ksKsZd"]')
    # submit.click()
    # time.sleep(2)
    next_button = driver.find_element(By.XPATH, '//span[text()="Next"]/ancestor::div[@role="button"]')
    next_button.click()
    time.sleep(3)
    # input_field = driver.find_elements(By.XPATH, '//input[@jsname="YPqjbf"]')
    # input_field[2].send_keys("Your Answer Here")
    # time.sleep(2)


    wait = WebDriverWait(driver, 10)
    textarea = wait.until(EC.presence_of_element_located((By.XPATH, '//textarea[@jsname="YPqjbf"]')))
    textarea.send_keys(f"{Job_Description}")
    time.sleep(2) 


    time.sleep(2)
    male=driver.find_element(By.ID,"i24")
    male.click()
    time.sleep(2)


    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    # Wait until the Submit button is present
    submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//span[text()="Submit"]/ancestor::div[@role="button"]'))
    )

    # Click the Submit button
    submit_button.click()

    # f



    print("registered successfully")
    driver.close()





    # # Load Excel file
    # df = pd.read_excel("student_data.xlsx")  # You can also specify sheet_name="Sheet1" if needed

    # # Save as CSV
    # df.to_csv("student_data.csv", index=False)
    # # Read the CSV file
    # df = pd.read_csv("student_data.csv")

    # # Iterate over rows
    # for index, row in df.iterrows():
    #     name = row['Name']         # Replace 'Name' with your actual column name
    #     email = row['Email']  


    # # driver.close()