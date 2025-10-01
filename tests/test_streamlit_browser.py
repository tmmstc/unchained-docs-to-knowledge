"""
Tests for Streamlit app browser integration using Selenium.
Note: This module requires Selenium and assumes Microsoft Edge is installed.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


@pytest.fixture
def browser():
    edge_options = Options()
    edge_options.add_argument("--headless=new")
    edge_options.add_argument("--no-sandbox")
    edge_options.add_argument("--disable-dev-shm-usage")
    edge_options.add_argument("--disable-gpu")

    driver = webdriver.Edge(options=edge_options)
    driver.set_page_load_timeout(30)
    yield driver
    driver.quit()


@pytest.mark.skip(
    reason="Requires Streamlit app to be running on localhost:8501"
)
def test_streamlit_app_loads(browser):
    browser.get("http://localhost:8501")
    wait = WebDriverWait(browser, 10)
    wait.until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    assert "streamlit" in browser.page_source.lower()


@pytest.mark.skip(
    reason="Requires Streamlit app to be running on localhost:8501"
)
def test_streamlit_app_title(browser):
    browser.get("http://localhost:8501")
    wait = WebDriverWait(browser, 10)
    wait.until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    time.sleep(2)
    assert browser.title or "streamlit" in browser.page_source.lower()


def test_browser_can_launch(browser):
    browser.get("https://example.com")
    assert "Example Domain" in browser.page_source
