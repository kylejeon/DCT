import streamlit as st
import psycopg2
import pandas as pd
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# PostgreSQL 설정
@st.experimental_singleton
def init_conection():
    return psycopg2.connect(**st.secrets["postgres"])
    
conn = init_conection()

@st.experimental_memo(ttl=660)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

# Side menu
with st.sidebar:
    st.write("TEST")

# 브라우저 설정
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(options=options)
baseUrl = 'https://hogangnono.com/'
driver.get(baseUrl)

# 팝업창 닫기
WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div/div[1]/div[2]/div[2]/h2")))
if driver.find_element(By.XPATH, "/html/body/div[2]/div/div[1]/div[2]/div[2]/h2").get_property("textContent") == "호갱노노의 강력한 기능을무료로 사용해보세요.":
    driver.find_element(By.XPATH, "/html/body/div[2]/div/div[1]/div[2]/div[2]/a[2]").click()