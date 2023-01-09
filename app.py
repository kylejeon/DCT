import streamlit as st
import psycopg2

# Postgre DB 접속
connection = psycopg2.connect(
    host='146.56.169.113',
    database = 'dct',
    user = 'yhjeon',
    password ='Cloud1q2w#$'
)
cursor = connection.cursor()
# cursor.execute("create table test (USER_ID SERIAL PRIMARY KEY, 	USERNAME VARCHAR(50) UNIQUE NOT NULL, 	PASSWORD VARCHAR(50) NOT NULL,	EMAIL VARCHAR(355) UNIQUE NOT NULL,	CREATED_ON TIMESTAMP NOT NULL,	LAST_LOGIN TIMESTAMP)")
# connection.commit()

# data =[100,200,300,400]

# st.bar_chart(data)

modality = cursor.execute("select modality from job group by modality")
reporter = cursor.execute("select requester_name from job group by requester_name")

st.header("Job Type")
job_type = st.selectbox('Select a job type',("Requested Job","Completed Job","Scheduled Job","Emergency Job"))
criteria = st.radio('Select a criteria',("All","Day","Week","Month"))
value_type = st.radio('Select a value type',("Count","Ratio(%)","Count/Ratio"))
filter = st.radio('Select a filter',("None","Hospital","Modality","Reporter"))
filter_hospital = st.selectbox("A병원","B병원","C병원")
filter_modality = st.selectbox(modality)
filter_reporter = st.selectbox(reporter)
