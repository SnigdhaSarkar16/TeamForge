import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


@pytest.mark.e2e
def test_team_generation_flow():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,1000")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get("http://127.0.0.1:8000")

        # Wait briefly for the frontend to load hackathons.
        time.sleep(1)

        hackathon_select = driver.find_element(
            By.ID,
            "hackathon-select",
        )

        options = hackathon_select.find_elements(
            By.TAG_NAME,
            "option",
        )

        assert len(options) > 1

        # Select the existing hackathon #3.
        for option in options:
            if option.get_attribute("value") == "3":
                option.click()
                break

        time.sleep(1)

        student_count = driver.find_element(
            By.ID,
            "student-count",
        )

        assert int(student_count.get_attribute("value")) > 0

        generate_button = driver.find_element(
            By.ID,
            "generate-teams",
        )

        generate_button.click()

        time.sleep(2)

        teams = driver.find_elements(
            By.CLASS_NAME,
            "team-card",
        )

        assert len(teams) > 0

        coverage = driver.find_element(
            By.ID,
            "stat-coverage",
        )

        assert "%" in coverage.text

    finally:
        driver.quit()