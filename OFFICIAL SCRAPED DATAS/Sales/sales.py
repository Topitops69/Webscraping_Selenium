import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, WebDriverException

import time

url = 'https://www.mynimo.com/cebu/sales-marketing-retail-jobs'

# Default Values:
default_job_id = 'N/A'
default_job_title = 'N/A'
default_salary = 'N/A'
default_experience = 'N/A'
default_company = 'N/A'
default_details = 'N/A'
default_address = 'N/A'
default_employees = 'N/A'
default_date = 'N/A'
default_link_elem = 'N/A'

try:
    # Set up the web driver using Chrome
    driver = webdriver.Chrome()

    driver.get(url)
    # Wait for the job listings to be visible
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, '//a[@class="href-button css-h9szfi"]')))

    total_pages = 8  # You may need to update this value based on the actual total number of pages

    # Open the CSV file for writing
    with open('Job_data_cebu.csv', mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'Job Title', 'Salary', 'Experience', 'Company', 'Details', 'Address', 'Employees', 'Date', 'Link'])

        for page_number in range(1, total_pages + 1):
            if page_number > 8:
                break  # Exit the loop if the page number is greater than 8

            print(f"Scraping page {page_number}...")
            # Find all job listings on the current page
            jobs = driver.find_elements(By.XPATH, '//a[@class="href-button css-h9szfi"]')

            for job in jobs:
                try:
                    # Find the job title element within each job listing
                    title_element = job.find_element(By.XPATH, './/p[@class="href-button css-qkcbob"]')
                    job_title = title_element.text if title_element else default_job_title

                    salary_elements = job.find_elements(By.XPATH, './/p[@class="css-1yqpud"]')
                    salary = salary_elements[0].text if salary_elements else default_salary

                    experience_element = job.find_elements(By.XPATH, './/h6[@class="badge-name-text"]')
                    experience = experience_element[0].text if experience_element else default_experience

                    company_elem = job.find_element(By.XPATH, './/h5[@class="company-name-text"]')
                    company = company_elem.text if company_elem else default_company

                    emp_elem = job.find_elements(By.XPATH, './/p[@class="css-1ht1cys"]')
                    employees = emp_elem[2].text if len(emp_elem) >= 3 else default_employees

                    link_elem = job.get_attribute('href')

                    # Click on the link to navigate to the job details page
                    driver.execute_script("arguments[0].click();", job)
                    try:
                        # Wait for the overlay/popup to disappear
                        WebDriverWait(driver, 60).until(EC.invisibility_of_element_located((By.XPATH, '//div[@role="alert"]')))
                        # Switch to the new tab/window
                        # driver.switch_to.window(driver.window_handles[1])

                        # Wait for the job details page to load completely
                        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, './/div[@class="css-1lz7cfx"]')))

                        # Code for scraping job_details
                        job_details_element = driver.find_element(By.XPATH, '//div[@class="html-box"]')
                        job_details_items = job_details_element.find_elements(By.XPATH, './/ul/li')
                        details_list = [item.text.strip() for item in job_details_items]
                        details = "\n".join(details_list)

                        address_elem = driver.find_element(By.XPATH, './/h6[@class="css-17y5fzp"]')
                        address = address_elem.text if address_elem else default_address

                        date_elem = driver.find_element(By.XPATH, './/h5[@class="tw-text-gray-600 tw-text-sm"]')
                        date = date_elem.text if date_elem else default_date

                        id_elem = driver.find_elements(By.XPATH, './/h5[@class="tw-text-gray-600 tw-text-sm"]')
                        job_id = id_elem[1].text if id_elem else default_job_id

                    except WebDriverException as e:
                        # Handle the disconnected exception
                        print("An error occurred:", e)
                        print("WebDriver lost connection. Trying to recover...")
                        driver.refresh()
                        # Wait for the job details page to load completely
                        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, './/div[@class="css-1lz7cfx"]')))
                        continue

                    except Exception as e:
                        print("An error occurred:", e)
                        print(f"Error while scraping {job_title} at page: {page_number}...")
                        driver.refresh()
                        # Wait for the job details page to load completely
                        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, './/div[@class="css-1lz7cfx"]')))
                        continue

                    print("ID:", job_id,
                          " || Job title:", job_title,
                          " || Salary:", salary,
                          " || Experience: ", experience,
                          " || Company:", company,
                          " || Details:", details,
                          " || Address:", address,
                          " || Employees:", employees,
                          " || Date:", date,
                          " || Link:", link_elem)

                    time.sleep(1)
                    # Write the data to the CSV file
                    writer.writerow([job_id, job_title, salary, experience, company, details, address, employees, date, link_elem])
                    # Go back to the original page with the list of jobs
                    driver.back()
                    # Wait for the job listings to be visible on the new page
                    time.sleep(3)

                except (StaleElementReferenceException, WebDriverException) as e:
                    # If the element becomes stale or WebDriverException occurs, catch the exception and continue to the next iteration
                    print("Element became stale or WebDriverException occurred. Skipping to the next job...")
                    continue

            if page_number < total_pages:
                # Find all page buttons
                page_buttons = driver.find_elements(By.XPATH, '//a[@class="href-button css-1ok8g35"]')

                # Click on the next page button
                for button in page_buttons:
                    if int(button.text) == page_number + 1:
                        button.click()
                        break

                # Wait for the job listings to be visible on the new page
                WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, '//a[@class="href-button css-h9szfi"]')))

            time.sleep(3)

except Exception as e:
    print("An error occurred:", e)
    print(f"Error while scraping {job_title} at page {page_number}...")

finally:
    # Quit the driver after finishing the task
    driver.quit()
