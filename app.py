import streamlit as st
import psycopg2
import pandas as pd
import numpy as np

@st.experimental_singleton
def init_conection():
    return psycopg2.connect(**st.secrets["postgres"])
    # Postgre DB 접속
    # connection = psycopg2.connect(
    #     host='146.56.169.113',
    #     database = 'dct',
    #     # user = 'yhjeon',
    #     # password ='Cloud1q2w#$'
    #     user = st.secrets["db_username"],
    #     password = st.secrets["db_password"]
    
conn = init_conection()
# data =[100,200,300,400]
# st.bar_chart(data)

@st.experimental_memo(ttl=660)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

hospital_data = run_query("select institution_code from job group by institution_code;")
hospital = []
for i in range(len(hospital_data)):
    hospital.append(hospital_data[i][0])
modality_data = run_query("select modality from job group by modality;")
modality = []
for i in range(len(modality_data)):
    modality.append(modality_data[i][0])
reporter_data = run_query("select request_name from job group by request_name;")
reporter = []
for i in range(len(reporter_data)):
    if reporter_data[i][0] != "":
        reporter.append(reporter_data[i][0])

with st.sidebar:
    if st.button("Clear"):
        st.session_state.main_job_type = "Request Job"
        st.session_state.job_type = "Requested Job"
        st.session_state.criteria = "All"
        st.session_state.value_type = "Count"
        st.session_state.filter = "None"
        st.session_state.group = "None"
        st.session_state.indicator = "None"

    st.title("LiveMeter Simulation")
    main_job_type = st.selectbox('**Main Job Type**',("Request Job","Complete Job","Cancel Job"), help='Select a main job type', key ='main_job_type')
    if main_job_type == "Request Job":
        job_type = st.radio('**Job Type**',("Requested Job","Emergency Job"), horizontal=True, key='job_type')
    elif main_job_type == "Complete Job":
        job_type = st.radio('**Job Type**',("Completed Job","Emergency Job"), horizontal=True, key='job_type')
    elif main_job_type == "Cancel Job":
        job_type = st.radio('**Job Type**',("Emergency Job","Not Emergency Job"), horizontal=True, key='job_type')
    criteria = st.radio('**Criteria**',("All","Day","Week","Month"), horizontal=True, key='criteria')
    value_type = st.radio('**Value Type**',("Count","Ratio(%)","Count/Ratio(%)"), horizontal=True, key='value_type')
    filter = st.radio('**Filter**',("None","Hospital","Modality","Reporter"), horizontal=True, key='filter')
    if filter == "Hospital":
        filter_hospital = st.selectbox('select a hospital',("A병원","B병원","C병원"))
    elif filter == "Modality":
        filter_modality = st.selectbox('select a modality',(modality))
    elif filter == "Reporter":
        filter_reporter = st.selectbox('select a reporter',(reporter))

    group = st.radio('**Compare with**',("None","Hospital","Modality","Reporter"), horizontal=True, key='group')
    if main_job_type == "Request Job":
        indicator = st.radio('**Add indicator**', ("None","Completed Job"), horizontal=True, key='indicator')
    elif main_job_type == "Complete Job":
        indicator = st.radio('**Add indicator**', ("None","Requested Job"), horizontal=True, key='indicator')
    elif main_job_type == "Cancel Job":
        indicator = st.radio('**Add indicator**', ("None","Requested Job","Completed Job"), horizontal=True, key='indicator')

with st.container():
    st.markdown("## Quiz!")
    st.text("Q1. 최근 1달의 판독 의뢰 건수를 표시하세요.")
    st.text("Q2. 병원별 판독 완료 건수를 표시하세요.")
    st.text("Q3. Reporter 별 CR 장비의 응급 의뢰 건수를 표시하세요.")
    st.text("Q4. 최근 1달의 병원별 판독 의뢰율을 표시하세요.")
    st.text("Q5. Modality 별 최근 1달의 판독 의뢰 건수와 판독 완료 건수를 함께 표시하세요.")
    st.text("Q6. Cancel 된 의뢰 중에서 일반 의뢰 건수를 표시하세요.")
    st.text("Q7. Modality 별로 Cancel 된 의뢰 중에서 응급 의뢰 건수를 표시하세요.")


st.write("--------------------------------------------------------------------------------")
with st.container():
    if group == "None":
        if main_job_type == "Request Job" and job_type == "Requested Job":
            if criteria == "All":
                requested_job_cnt = run_query("select count(*) from job where job_stat = '200';")
                total = run_query("select count(*) from job;")
                try:               
                    ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)
                except ZeroDivisionError:
                    ratio = 0
                if value_type == "Count":
                    if filter == "None":
                        st.metric(label="Reuqested Job Count",value=requested_job_cnt[0][0])
                    elif filter == "Hospital" and filter_hospital in hospital:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and institution_code='"+ filter_hospital +"';")                    
                        st.metric(label="Reuqested Job Count",value=requested_job_cnt[0][0])               
                    elif filter == "Modality" and filter_modality in modality:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and modality='" + filter_modality + "';")                    
                        st.metric(label="Reuqested Job Count",value=requested_job_cnt[0][0])
                    elif filter == "Reporter" and filter_reporter in reporter:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and request_name='" + filter_reporter + "';")                    
                        st.metric(label="Reuqested Job Count",value=requested_job_cnt[0][0])
                elif value_type == "Ratio(%)":
                    if filter == "None":
                        st.metric(label="Reuqested Job Ratio(%)",value=str(ratio)+"%")
                    elif filter == "Hospital" and filter_hospital in hospital:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and institution_code='"+ filter_hospital +"';")
                        ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)
                        st.metric(label="Reuqested Job Ratio(%)",value=str(ratio)+"%")               
                    elif filter == "Modality" and filter_modality in modality:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and modality='" + filter_modality + "';") 
                        ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)                   
                        st.metric(label="Reuqested Job Ratio(%)",value=str(ratio)+"%")
                    elif filter == "Reporter" and filter_reporter in modality:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and request_name='" + filter_reporter + "';") 
                        ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)                   
                        st.metric(label="Reuqested Job Ratio(%)",value=str(ratio)+"%")
                else:
                    if filter == "None":
                        st.metric(label="Reuqested Job Count/Ratio(%)",value=str(requested_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Hospital" and filter_hospital in hospital:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and institution_code='"+ filter_hospital +"';")
                        ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)
                        st.metric(label="Reuqested Job Count/Ratio(%)",value=str(requested_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Modality" and filter_modality in modality:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and modality='" + filter_modality + "';") 
                        ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)                   
                        st.metric(label="Reuqested Job Count/Ratio(%)",value=str(requested_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Reporter" and filter_reporter in modality:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and request_name='" + filter_reporter + "';") 
                        ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)                   
                        st.metric(label="Reuqested Job Count/Ratio(%)",value=str(requested_job_cnt[0][0]) + "/" + str(ratio)+ "%")

            elif criteria == "Day":
                requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm =current_date;")
                total = run_query("select count(*) from job where job_dttm = current_date;")
                try:               
                    ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)
                except ZeroDivisionError:
                    ratio = 0
                if value_type == "Count":
                    if filter == "None":
                        prior = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '1 day' and current_date;")
                        delta = requested_job_cnt[0][0] - prior[0][0]
                        st.metric(label="Reuqested Job Count",value=requested_job_cnt[0][0], delta=delta)
                    elif filter == "Hospital" and filter_hospital in hospital:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm =current_date and institution_code='"+ filter_hospital +"';")
                        prior = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '1 day' and current_date;")
                        delta = requested_job_cnt[0][0] - prior[0][0]
                        st.metric(label="Reuqested Job Count",value=requested_job_cnt[0][0], delta=delta)               
                    elif filter == "Modality" and filter_modality in modality:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm =current_date and modality='" + filter_modality + "';")                    
                        prior = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '1 day' and current_date;")
                        delta = requested_job_cnt[0][0] - prior[0][0]
                        st.metric(label="Reuqested Job Count",value=requested_job_cnt[0][0], delta=delta)
                    elif filter == "Reporter" and filter_reporter in reporter:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm =current_date and request_name='" + filter_reporter + "';")                    
                        prior = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '1 day' and current_date;")
                        delta = requested_job_cnt[0][0] - prior[0][0]
                        st.metric(label="Reuqested Job Count",value=requested_job_cnt[0][0], delta=delta)
                elif value_type == "Ratio(%)":
                    if filter == "None":
                        prior = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '2 day' and current_date - interval '1 day';")
                        total = run_query("select count(*) from job where job_dttm between current_date - interval '2 day' and current_date - interval '1 day';")
                        try:               
                            ratio2 = round((prior[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio2 = 0
                        delta = round((ratio - ratio2),1)
                        st.metric(label="Reuqested Job Ratio(%)",value=str(ratio)+"%", delta=str(delta)+"%")
                    elif filter == "Hospital" and filter_hospital in hospital:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm =current_date and institution_code='"+ filter_hospital +"';")
                        prior = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '2 day' and current_date - interval '1 day' and institution_code='"+ filter_hospital +"';")
                        total = run_query("select count(*) from job where job_dttm between current_date - interval '2 day' and current_date - interval '1 day';")
                        try:               
                            ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)
                            ratio2 = round((prior[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0
                            ratio2 = 0
                        delta = round((ratio - ratio2),1)
                        st.metric(label="Reuqested Job Ratio(%)",value=str(ratio)+"%", delta=str(delta)+"%")               
                    elif filter == "Modality" and filter_modality in modality:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm =current_date and modality='" + filter_modality + "';") 
                        prior = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '2 day' and current_date - interval '1 day' and modality='"+ filter_modality +"';")
                        total = run_query("select count(*) from job where job_dttm between current_date - interval '2 day' and current_date - interval '1 day';")
                        try:               
                            ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)
                            ratio2 = round((prior[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0  
                            ratio2 = 0            
                        delta = round((ratio - ratio2),1)
                        st.metric(label="Reuqested Job Ratio(%)",value=str(ratio)+"%", delta=str(delta)+"%")
                    elif filter == "Reporter" and filter_reporter in modality:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm =current_date and request_name='" + filter_reporter + "';") 
                        prior = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '2 day' and current_date - interval '1 day' and request_name='"+ filter_reporter +"';")
                        total = run_query("select count(*) from job where job_dttm between current_date - interval '2 day' and current_date - interval '1 day';")
                        try:               
                            ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)
                            ratio2 = round((prior[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0 
                            ratio2 = 0                 
                        delta = round((ratio - ratio2),1)
                        st.metric(label="Reuqested Job Ratio(%)",value=str(ratio)+"%", delta=str(delta)+"%")
                else:
                    if filter == "None":
                        st.metric(label="Reuqested Job Count/Ratio(%)",value=str(requested_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Hospital" and filter_hospital in hospital:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm =current_date and institution_code='"+ filter_hospital +"';")
                        try:               
                            ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0
                        st.metric(label="Reuqested Job Count/Ratio(%)",value=str(requested_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Modality" and filter_modality in modality:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm =current_date and modality='" + filter_modality + "';") 
                        try:               
                            ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                  
                        st.metric(label="Reuqested Job Count/Ratio(%)",value=str(requested_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Reporter" and filter_reporter in modality:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm =current_date and request_name='" + filter_reporter + "';") 
                        try:               
                            ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                
                        st.metric(label="Reuqested Job Count/Ratio(%)",value=str(requested_job_cnt[0][0]) + "/" + str(ratio)+ "%")

            elif criteria == "Week":
                requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '1 week' and current_date;")
                total = run_query("select count(*) from job where job_dttm between current_date - interval '1 week' and current_date;")
                try:               
                    ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)
                except ZeroDivisionError:
                    ratio = 0
                if value_type == "Count":
                    if filter == "None":
                        prior = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '1 day' and current_date;")
                        delta = requested_job_cnt[0][0] - prior[0][0]
                        st.metric(label="Reuqested Job Count",value=requested_job_cnt[0][0], delta=delta)
                    elif filter == "Hospital" and filter_hospital in hospital:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '1 week' and current_date and institution_code='"+ filter_hospital +"';")
                        st.metric(label="Reuqested Job Count",value=requested_job_cnt[0][0], delta=delta)               
                    elif filter == "Modality" and filter_modality in modality:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '1 week' and current_date and modality='" + filter_modality + "';")                    
                        st.metric(label="Reuqested Job Count",value=requested_job_cnt[0][0], delta=delta)
                    elif filter == "Reporter" and filter_reporter in reporter:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '1 week' and current_date and request_name='" + filter_reporter + "';")                    
                        st.metric(label="Reuqested Job Count",value=requested_job_cnt[0][0], delta=delta)
                elif value_type == "Ratio(%)":
                    if filter == "None":
                        prior = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '2 week' and current_date - interval '1 week';")
                        total = run_query("select count(*) from job where job_dttm between current_date - interval '2 week' and current_date - interval '1 week';")
                        try:               
                            ratio2 = round((prior[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio2 = 0
                        delta = round((ratio - ratio2),1)
                        st.metric(label="Reuqested Job Ratio(%)",value=str(ratio)+"%", delta=str(delta)+"%")
                    elif filter == "Hospital" and filter_hospital in hospital:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '1 week' and current_date and institution_code='"+ filter_hospital +"';")
                        prior = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '2 week' and current_date - interval '1 week' and institution_code='"+ filter_hospital +"';")
                        total = run_query("select count(*) from job where job_dttm between current_date - interval '2 week' and current_date - interval '1 week' and institution_code='"+ filter_hospital +"';")
                        try:               
                            ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)
                            ratio2 = round((prior[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0
                        delta = round((ratio - ratio2),1)
                        st.metric(label="Reuqested Job Ratio(%)",value=str(ratio)+"%", delta=str(delta)+"%")               
                    elif filter == "Modality" and filter_modality in modality:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '1 week' and current_date and modality='" + filter_modality + "';")
                        prior = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '2 week' and current_date - interval '1 week' and modality='"+ filter_modality +"';")
                        total = run_query("select count(*) from job where job_dttm between current_date - interval '2 week' and current_date - interval '1 week' and modality='"+ filter_modality +"';") 
                        try:               
                            ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)
                            ratio2 = round((prior[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                 
                        delta = round((ratio - ratio2),1)
                        st.metric(label="Reuqested Job Ratio(%)",value=str(ratio)+"%", delta=str(delta)+"%")
                    elif filter == "Reporter" and filter_reporter in modality:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '1 week' and current_date and request_name='" + filter_reporter + "';") 
                        prior = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '2 week' and current_date - interval '1 week' and request_name='"+ filter_reporter +"';")
                        total = run_query("select count(*) from job where job_dttm between current_date - interval '2 week' and current_date - interval '1 week' and request_name='"+ filter_reporter +"';")
                        try:               
                            ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)
                            ratio2 = round((prior[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                 
                        delta = round((ratio - ratio2),1)
                        st.metric(label="Reuqested Job Ratio(%)",value=str(ratio)+"%", delta=str(delta)+"%")
                else:
                    if filter == "None":
                        st.metric(label="Reuqested Job Count/Ratio(%)",value=str(requested_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Hospital" and filter_hospital in hospital:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '1 week' and current_date and institution_code='"+ filter_hospital +"';")
                        try:               
                            ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0
                        st.metric(label="Reuqested Job Count/Ratio(%)",value=str(requested_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Modality" and filter_modality in modality:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '1 week' and current_date and modality='" + filter_modality + "';") 
                        try:               
                            ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                 
                        st.metric(label="Reuqested Job Count/Ratio(%)",value=str(requested_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Reporter" and filter_reporter in modality:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '1 week' and current_date and request_name='" + filter_reporter + "';") 
                        try:               
                            ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                  
                        st.metric(label="Reuqested Job Count/Ratio(%)",value=str(requested_job_cnt[0][0]) + "/" + str(ratio)+ "%")

            elif criteria == "Month":
                requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '1 month' and current_date;")
                total = run_query("select count(*) from job where job_dttm between current_date - interval '1 month' and current_date;")
                try:               
                    ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)
                except ZeroDivisionError:
                    ratio = 0
                if value_type == "Count":
                    if filter == "None":
                        prior = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '2 month' and current_date;")
                        delta = requested_job_cnt[0][0] - prior[0][0]
                        st.metric(label="Reuqested Job Count",value=requested_job_cnt[0][0], delta=delta)
                    elif filter == "Hospital" and filter_hospital in hospital:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '1 month' and current_date and institution_code='"+ filter_hospital +"';")
                        prior = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '2 month' and current_date - interval '1 month' and institution_code='"+ filter_hospital +"';")
                        delta = requested_job_cnt[0][0] - prior[0][0]
                        st.metric(label="Reuqested Job Count",value=requested_job_cnt[0][0], delta=delta)               
                    elif filter == "Modality" and filter_modality in modality:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '1 month' and current_date - interval '1 month' and modality='" + filter_modality + "';")                    
                        prior = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '2 month' and current_date and modality='" + filter_modality + "';")
                        delta = requested_job_cnt[0][0] - prior[0][0]
                        st.metric(label="Reuqested Job Count",value=requested_job_cnt[0][0], delta=delta)
                    elif filter == "Reporter" and filter_reporter in reporter:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '1 month' and current_date - interval '1 month' and request_name='" + filter_reporter + "';")                    
                        prior = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '2 month' and current_date and request_name='" + filter_reporter + "';")
                        delta = requested_job_cnt[0][0] - prior[0][0]
                        st.metric(label="Reuqested Job Count",value=requested_job_cnt[0][0], delta=delta)

                elif value_type == "Ratio(%)":
                    if filter == "None":
                        prior = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '2 month' and current_date - interval '1 month';")
                        total = run_query("select count(*) from job where job_dttm between current_date - interval '2 month' and current_date - interval '1 month';")
                        try:               
                            ratio2 = round((prior[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio2 = 0
                        delta = round((ratio - ratio2),1)
                        st.metric(label="Reuqested Job Ratio(%)",value=str(ratio)+"%", delta=str(delta)+"%")
                    elif filter == "Hospital" and filter_hospital in hospital:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '1 month' and current_date and institution_code='"+ filter_hospital +"';")
                        prior = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '2 month' and current_date - interval '1 month' and institution_code='" + filter_hospital + "';")
                        total = run_query("select count(*) from job where job_dttm between current_date - interval '2 month' and current_date - interval '1 month' and institution_code='" + filter_hospital + "';")
                        try:               
                            ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)
                            ratio2 = round((prior[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0
                            ratio2 = 0
                        delta = round((ratio - ratio2),1)
                        st.metric(label="Reuqested Job Ratio(%)",value=str(ratio)+"%", delta=str(delta)+"%")               
                    elif filter == "Modality" and filter_modality in modality:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '1 month' and current_date and modality='" + filter_modality + "';") 
                        prior = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '2 month' and current_date - interval '1 month' and modality='" + filter_modality + "';")
                        total = run_query("select count(*) from job where job_dttm between current_date - interval '2 month' and current_date - interval '1 month' and modality='" + filter_modality + "';")
                        try:               
                            ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)
                            ratio2 = round((prior[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0 
                            ratio2 = 0                 
                        delta = round((ratio - ratio2),1)
                        st.metric(label="Reuqested Job Ratio(%)",value=str(ratio)+"%", delta=str(delta)+"%")
                    elif filter == "Reporter" and filter_reporter in modality:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '1 month' and current_date and request_name='" + filter_reporter + "';") 
                        prior = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '2 month' and current_date - interval '1 month' and request_name='" + filter_reporter + "';")
                        total = run_query("select count(*) from job where job_dttm between current_date - interval '2 month' and current_date - interval '1 month' and request_name='" + filter_reporter + "';")
                        try:               
                            ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)
                            ratio2 = round((prior[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0 
                            ratio2 = 0               
                        delta = round((ratio - ratio2),1)
                        st.metric(label="Reuqested Job Ratio(%)",value=str(ratio)+"%", delta=str(delta)+"%")
                else:
                    if filter == "None":
                        st.metric(label="Reuqested Job Count/Ratio(%)",value=str(requested_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Hospital" and filter_hospital in hospital:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '1 month' and current_date and institution_code='"+ filter_hospital +"';")
                        try:               
                            ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0
                        st.metric(label="Reuqested Job Count/Ratio(%)",value=str(requested_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Modality" and filter_modality in modality:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '1 month' and current_date and modality='" + filter_modality + "';") 
                        try:               
                            ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                  
                        st.metric(label="Reuqested Job Count/Ratio(%)",value=str(requested_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Reporter" and filter_reporter in modality:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '1 month' and current_date and request_name='" + filter_reporter + "';") 
                        try:               
                            ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                  
                        st.metric(label="Reuqested Job Count/Ratio(%)",value=str(requested_job_cnt[0][0]) + "/" + str(ratio)+ "%")

        elif main_job_type == "Complete Job" and job_type == "Completed Job":
            if criteria == "All":
                completed_job_cnt = run_query("select count(*) from job where job_stat = '310';")
                total = run_query("select count(*) from job;")
                try:               
                    ratio = round((completed_job_cnt[0][0] * 100) / total[0][0],1)
                except ZeroDivisionError:
                    ratio = 0
                if value_type == "Count":
                    if filter == "None":
                        st.metric(label="Completed Job Count",value=completed_job_cnt[0][0])
                    elif filter == "Hospital" and filter_hospital in hospital:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and institution_code='"+ filter_hospital +"';")
                        st.metric(label="Completed Job Count",value=completed_job_cnt[0][0])               
                    elif filter == "Modality" and filter_modality in modality:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and modality='" + filter_modality + "';")                    
                        st.metric(label="Completed Job Count",value=completed_job_cnt[0][0])
                    elif filter == "Reporter" and filter_reporter in reporter:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and request_name='" + filter_reporter + "';")                    
                        st.metric(label="Completed Job Count",value=completed_job_cnt[0][0])
                elif value_type == "Ratio(%)":
                    if filter == "None":
                        st.metric(label="Completed Job Ratio(%)",value=str(ratio)+"%")
                    elif filter == "Hospital" and filter_hospital in hospital:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and institution_code='"+ filter_hospital +"';")
                        try:               
                            ratio = round((completed_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0
                        st.metric(label="Completed Job Ratio(%)",value=str(ratio)+"%")               
                    elif filter == "Modality" and filter_modality in modality:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and modality='" + filter_modality + "';") 
                        try:               
                            ratio = round((completed_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                  
                        st.metric(label="Completed Job Ratio(%)",value=str(ratio)+"%")
                    elif filter == "Reporter" and filter_reporter in modality:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and request_name='" + filter_reporter + "';") 
                        try:               
                            ratio = round((completed_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                 
                        st.metric(label="Completed Job Ratio(%)",value=str(ratio)+"%")
                else:
                    if filter == "None":
                        st.metric(label="Completed Job Count/Ratio(%)",value=str(completed_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Hospital" and filter_hospital in hospital:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and institution_code='"+ filter_hospital +"';")
                        try:               
                            ratio = round((completed_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0
                        st.metric(label="Completed Job Count/Ratio(%)",value=str(completed_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Modality" and filter_modality in modality:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and modality='" + filter_modality + "';") 
                        try:               
                            ratio = round((completed_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                  
                        st.metric(label="Completed Job Count/Ratio(%)",value=str(completed_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Reporter" and filter_reporter in modality:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and request_name='" + filter_reporter + "';") 
                        try:               
                            ratio = round((completed_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                 
                        st.metric(label="Completed Job Count/Ratio(%)",value=str(completed_job_cnt[0][0]) + "/" + str(ratio)+ "%")
                # if value_type == "Count":
                #     st.metric(label="Completed Job Count",value=completed_job_cnt[0][0])
                # elif value_type == "Ratio(%)":
                #     st.metric(label="Completed Job Ratio(%)",value=str(ratio)+"%")
                # else:
                #     st.metric(label="Completed Job Count/Ratio(%)",value=str(completed_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
            elif criteria == "Day":
                completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_dttm =current_date;")
                total = run_query("select count(*) from job where job_dttm =current_date;")
                try:               
                    ratio = round((completed_job_cnt[0][0] * 100) / total[0][0],1)
                except ZeroDivisionError:
                    ratio = 0
                if value_type == "Count":
                    if filter == "None":
                        st.metric(label="Completed Job Count",value=completed_job_cnt[0][0])
                    elif filter == "Hospital" and filter_hospital in hospital:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_dttm =current_date and institution_code='"+ filter_hospital +"';")
                        st.metric(label="Completed Job Count",value=completed_job_cnt[0][0])               
                    elif filter == "Modality" and filter_modality in modality:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_dttm =current_date and modality='" + filter_modality + "';")                    
                        st.metric(label="Completed Job Count",value=completed_job_cnt[0][0])
                    elif filter == "Reporter" and filter_reporter in reporter:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_dttm =current_date and request_name='" + filter_reporter + "';")                    
                        st.metric(label="Completed Job Count",value=completed_job_cnt[0][0])
                elif value_type == "Ratio(%)":
                    if filter == "None":
                        prior = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '2 day' and current_date - interval '1 day';")
                        total = run_query("select count(*) from job where job_dttm between current_date - interval '2 day' and current_date - interval '1 day';")
                        try:               
                            ratio2 = round((prior[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio2 = 0
                        delta = round((ratio - ratio2),1)
                        st.metric(label="Completed Job Ratio(%)",value=str(ratio)+"%", delta=str(delta)+"%")
                    elif filter == "Hospital" and filter_hospital in hospital:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_dttm =current_date and institution_code='"+ filter_hospital +"';")
                        prior = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '2 day' and current_date - interval '1 day' and institution_code='"+ filter_hospital +"';")
                        total = run_query("select count(*) from job where job_dttm between current_date - interval '2 day' and current_date - interval '1 day' and institution_code='"+ filter_hospital +"';")
                        try:               
                            ratio = round((completed_job_cnt[0][0] * 100) / total[0][0],1)
                            ratio2 = round((prior[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0
                            ratio2 = 0
                        delta = round((ratio - ratio2),1)
                        st.metric(label="Completed Job Ratio(%)",value=str(ratio)+"%", delta=str(delta)+"%")               
                    elif filter == "Modality" and filter_modality in modality:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_dttm =current_date and modality='" + filter_modality + "';") 
                        prior = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '2 day' and current_date - interval '1 day' and modality='" + filter_modality + "';")
                        total = run_query("select count(*) from job where job_dttm between current_date - interval '2 day' and current_date - interval '1 day' and modality='" + filter_modality + "';")
                        try:               
                            ratio = round((completed_job_cnt[0][0] * 100) / total[0][0],1)
                            ratio2 = round((prior[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0  
                            ratio2 = 0              
                        delta = round((ratio - ratio2),1)
                        st.metric(label="Completed Job Ratio(%)",value=str(ratio)+"%", delta=str(delta)+"%")
                    elif filter == "Reporter" and filter_reporter in modality:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_dttm =current_date and request_name='" + filter_reporter + "';") 
                        prior = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '2 day' and current_date - interval '1 day' and request_name='" + filter_reporter + "';")
                        total = run_query("select count(*) from job where job_dttm between current_date - interval '2 day' and current_date - interval '1 day' and request_name='" + filter_reporter + "';")
                        try:               
                            ratio = round((completed_job_cnt[0][0] * 100) / total[0][0],1)
                            ratio2 = round((prior[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0     
                            ratio2 = 0        
                        delta = round((ratio - ratio2),1)
                        st.metric(label="Completed Job Ratio(%)",value=str(ratio)+"%", delta=str(delta)+"%")
                else:
                    if filter == "None":
                        st.metric(label="Completed Job Count/Ratio(%)",value=str(completed_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Hospital" and filter_hospital in hospital:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_dttm =current_date and institution_code='"+ filter_hospital +"';")
                        try:               
                            ratio = round((completed_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0
                        st.metric(label="Completed Job Count/Ratio(%)",value=str(completed_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Modality" and filter_modality in modality:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_dttm =current_date and modality='" + filter_modality + "';") 
                        try:               
                            ratio = round((completed_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                 
                        st.metric(label="Completed Job Count/Ratio(%)",value=str(completed_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Reporter" and filter_reporter in modality:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_dttm =current_date and request_name='" + filter_reporter + "';") 
                        try:               
                            ratio = round((completed_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                 
                        st.metric(label="Completed Job Count/Ratio(%)",value=str(completed_job_cnt[0][0]) + "/" + str(ratio)+ "%")
                # if value_type == "Count":
                #     st.metric(label="Completed Job Count",value=completed_job_cnt[0][0])
                # elif value_type == "Ratio(%)":
                #     st.metric(label="Completed Job Ratio(%)",value=str(ratio)+"%")
                # else:
                #     st.metric(label="Completed Job Count/Ratio(%)",value=str(completed_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
            elif criteria == "Week":
                completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '1 week' and current_date;")
                total = run_query("select count(*) from job where job_dttm between current_date - interval '1 week' and current_date;")
                try:               
                    ratio = round((completed_job_cnt[0][0] * 100) / total[0][0],1)
                except ZeroDivisionError:
                    ratio = 0
                if value_type == "Count":
                    if filter == "None":
                        st.metric(label="Completed Job Count",value=completed_job_cnt[0][0])
                    elif filter == "Hospital" and filter_hospital in hospital:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '1 week' and current_date and institution_code='"+ filter_hospital +"';")
                        st.metric(label="Completed Job Count",value=completed_job_cnt[0][0])               
                    elif filter == "Modality" and filter_modality in modality:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '1 week' and current_date and modality='" + filter_modality + "';")                    
                        st.metric(label="Completed Job Count",value=completed_job_cnt[0][0])
                    elif filter == "Reporter" and filter_reporter in reporter:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '1 week' and current_date and request_name='" + filter_reporter + "';")                    
                        st.metric(label="Completed Job Count",value=completed_job_cnt[0][0])
                elif value_type == "Ratio(%)":
                    if filter == "None":
                        prior = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '2 week' and current_date - interval '1 week';")
                        total = run_query("select count(*) from job where job_dttm between current_date - interval '2 week' and current_date - interval '1 week';")
                        try:               
                            ratio2 = round((prior[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio2 = 0
                        delta = round((ratio - ratio2),1)
                        st.metric(label="Completed Job Ratio(%)",value=str(ratio)+"%", delta=str(delta)+"%")
                    elif filter == "Hospital" and filter_hospital in hospital:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '1 week' and current_date and institution_code='"+ filter_hospital +"';")
                        prior = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '2 week' and current_date - interval '1 week' and institution_code='"+ filter_hospital +"';")
                        total = run_query("select count(*) from job where job_dttm between current_date - interval '2 week' and current_date - interval '1 week' and institution_code='"+ filter_hospital +"';")
                        try:               
                            ratio = round((completed_job_cnt[0][0] * 100) / total[0][0],1)
                            ratio2 = round((prior[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0
                            ratio2 = 0
                        delta = round((ratio - ratio2),1)
                        st.metric(label="Completed Job Ratio(%)",value=str(ratio)+"%", delta=str(delta)+"%")               
                    elif filter == "Modality" and filter_modality in modality:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '1 week' and current_date and modality='" + filter_modality + "';") 
                        prior = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '2 week' and current_date - interval '1 week' and modality='" + filter_modality + "';")
                        total = run_query("select count(*) from job where job_dttm between current_date - interval '2 week' and current_date - interval '1 week' and modality='" + filter_modality + "';")
                        try:               
                            ratio = round((completed_job_cnt[0][0] * 100) / total[0][0],1)
                            ratio2 = round((prior[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0     
                            ratio2 = 0            
                        delta = round((ratio - ratio2),1)
                        st.metric(label="Completed Job Ratio(%)",value=str(ratio)+"%", delta=str(delta)+"%")
                    elif filter == "Reporter" and filter_reporter in modality:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '1 week' and current_date and request_name='" + filter_reporter + "';") 
                        prior = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '2 week' and current_date - interval '1 week' and request_name='" + filter_reporter + "';")
                        total = run_query("select count(*) from job where job_dttm between current_date - interval '2 week' and current_date - interval '1 week' and request_name='" + filter_reporter + "';")
                        try:               
                            ratio = round((completed_job_cnt[0][0] * 100) / total[0][0],1)
                            ratio2 = round((prior[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0     
                            ratio2 = 0             
                        delta = round((ratio - ratio2),1)
                        st.metric(label="Completed Job Ratio(%)",value=str(ratio)+"%", delta=str(delta)+"%")
                else:
                    if filter == "None":
                        st.metric(label="Completed Job Count/Ratio(%)",value=str(completed_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Hospital" and filter_hospital in hospital:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '1 week' and current_date and institution_code='"+ filter_hospital +"';")
                        try:               
                            ratio = round((completed_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0
                        st.metric(label="Completed Job Count/Ratio(%)",value=str(completed_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Modality" and filter_modality in modality:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '1 week' and current_date and modality='" + filter_modality + "';") 
                        try:               
                            ratio = round((completed_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                  
                        st.metric(label="Completed Job Count/Ratio(%)",value=str(completed_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Reporter" and filter_reporter in modality:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '1 week' and current_date and request_name='" + filter_reporter + "';") 
                        try:               
                            ratio = round((completed_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                  
                        st.metric(label="Completed Job Count/Ratio(%)",value=str(completed_job_cnt[0][0]) + "/" + str(ratio)+ "%")
                # if value_type == "Count":
                #     st.metric(label="Completed Job Count",value=completed_job_cnt[0][0])
                # elif value_type == "Ratio(%)":
                #     st.metric(label="Completed Job Ratio(%)",value=str(ratio)+"%")
                # else:
                #     st.metric(label="Completed Job Count/Ratio(%)",value=str(completed_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
            elif criteria == "Month":
                completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '1 month' and current_date;")
                total = run_query("select count(*) from job where job_dttm between current_date - interval '1 month' and current_date;")
                try:               
                    ratio = round((completed_job_cnt[0][0] * 100) / total[0][0],1)
                except ZeroDivisionError:
                    ratio = 0
                if value_type == "Count":
                    if filter == "None":
                        st.metric(label="Completed Job Count",value=completed_job_cnt[0][0])
                    elif filter == "Hospital" and filter_hospital in hospital:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '1 month' and current_date and institution_code='"+ filter_hospital +"';")
                        st.metric(label="Completed Job Count",value=completed_job_cnt[0][0])               
                    elif filter == "Modality" and filter_modality in modality:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '1 month' and current_date and modality='" + filter_modality + "';")                    
                        st.metric(label="Completed Job Count",value=completed_job_cnt[0][0])
                    elif filter == "Reporter" and filter_reporter in reporter:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '1 month' and current_date and request_name='" + filter_reporter + "';")                    
                        st.metric(label="Completed Job Count",value=completed_job_cnt[0][0])
                elif value_type == "Ratio(%)":
                    if filter == "None":
                        prior = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '2 month' and current_date - interval '1 month';")
                        total = run_query("select count(*) from job where job_dttm between current_date - interval '2 month' and current_date - interval '1 month';")
                        try:               
                            ratio2 = round((prior[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio2 = 0
                        delta = round((ratio - ratio2),1)
                        st.metric(label="Completed Job Ratio(%)",value=str(ratio)+"%", delta=str(delta)+"%")
                    elif filter == "Hospital" and filter_hospital in hospital:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '1 month' and current_date and institution_code='"+ filter_hospital +"';")
                        prior = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '2 month' and current_date - interval '1 month' and institution_code='"+ filter_hospital +"';")
                        total = run_query("select count(*) from job where job_dttm between current_date - interval '2 month' and current_date - interval '1 month' and institution_code='"+ filter_hospital +"';")
                        try:               
                            ratio = round((completed_job_cnt[0][0] * 100) / total[0][0],1)
                            ratio2 = round((prior[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0
                            ratio2 = 0
                        delta = round((ratio - ratio2),1)
                        st.metric(label="Completed Job Ratio(%)",value=str(ratio)+"%", delta=str(delta)+"%")               
                    elif filter == "Modality" and filter_modality in modality:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '1 month' and current_date and modality='" + filter_modality + "';") 
                        prior = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '2 month' and current_date - interval '1 month' and modality='"+ filter_modality +"';")
                        total = run_query("select count(*) from job where job_dttm between current_date - interval '2 month' and current_date - interval '1 month' and modality='"+ filter_modality +"';")
                        try:               
                            ratio = round((completed_job_cnt[0][0] * 100) / total[0][0],1)
                            ratio2 = round((prior[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0   
                            ratio2 = 0            
                        delta = round((ratio - ratio2),1)
                        st.metric(label="Completed Job Ratio(%)",value=str(ratio)+"%", delta=str(delta)+"%")
                    elif filter == "Reporter" and filter_reporter in modality:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '1 month' and current_date and request_name='" + filter_reporter + "';") 
                        prior = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '2 month' and current_date - interval '1 month' and request_name='"+ filter_reporter +"';")
                        total = run_query("select count(*) from job where job_dttm between current_date - interval '2 month' and current_date - interval '1 month' and request_name='"+ filter_reporter +"';")
                        try:               
                            ratio = round((completed_job_cnt[0][0] * 100) / total[0][0],1)
                            ratio2 = round((prior[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0 
                            ratio2 = 0                  
                        delta = round((ratio - ratio2),1)
                        st.metric(label="Completed Job Ratio(%)",value=str(ratio)+"%", delta=str(delta)+"%")
                else:
                    if filter == "None":
                        st.metric(label="Completed Job Count/Ratio(%)",value=str(completed_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Hospital" and filter_hospital in hospital:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '1 month' and current_date and institution_code='"+ filter_hospital +"';")
                        try:               
                            ratio = round((completed_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0
                        st.metric(label="Completed Job Count/Ratio(%)",value=str(completed_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Modality" and filter_modality in modality:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '1 month' and current_date and modality='" + filter_modality + "';") 
                        try:               
                            ratio = round((completed_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                   
                        st.metric(label="Completed Job Count/Ratio(%)",value=str(completed_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Reporter" and filter_reporter in modality:
                        completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '1 month' and current_date and request_name='" + filter_reporter + "';") 
                        try:               
                            ratio = round((completed_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                   
                        st.metric(label="Completed Job Count/Ratio(%)",value=str(completed_job_cnt[0][0]) + "/" + str(ratio)+ "%")
                # if value_type == "Count":
                #     st.metric(label="Completed Job Count",value=completed_job_cnt[0][0])
                # elif value_type == "Ratio(%)":
                #     st.metric(label="Completed Job Ratio(%)",value=str(ratio)+"%")
                # else:
                #     st.metric(label="Completed Job Count/Ratio(%)",value=str(completed_job_cnt[0][0]) + "/" + str(ratio)+ "%",)

        elif main_job_type == "Request Job" and job_type == "Emergency Job":
            if criteria == "All":
                emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E';")
                total = run_query("select count(*) from job where job_stat = '200';")
                try:               
                    ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                except ZeroDivisionError:
                    ratio = 0
                if value_type == "Count":
                    if filter == "None":
                        st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
                    elif filter == "Hospital" and filter_hospital in hospital:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and institution_code='"+ filter_hospital +"';")
                        st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])               
                    elif filter == "Modality" and filter_modality in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and modality='" + filter_modality + "';")                    
                        st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
                    elif filter == "Reporter" and filter_reporter in reporter:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and request_name='" + filter_reporter + "';")                    
                        st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
                elif value_type == "Ratio(%)":
                    if filter == "None":
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                    elif filter == "Hospital" and filter_hospital in hospital:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and institution_code='"+ filter_hospital +"';")
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")               
                    elif filter == "Modality" and filter_modality in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and modality='" + filter_modality + "';") 
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0      
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                    elif filter == "Reporter" and filter_reporter in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and request_name='" + filter_reporter + "';") 
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0               
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                else:
                    if filter == "None":
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Hospital" and filter_hospital in hospital:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and institution_code='"+ filter_hospital +"';")
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Modality" and filter_modality in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and modality='" + filter_modality + "';") 
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                   
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Reporter" and filter_reporter in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and request_name='" + filter_reporter + "';") 
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                  
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%")
                # if value_type == "Count":
                #     st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
                # elif value_type == "Ratio(%)":
                #     st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                # else:
                #     st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
            elif criteria == "Day":
                emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and job_dttm =current_date;")
                total = run_query("select count(*) from job where job_stat = '200' and job_dttm =current_date;")
                try:               
                    ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                except ZeroDivisionError:
                    ratio = 0
                if value_type == "Count":
                    if filter == "None":
                        st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
                    elif filter == "Hospital" and filter_hospital in hospital:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and job_dttm =current_date and institution_code='"+ filter_hospital +"';")
                        st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])               
                    elif filter == "Modality" and filter_modality in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and job_dttm =current_date and modality='" + filter_modality + "';")                    
                        st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
                    elif filter == "Reporter" and filter_reporter in reporter:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and job_dttm =current_date and request_name='" + filter_reporter + "';")                    
                        st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
                elif value_type == "Ratio(%)":
                    if filter == "None":
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                    elif filter == "Hospital" and filter_hospital in hospital:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and job_dttm =current_date and institution_code='"+ filter_hospital +"';")
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")               
                    elif filter == "Modality" and filter_modality in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and job_dttm =current_date and modality='" + filter_modality + "';") 
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                   
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                    elif filter == "Reporter" and filter_reporter in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and job_dttm =current_date and request_name='" + filter_reporter + "';") 
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                  
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                else:
                    if filter == "None":
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Hospital" and filter_hospital in hospital:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and job_dttm =current_date and institution_code='"+ filter_hospital +"';")
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Modality" and filter_modality in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and job_dttm =current_date and modality='" + filter_modality + "';") 
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                 
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Reporter" and filter_reporter in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and job_dttm =current_date and request_name='" + filter_reporter + "';") 
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                 
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%")
                # if value_type == "Count":
                #     st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
                # elif value_type == "Ratio(%)":
                #     st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                # else:
                #     st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
            elif criteria == "Week":
                emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and job_dttm between current_date - interval '1 week' and current_date;")
                total = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '1 week' and current_date;")
                try:               
                    ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                except ZeroDivisionError:
                    ratio = 0
                if value_type == "Count":
                    if filter == "None":
                        st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
                    elif filter == "Hospital" and filter_hospital in hospital:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and job_dttm between current_date - interval '1 week' and current_date and institution_code='"+ filter_hospital +"';")
                        st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])               
                    elif filter == "Modality" and filter_modality in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and job_dttm between current_date - interval '1 week' and current_date and modality='" + filter_modality + "';")                    
                        st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
                    elif filter == "Reporter" and filter_reporter in reporter:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and job_dttm between current_date - interval '1 week' and current_date and request_name='" + filter_reporter + "';")                    
                        st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
                elif value_type == "Ratio(%)":
                    if filter == "None":
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                    elif filter == "Hospital" and filter_hospital in hospital:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and job_dttm between current_date - interval '1 week' and current_date and institution_code='"+ filter_hospital +"';")
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")               
                    elif filter == "Modality" and filter_modality in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and job_dttm between current_date - interval '1 week' and current_date and modality='" + filter_modality + "';") 
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                   
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                    elif filter == "Reporter" and filter_reporter in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and job_dttm between current_date - interval '1 week' and current_date and request_name='" + filter_reporter + "';") 
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                   
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                else:
                    if filter == "None":
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Hospital" and filter_hospital in hospital:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and job_dttm between current_date - interval '1 week' and current_date and institution_code='"+ filter_hospital +"';")
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Modality" and filter_modality in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and job_dttm between current_date - interval '1 week' and current_date and modality='" + filter_modality + "';") 
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                 
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Reporter" and filter_reporter in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and job_dttm between current_date - interval '1 week' and current_date and request_name='" + filter_reporter + "';") 
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                 
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%")
                # if value_type == "Count":
                #     st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
                # elif value_type == "Ratio(%)":
                #     st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                # else:
                #     st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
            elif criteria == "Month":
                emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and job_dttm between current_date - interval '1 month' and current_date;")
                total = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '1 month' and current_date;")
                try:               
                    ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                except ZeroDivisionError:
                    ratio = 0
                if value_type == "Count":
                    if filter == "None":
                        st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
                    elif filter == "Hospital" and filter_hospital in hospital:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and job_dttm between current_date - interval '1 month' and current_date and institution_code='"+ filter_hospital +"';")
                        st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])               
                    elif filter == "Modality" and filter_modality in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and job_dttm between current_date - interval '1 month' and current_date and modality='" + filter_modality + "';")                    
                        st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
                    elif filter == "Reporter" and filter_reporter in reporter:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and job_dttm between current_date - interval '1 month' and current_date and request_name='" + filter_reporter + "';")                    
                        st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
                elif value_type == "Ratio(%)":
                    if filter == "None":
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                    elif filter == "Hospital" and filter_hospital in hospital:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and job_dttm between current_date - interval '1 month' and current_date and institution_code='"+ filter_hospital +"';")
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")               
                    elif filter == "Modality" and filter_modality in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and job_dttm between current_date - interval '1 month' and current_date and modality='" + filter_modality + "';") 
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                 
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                    elif filter == "Reporter" and filter_reporter in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and job_dttm between current_date - interval '1 month' and current_date and request_name='" + filter_reporter + "';") 
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                  
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                else:
                    if filter == "None":
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Hospital" and filter_hospital in hospital:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and job_dttm between current_date - interval '1 month' and current_date and institution_code='"+ filter_hospital +"';")
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Modality" and filter_modality in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and job_dttm between current_date - interval '1 month' and current_date and modality='" + filter_modality + "';") 
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                   
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Reporter" and filter_reporter in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and job_dttm between current_date - interval '1 month' and current_date and request_name='" + filter_reporter + "';") 
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                  
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%")
                # if value_type == "Count":
                #     st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
                # elif value_type == "Ratio(%)":
                #     st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                # else:
                #     st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
        elif main_job_type == "Complete Job" and job_type == "Emergency Job":
            if criteria == "All":
                emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E';")
                total = run_query("select count(*) from job where job_stat = '310';")
                try:               
                    ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                except ZeroDivisionError:
                    ratio = 0
                if value_type == "Count":
                    if filter == "None":
                        st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
                    elif filter == "Hospital" and filter_hospital in hospital:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and institution_code='"+ filter_hospital +"';")
                        st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])               
                    elif filter == "Modality" and filter_modality in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and modality='" + filter_modality + "';")                    
                        st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
                    elif filter == "Reporter" and filter_reporter in reporter:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and request_name='" + filter_reporter + "';")                    
                        st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
                elif value_type == "Ratio(%)":
                    if filter == "None":
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                    elif filter == "Hospital" and filter_hospital in hospital:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and institution_code='"+ filter_hospital +"';")
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")               
                    elif filter == "Modality" and filter_modality in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and modality='" + filter_modality + "';") 
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                 
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                    elif filter == "Reporter" and filter_reporter in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and request_name='" + filter_reporter + "';") 
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                   
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                else:
                    if filter == "None":
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Hospital" and filter_hospital in hospital:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and institution_code='"+ filter_hospital +"';")
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Modality" and filter_modality in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and modality='" + filter_modality + "';") 
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                  
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Reporter" and filter_reporter in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and request_name='" + filter_reporter + "';") 
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                  
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%")
                # if value_type == "Count":
                #     st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
                # elif value_type == "Ratio(%)":
                #     st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                # else:
                #     st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
            elif criteria == "Day":
                emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and job_dttm =current_date;")
                total = run_query("select count(*) from job where job_stat = '310' and job_dttm =current_date;")
                try:               
                    ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                except ZeroDivisionError:
                    ratio = 0
                if value_type == "Count":
                    if filter == "None":
                        st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
                    elif filter == "Hospital" and filter_hospital in hospital:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and job_dttm =current_date and institution_code='"+ filter_hospital +"';")
                        st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])               
                    elif filter == "Modality" and filter_modality in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and job_dttm =current_date and modality='" + filter_modality + "';")                    
                        st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
                    elif filter == "Reporter" and filter_reporter in reporter:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and job_dttm =current_date and request_name='" + filter_reporter + "';")                    
                        st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
                elif value_type == "Ratio(%)":
                    if filter == "None":
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                    elif filter == "Hospital" and filter_hospital in hospital:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and job_dttm =current_date and institution_code='"+ filter_hospital +"';")
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")               
                    elif filter == "Modality" and filter_modality in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and job_dttm =current_date and modality='" + filter_modality + "';") 
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                   
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                    elif filter == "Reporter" and filter_reporter in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and job_dttm =current_date and request_name='" + filter_reporter + "';") 
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0               
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                else:
                    if filter == "None":
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Hospital" and filter_hospital in hospital:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and job_dttm =current_date and institution_code='"+ filter_hospital +"';")
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Modality" and filter_modality in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and job_dttm =current_date and modality='" + filter_modality + "';") 
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Reporter" and filter_reporter in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and job_dttm =current_date and request_name='" + filter_reporter + "';") 
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                  
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%")
                # if value_type == "Count":
                #     st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
                # elif value_type == "Ratio(%)":
                #     st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                # else:
                #     st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
            elif criteria == "Week":
                emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and job_dttm between current_date - interval '1 week' and current_date;")
                total = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '1 week' and current_date;")
                try:               
                    ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                except ZeroDivisionError:
                    ratio = 0
                if value_type == "Count":
                    if filter == "None":
                        st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
                    elif filter == "Hospital" and filter_hospital in hospital:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and job_dttm between current_date - interval '1 week' and current_date and institution_code='"+ filter_hospital +"';")
                        st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])               
                    elif filter == "Modality" and filter_modality in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and job_dttm between current_date - interval '1 week' and current_date and modality='" + filter_modality + "';")                    
                        st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
                    elif filter == "Reporter" and filter_reporter in reporter:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and job_dttm between current_date - interval '1 week' and current_date and request_name='" + filter_reporter + "';")                    
                        st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
                elif value_type == "Ratio(%)":
                    if filter == "None":
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                    elif filter == "Hospital" and filter_hospital in hospital:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and job_dttm between current_date - interval '1 week' and current_date and institution_code='"+ filter_hospital +"';")
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")               
                    elif filter == "Modality" and filter_modality in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and job_dttm between current_date - interval '1 week' and current_date and modality='" + filter_modality + "';") 
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                  
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                    elif filter == "Reporter" and filter_reporter in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and job_dttm between current_date - interval '1 week' and current_date and request_name='" + filter_reporter + "';") 
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                   
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                else:
                    if filter == "None":
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Hospital" and filter_hospital in hospital:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and job_dttm between current_date - interval '1 week' and current_date and institution_code='"+ filter_hospital +"';")
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Modality" and filter_modality in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and job_dttm between current_date - interval '1 week' and current_date and modality='" + filter_modality + "';") 
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                   
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Reporter" and filter_reporter in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and job_dttm between current_date - interval '1 week' and current_date and request_name='" + filter_reporter + "';") 
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0      
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%")
                # if value_type == "Count":
                #     st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
                # elif value_type == "Ratio(%)":
                #     st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                # else:
                #     st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
            elif criteria == "Month":
                emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and job_dttm between current_date - interval '1 month' and current_date;")
                total = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '1 month' and current_date;")
                try:               
                    ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                except ZeroDivisionError:
                    ratio = 0
                if value_type == "Count":
                    if filter == "None":
                        st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
                    elif filter == "Hospital" and filter_hospital in hospital:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and job_dttm between current_date - interval '1 month' and current_date and institution_code='"+ filter_hospital +"';")
                        st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])               
                    elif filter == "Modality" and filter_modality in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and job_dttm between current_date - interval '1 month' and current_date and modality='" + filter_modality + "';")                    
                        st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
                    elif filter == "Reporter" and filter_reporter in reporter:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and job_dttm between current_date - interval '1 month' and current_date and request_name='" + filter_reporter + "';")                    
                        st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
                elif value_type == "Ratio(%)":
                    if filter == "None":
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                    elif filter == "Hospital" and filter_hospital in hospital:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and job_dttm between current_date - interval '1 month' and current_date and institution_code='"+ filter_hospital +"';")
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")               
                    elif filter == "Modality" and filter_modality in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and job_dttm between current_date - interval '1 month' and current_date and modality='" + filter_modality + "';") 
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                   
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                    elif filter == "Reporter" and filter_reporter in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and job_dttm between current_date - interval '1 month' and current_date and request_name='" + filter_reporter + "';") 
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                  
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                else:
                    if filter == "None":
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Hospital" and filter_hospital in hospital:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and job_dttm between current_date - interval '1 month' and current_date and institution_code='"+ filter_hospital +"';")
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Modality" and filter_modality in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and job_dttm between current_date - interval '1 month' and current_date and modality='" + filter_modality + "';") 
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0                  
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Reporter" and filter_reporter in modality:
                        emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and job_dttm between current_date - interval '1 month' and current_date and request_name='" + filter_reporter + "';") 
                        try:               
                            ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
                        except ZeroDivisionError:
                            ratio = 0         
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%")
                # if value_type == "Count":
                #     st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
                # elif value_type == "Ratio(%)":
                #     st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                # else:
                #     st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
        
        if main_job_type == "Cancel Job" and job_type == "Emergency Job":
            if criteria == "All":
                requested_job_cnt = run_query("select count(*) from job where job_stat = '100' and job_priority='E';")
                total = run_query("select count(*) from job where job_stat = '100';")
                try:               
                    ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)
                except ZeroDivisionError:
                    ratio = 0
                if value_type == "Count":
                    if filter == "None":
                        st.metric(label="Emergency Job Count",value=requested_job_cnt[0][0])
                    elif filter == "Hospital" and filter_hospital in hospital:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '100' and institution_code='"+ filter_hospital +"' and job_priority='E';")                    
                        st.metric(label="Emergency Job Count",value=requested_job_cnt[0][0])               
                    elif filter == "Modality" and filter_modality in modality:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '100' and modality='" + filter_modality + "' and job_priority='E';")                    
                        st.metric(label="Emergency Job Count",value=requested_job_cnt[0][0])
                    elif filter == "Reporter" and filter_reporter in reporter:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '100' and request_name='" + filter_reporter + "' and job_priority='E';")                    
                        st.metric(label="Emergency Job Count",value=requested_job_cnt[0][0])
                elif value_type == "Ratio(%)":
                    if filter == "None":
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                    elif filter == "Hospital" and filter_hospital in hospital:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '100' and institution_code='"+ filter_hospital +"' and job_priority='E';")
                        ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")               
                    elif filter == "Modality" and filter_modality in modality:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '100' and modality='" + filter_modality + "' and job_priority='E';") 
                        ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)                   
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                    elif filter == "Reporter" and filter_reporter in modality:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '100' and request_name='" + filter_reporter + "' and job_priority='E';") 
                        ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)                   
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                else:
                    if filter == "None":
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(requested_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Hospital" and filter_hospital in hospital:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '100' and institution_code='"+ filter_hospital +"' and job_priority='E';")
                        ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(requested_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Modality" and filter_modality in modality:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '100' and modality='" + filter_modality + "' and job_priority='E';") 
                        ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)                   
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(requested_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Reporter" and filter_reporter in modality:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '100' and request_name='" + filter_reporter + "' and job_priority='E';") 
                        ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)                   
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(requested_job_cnt[0][0]) + "/" + str(ratio)+ "%")

        if main_job_type == "Cancel Job" and job_type == "Not Emergency Job":
            if criteria == "All":
                requested_job_cnt = run_query("select count(*) from job where job_stat = '100' and job_priority = 'N';")
                total = run_query("select count(*) from job where job_priority = 'N';")
                try:               
                    ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)
                except ZeroDivisionError:
                    ratio = 0
                if value_type == "Count":
                    if filter == "None":
                        st.metric(label="Emergency Job Count",value=requested_job_cnt[0][0])
                    elif filter == "Hospital" and filter_hospital in hospital:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '100' and institution_code='"+ filter_hospital +"' and job_priority = 'N';")                    
                        st.metric(label="Emergency Job Count",value=requested_job_cnt[0][0])               
                    elif filter == "Modality" and filter_modality in modality:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '100' and modality='" + filter_modality + "' and job_priority = 'N';")                    
                        st.metric(label="Emergency Job Count",value=requested_job_cnt[0][0])
                    elif filter == "Reporter" and filter_reporter in reporter:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '100' and request_name='" + filter_reporter + "' and job_priority = 'N';")                    
                        st.metric(label="Emergency Job Count",value=requested_job_cnt[0][0])
                elif value_type == "Ratio(%)":
                    if filter == "None":
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                    elif filter == "Hospital" and filter_hospital in hospital:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '100' and institution_code='"+ filter_hospital +"' and job_priority = 'N';")
                        ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")               
                    elif filter == "Modality" and filter_modality in modality:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '100' and modality='" + filter_modality + "' and job_priority = 'N';") 
                        ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)                   
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                    elif filter == "Reporter" and filter_reporter in modality:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '100' and request_name='" + filter_reporter + "' and job_priority = 'N';") 
                        ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)                   
                        st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
                else:
                    if filter == "None":
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(requested_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Hospital" and filter_hospital in hospital:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '100' and institution_code='"+ filter_hospital +"' and job_priority = 'N';")
                        ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(requested_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Modality" and filter_modality in modality:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '100' and modality='" + filter_modality + "' and job_priority = 'N';") 
                        ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)                   
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(requested_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
                    elif filter == "Reporter" and filter_reporter in modality:
                        requested_job_cnt = run_query("select count(*) from job where job_stat = '100' and request_name='" + filter_reporter + "' and job_priority = 'N';") 
                        ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)                   
                        st.metric(label="Emergency Job Count/Ratio(%)",value=str(requested_job_cnt[0][0]) + "/" + str(ratio)+ "%")

    elif group == "Hospital":
        if criteria == "All":
            if job_type == "Requested Job":
                total = run_query("select count(*) from job where job_stat = '200';")
                requested_job_cnt = run_query("select count(*) from job where job_stat = '200';")
                hospital_data = run_query("select institution_code from job group by institution_code;")
                hospital = []
                for i in range(len(hospital_data)):
                    hospital.append(hospital_data[i][0])
                hospital_cnt = len(hospital)

                if filter == "None":
                    if indicator == "None":
                        name = []
                        data = []
                        for i in range(hospital_cnt): 
                            hospital = hospital_data[i][0]
                            name.append(hospital_data[i][0])
                            # if value_type == "Count":
                            value = run_query("select count(*) from job where institution_code ='" + hospital +"' and job_stat='200';")
                            data.append(value[0][0])
                            # elif value_type == "Ratio(%)":
                            #     value = run_query("select count(*) from job where institution_code ='" + hospital +"' and job_stat='200';")
                            #     ratio = str(round((value[0][0] * 100) / total[0][0],1))
                            #     data.append(ratio)

                        source = pd.DataFrame({
                            'ratio': data,
                            'hospital': name
                        }).set_index('hospital')
                        st.bar_chart(source)
                    elif indicator == "Completed Job":
                        name = []
                        data = []
                        indicator = []
                        for i in range(hospital_cnt): 
                            hospital = hospital_data[i][0]
                            name.append(hospital_data[i][0])
                            value = run_query("select count(*) from job where institution_code ='" + hospital +"' and job_stat='200';")
                            data.append(value[0][0])
                            value2 = run_query("select count(*) from job where job_stat='310' and institution_code='" + hospital + "';")
                            indicator.append(value2[0][0])

                        source = pd.DataFrame({
                            'Requested Job Count': data,
                            'Completed Job Count:': indicator,
                            'hospital': name
                        }).set_index('hospital')
                        st.bar_chart(source)
                elif filter == "Hospital" and filter_hospital in hospital:
                    if indicator == "None":
                        data = []
                        exam = filter_hospital
                        name = filter_hospital
                        value = run_query("select count(*) from job where institution_code ='" + exam +"' and job_stat='200';")
                        data.append(value)

                        source = pd.DataFrame({
                            'count': data[0][0],
                            'hospital': name
                        }).set_index('hospital')
                        st.bar_chart(source)
                    elif indicator == "Completed Job":
                        name = filter_hospital
                        data = []
                        indicator = []
                        hospital = filter_hospital
                        value = run_query("select count(*) from job where institution_code ='" + hospital +"' and job_stat='200';")
                        data.append(value)
                        value2 = run_query("select count(*) from job where job_stat='310' and institution_code='" + hospital + "';")
                        indicator.append(value2)

                        source = pd.DataFrame({
                            'Requested Job Count': data[0][0],
                            'Completed Job Count:': indicator[0][0],
                            'hospital': name
                        }).set_index('hospital')
                        st.bar_chart(source)
                elif filter == "Modality" and filter_modality in modality:
                    if indicator == "None":
                        name = []
                        data = []            
                        modality = filter_modality
                        for i in range(hospital_cnt): 
                            hospital = hospital_data[i][0]
                            name.append(hospital_data[i][0])
                            value = run_query("select count(*) from job where modality ='" + modality +"' and job_stat='200' and institution_code ='" + hospital + "';")
                            data.append(value[0][0])

                        source = pd.DataFrame({
                            'count': data,
                            'hospital': name
                        }).set_index('hospital')
                        st.bar_chart(source)
                    elif indicator == "Completed Job":
                        name = []
                        data = []
                        indicator = []
                        modality = filter_modality
                        for i in range(hospital_cnt): 
                            hospital = hospital_data[i][0]
                            name.append(hospital_data[i][0])
                            value = run_query("select count(*) from job where modality ='" + modality +"' and job_stat='200' and institution_code ='" + hospital + "';")
                            data.append(value[0][0])
                            value2 = run_query("select count(*) from job where job_stat='310' and institution_code='" + hospital + "' and modality ='" + modality +"'")
                            indicator.append(value2[0][0])

                        source = pd.DataFrame({
                            'Requested Job Count': data,
                            'Completed Job Count:': indicator,
                            'hospital': name
                        }).set_index('hospital')
                        st.bar_chart(source)
                elif filter == "Reporter" and filter_reporter in reporter:
                    if indicator == "None":
                        name = []
                        data = []            
                        reporter = filter_reporter
                        for i in range(hospital_cnt): 
                            hospital = hospital_data[i][0]
                            name.append(hospital_data[i][0])
                            value = run_query("select count(*) from job where request_name ='" + reporter +"' and job_stat='200' and institution_code ='" + hospital + "';")
                            data.append(value[0][0])

                        source = pd.DataFrame({
                            'count': data,
                            'hospital': name
                        }).set_index('hospital')
                        st.bar_chart(source)
                    elif indicator == "Completed Job":
                        name = []
                        data = []
                        indicator = []
                        reporter = filter_reporter
                        for i in range(hospital_cnt): 
                            hospital = hospital_data[i][0]
                            name.append(hospital_data[i][0])
                            value = run_query("select count(*) from job where request_name ='" + reporter +"' and job_stat='200' and institution_code ='" + hospital + "';")
                            data.append(value[0][0])
                            value2 = run_query("select count(*) from job where job_stat='310' and institution_code='" + hospital + "' and request_name ='" + reporter +"'")
                            indicator.append(value2[0][0])

                        source = pd.DataFrame({
                            'Requested Job Count': data,
                            'Completed Job Count:': indicator,
                            'hospital': name
                        }).set_index('hospital')
                        st.bar_chart(source)

            elif main_job_type == "Request Job" and job_type == "Emergency Job":
                hospital_data = run_query("select institution_code from job group by institution_code;")
                hospital = []
                for i in range(len(hospital_data)):
                    hospital.append(hospital_data[i][0])
                hospital_cnt = len(hospital)

                name = []
                data = []
                if filter == "None":
                    for i in range(hospital_cnt): 
                        exam = hospital_data[i][0]
                        name.append(hospital_data[i][0])
                        value = run_query("select count(*) from job where institution_code ='" + exam +"' and job_stat='200' and job_priority = 'E';")
                        data.append(value[0][0])

                    source = pd.DataFrame({
                        'count': data,
                    }, index=name) 
                    st.bar_chart(source)    
                elif filter == "Hospital" and filter_hospital in hospital:
                    data = []
                    exam = filter_hospital
                    name = filter_hospital
                    value = run_query("select count(*) from job where institution_code ='" + exam +"' and job_stat='200' and job_priority = 'E';")
                    data.append(value)

                    source = pd.DataFrame({
                        'count': data[0][0],
                        'hospital': name
                    }).set_index('hospital')
                    st.bar_chart(source)
                elif filter == "Modality" and filter_modality in modality:
                    name = []
                    data = []            
                    modality = filter_modality
                    for i in range(hospital_cnt): 
                        hospital = hospital_data[i][0]
                        name.append(hospital_data[i][0])
                        value = run_query("select count(*) from job where modality ='" + modality +"' and job_stat='200' and institution_code ='" + hospital + "' and job_priority = 'E';")
                        data.append(value[0][0])

                    source = pd.DataFrame({
                        'count': data,
                        'hospital': name
                    }).set_index('hospital')
                    st.bar_chart(source)
                elif filter == "Reporter" and filter_reporter in reporter:
                    name = []
                    data = []            
                    reporter = filter_reporter
                    for i in range(hospital_cnt): 
                        hospital = hospital_data[i][0]
                        name.append(hospital_data[i][0])
                        value = run_query("select count(*) from job where request_name ='" + reporter +"' and job_stat='200' and institution_code ='" + hospital + "' and job_priority = 'E';")
                        data.append(value[0][0])

                    source = pd.DataFrame({
                        'count': data,
                        'hospital': name
                    }).set_index('hospital')
                    st.bar_chart(source)
            elif job_type == "Completed Job":
                hospital = run_query("select institution_code from job group by institution_code;")
                hospital = []
                for i in range(len(hospital_data)):
                    hospital.append(hospital_data[i][0])
                hospital_cnt = len(hospital)

                name = []
                data = []
                if filter == "None":
                    for i in range(hospital_cnt): 
                        exam = hospital_data[i][0]
                        name.append(hospital_data[i][0])
                        value = run_query("select count(*) from job where institution_code ='" + exam +"' and job_stat='310';")
                        data.append(value[0][0])

                    source = pd.DataFrame({
                        'count': data,
                    }, index=name) 
                    st.bar_chart(source)    
                elif filter == "Hospital" and filter_hospital in hospital:
                    data = []
                    exam = filter_hospital
                    name = filter_hospital
                    value = run_query("select count(*) from job where institution_code ='" + exam +"' and job_stat='310';")
                    data.append(value)

                    source = pd.DataFrame({
                        'count': data[0][0],
                        'hospital': name
                    }).set_index('hospital')
                    st.bar_chart(source)
                elif filter == "Modality" and filter_modality in modality:
                    name = []
                    data = []            
                    modality = filter_modality
                    for i in range(hospital_cnt): 
                        hospital = hospital_data[i][0]
                        name.append(hospital_data[i][0])
                        value = run_query("select count(*) from job where modality ='" + modality +"' and job_stat='310' and institution_code ='" + hospital + "';")
                        data.append(value[0][0])

                    source = pd.DataFrame({
                        'count': data,
                        'hospital': name
                    }).set_index('hospital')
                    st.bar_chart(source)
                elif filter == "Reporter" and filter_reporter in reporter:
                    name = []
                    data = []            
                    reporter = filter_reporter
                    for i in range(hospital_cnt): 
                        hospital = hospital_data[i][0]
                        name.append(hospital_data[i][0])
                        value = run_query("select count(*) from job where request_name ='" + reporter +"' and job_stat='310' and institution_code ='" + hospital + "';")
                        data.append(value[0][0])

                    source = pd.DataFrame({
                        'count': data,
                        'hospital': name
                    }).set_index('hospital')
                    st.bar_chart(source)

        elif criteria == "Month":
            if job_type == "Requested Job":
                    total = run_query("select count(*) from job where job_dttm between current_date - interval '1 month' and current_date;")
                    requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '1 month' and current_date;")
                    hospital_data = run_query("select institution_code from job group by institution_code;")
                    hospital = []
                    for i in range(len(hospital_data)):
                        hospital.append(hospital_data[i][0])
                    hospital_cnt = len(hospital)

                    if filter == "None":
                        if indicator == "None":
                            name = []
                            data = []
                            if value_type == "Count":
                                for i in range(hospital_cnt): 
                                    hospital = hospital_data[i][0]
                                    name.append(hospital_data[i][0])
                                    value = run_query("select count(*) from job where institution_code ='" + hospital +"' and job_stat='200' and job_dttm between current_date - interval '1 month' and current_date;")
                                    data.append(value[0][0])

                                source = pd.DataFrame({
                                    'Requested Job Count': data,
                                    'hospital': name
                                }).set_index('hospital')
                                st.bar_chart(source)
                            elif value_type == "Ratio(%)":
                                for i in range(hospital_cnt): 
                                    hospital = hospital_data[i][0]
                                    name.append(hospital_data[i][0])
                                    value = run_query("select count(*) from job where institution_code ='" + hospital +"' and job_stat='200' and job_dttm between current_date - interval '1 month' and current_date;")
                                    ratio = round((value[0][0] * 100) / total[0][0],1)
                                    data.append(ratio)

                                source = pd.DataFrame({
                                    'Ratio(%)': data,
                                    'hospital': name
                                }).set_index('hospital')
                                st.bar_chart(source)

    elif group == "Modality":
        
        if job_type == "Requested Job":
            modality_data = run_query("select modality from job group by modality;")
            modality = []
            for i in range(len(modality_data)):
                modality.append(modality_data[i][0])
            modality_cnt = len(modality)
            
            if filter == "None":
                if indicator == "None":
                    name = []
                    data = []
                    for i in range(modality_cnt): 
                        modality = modality_data[i][0]
                        name.append(modality_data[i][0])
                        value = run_query("select count(*) from job where modality ='" + modality +"' and job_stat='200';")
                        data.append(value[0][0])

                    source = pd.DataFrame({
                    'Requested Job Count': data,
                    'modality': name
                    }).set_index('modality')
                    st.bar_chart(source)

                elif indicator == "Completed Job":
                    name = []
                    data = []
                    indicator = []
                    for i in range(modality_cnt): 
                        modality = modality_data[i][0]
                        name.append(modality_data[i][0])
                        value = run_query("select count(*) from job where modality ='" + modality +"' and job_stat='200';")
                        data.append(value[0][0])
                        value2 = run_query("select count(*) from job where job_stat='310' and modality='" + modality + "';")
                        indicator.append(value2[0][0])

                    source = pd.DataFrame({
                        'Requested Job Count': data,
                        'Completed Job Count:': indicator,
                        'modality': name
                    }).set_index('modality')
                    st.bar_chart(source)
            elif filter == "Hospital" and filter_hospital in hospital:
                data = []
                name = []
                for i in range(modality_cnt): 
                    modality = modality_data[i][0]
                    name.append(modality_data[i][0])
                    hospital = filter_hospital
                    value = run_query("select count(*) from job where modality ='" + modality +"' and job_stat='200' and institution_code ='" + hospital + "';")
                    data.append(value[0][0])

                source = pd.DataFrame({
                    'Requested Job Count': data,
                    'modality': name
                }).set_index('modality')
                st.bar_chart(source)
            elif filter == "Modality" and filter_modality in modality:
                data = []            
                modality = filter_modality
                name = filter_modality
                value = run_query("select count(*) from job where modality ='" + modality +"' and job_stat='200';")
                data.append(value[0][0])

                source = pd.DataFrame({
                    'Requested Job Count': data,
                    'modality': name
                }).set_index('modality')
                st.bar_chart(source)
            elif filter == "Reporter" and filter_reporter in reporter:
                name = []
                data = []            
                reporter = filter_reporter
                for i in range(modality_cnt): 
                    modality = modality_data[i][0]
                    name.append(modality_data[i][0])
                    value = run_query("select count(*) from job where request_name ='" + reporter +"' and job_stat='200' and modality ='" + modality + "';")
                    data.append(value[0][0])

                source = pd.DataFrame({
                    'Requested Job Count': data,
                    'modality': name
                }).set_index('modality')
                st.bar_chart(source)

        elif main_job_type == "Request Job" and job_type == "Emergency Job":
                modality_data = run_query("select modality from job group by modality;")
                modality = []
                for i in range(len(modality_data)):
                    modality.append(modality_data[i][0])
                modality_cnt = len(modality)

                if filter == "None":
                    name = []
                    data = []
                    for i in range(modality_cnt): 
                        modality = modality_data[i][0]
                        name.append(modality_data[i][0])
                        value = run_query("select count(*) from job where job_stat='200' and job_priority = 'E' and modality ='" + modality + "';")
                        data.append(value[0][0])

                    source = pd.DataFrame({
                        'Requested Job Count': data,
                        'modality': name
                    }).set_index('modality')
                    st.bar_chart(source)    
                elif filter == "Hospital" and filter_hospital in hospital:
                    data = []
                    name = []
                    for i in range(modality_cnt): 
                        modality = modality_data[i][0]
                        name.append(modality_data[i][0])
                        hospital = filter_hospital
                        value = run_query("select count(*) from job where job_stat='200' and job_priority = 'E' and institution_code ='" + hospital + "' and modality ='" + modality + "';")
                        data.append(value[0][0])

                    source = pd.DataFrame({
                        'Requested Job Count': data,
                        'modality': name
                    }).set_index('modality')
                    st.bar_chart(source)
                elif filter == "Modality" and filter_modality in modality:
                    name = filter_modality
                    data = []            
                    modality = filter_modality
                    value = run_query("select count(*) from job where modality ='" + modality +"' and job_stat='200' and job_priority = 'E';")
                    data.append(value[0][0])

                    source = pd.DataFrame({
                        'Requested Job Count': data,
                        'modality': name
                    }).set_index('modality')
                    st.bar_chart(source)
                elif filter == "Reporter" and filter_reporter in reporter:
                    name = []
                    data = []            
                    reporter = filter_reporter
                    for i in range(modality_cnt): 
                        modality = modality_data[i][0]
                        name.append(modality_data[i][0])
                        value = run_query("select count(*) from job where request_name ='" + reporter +"' and job_stat='200' and job_priority = 'E' and modality ='" + modality + "';")
                        data.append(value[0][0])

                    source = pd.DataFrame({
                        'Requested Job Count': data,
                        'modality': name
                    }).set_index('modality')
                    st.bar_chart(source)

        elif job_type == "Completed Job":
            modality = run_query("select modality from job group by modality;")
            modality = []
            for i in range(len(modality_data)):
                modality.append(modality_data[i][0])
            modality_cnt = len(modality)
            
            if filter == "None":
                name = []
                data = []
                for i in range(modality_cnt): 
                    modality = modality_data[i][0]
                    name.append(modality_data[i][0])
                    value = run_query("select count(*) from job where modality ='" + modality +"' and job_stat='310';")
                    data.append(value[0][0])

                source = pd.DataFrame({
                    'count': data,
                    'modality': name
                }).set_index('modality')
                st.bar_chart(source)
            elif filter == "Hospital" and filter_hospital in hospital:
                data = []
                name = []
                for i in range(modality_cnt): 
                    modality = modality_data[i][0]
                    name.append(modality_data[i][0])
                    hospital = filter_hospital
                    value = run_query("select count(*) from job where modality ='" + modality +"' and job_stat='310' and institution_code ='" + hospital + "';")
                    data.append(value[0][0])

                source = pd.DataFrame({
                    'count': data,
                    'modality': name
                }).set_index('modality')
                st.bar_chart(source)
            elif filter == "Modality" and filter_modality in modality:
                data = []            
                modality = filter_modality
                name = filter_modality
                value = run_query("select count(*) from job where modality ='" + modality +"' and job_stat='310';")
                data.append(value[0][0])

                source = pd.DataFrame({
                    'count': data,
                    'modality': name
                }).set_index('modality')
                st.bar_chart(source)
            elif filter == "Reporter" and filter_reporter in reporter:
                name = []
                data = []            
                reporter = filter_reporter
                for i in range(modality_cnt): 
                    modality = modality_data[i][0]
                    name.append(modality_data[i][0])
                    value = run_query("select count(*) from job where request_name ='" + reporter +"' and job_stat='310' and modality ='" + modality + "';")
                    data.append(value[0][0])

                source = pd.DataFrame({
                    'count': data,
                    'modality': name
                }).set_index('modality')
                st.bar_chart(source)

        elif main_job_type == "Cancel Job" and job_type == "Emergency Job":
            modality_data = run_query("select modality from job group by modality;")
            modality = []
            for i in range(len(modality_data)):
                modality.append(modality_data[i][0])
            modality_cnt = len(modality)
            
            if filter == "None":
                if indicator == "None":
                    name = []
                    data = []
                    for i in range(modality_cnt): 
                        modality = modality_data[i][0]
                        name.append(modality_data[i][0])
                        value = run_query("select count(*) from job where modality ='" + modality +"' and job_stat='100' and job_priority='E';")
                        data.append(value[0][0])

                    source = pd.DataFrame({
                    'Canceled Job Count': data,
                    'modality': name
                    }).set_index('modality')
                    st.bar_chart(source)

    elif group == "Reporter":
        if job_type == "Requested Job":
            reporter_data = run_query("select request_name from job group by request_name;")
            reporter = []
            for i in range(len(reporter_data)):
                reporter.append(reporter_data[i][0])
            reporter_cnt = len(reporter)

            if filter == "None":
                if indicator == "None":
                    name = []
                    data = []
                    for i in range(reporter_cnt): 
                        reporter = reporter_data[i][0]
                        name.append(reporter_data[i][0])
                        value = run_query("select count(*) from job where request_name ='" + reporter +"' and job_stat='200';")
                        data.append(value[0][0])

                    source = pd.DataFrame({
                        'count': data,
                        'reporter': name
                    }).set_index('reporter')
                    st.bar_chart(source)
                elif indicator == "Completed Job":
                    name = []
                    data = []
                    indicator = []
                    for i in range(reporter_cnt): 
                        reporter = reporter_data[i][0]
                        name.append(reporter_data[i][0])
                        value = run_query("select count(*) from job where request_name ='" + reporter +"' and job_stat='200';")
                        data.append(value[0][0])
                        value2 = run_query("select count(*) from job where job_stat='310' and request_name='" + reporter + "';")
                        indicator.append(value2[0][0])

                    source = pd.DataFrame({
                        'Requested Job Count': data,
                        'Completed Job Count:': indicator,
                        'reporter': name
                    }).set_index('reporter')
                    st.bar_chart(source)
            elif filter == "Hospital" and filter_hospital in hospital:
                data = []
                name = []
                for i in range(reporter_cnt): 
                    reporter = reporter_data[i][0]
                    name.append(reporter_data[i][0])
                    hospital = filter_hospital
                    value = run_query("select count(*) from job where request_name ='" + reporter +"' and job_stat='200' and institution_code ='" + hospital + "';")
                    data.append(value[0][0])

                source = pd.DataFrame({
                    'count': data,
                    'reporter': name
                }).set_index('reporter')
                st.bar_chart(source)
            elif filter == "Modality" and filter_modality in modality:
                data = []    
                name = []
                for i in range(reporter_cnt): 
                    reporter = reporter_data[i][0]
                    name.append(reporter_data[i][0])
                    modality = filter_modality        
                    value = run_query("select count(*) from job where request_name ='" + reporter +"' and job_stat='200' and modality ='" + modality + "';")            
                    data.append(value[0][0])

                source = pd.DataFrame({
                    'count': data,
                    'reporter': name
                }).set_index('reporter')
                st.bar_chart(source)
            elif filter == "Reporter" and filter_reporter in reporter:
                name = filter_reporter
                data = []            
                reporter = filter_reporter
                value = run_query("select count(*) from job where request_name ='" + reporter +"' and job_stat='200'")
                data.append(value[0][0])

                source = pd.DataFrame({
                    'count': data,
                    'reporter': name
                }).set_index('reporter')
                st.bar_chart(source)

        elif job_type == "Completed Job":
            reporter = run_query("select request_name from job group by request_name;")
            reporter = []
            for i in range(len(reporter_data)):
                reporter.append(reporter_data[i][0])
            reporter_cnt = len(reporter)

            name = []
            data = []
            if filter == "None":
                for i in range(reporter_cnt): 
                    reporter = reporter_data[i][0]
                    name.append(reporter_data[i][0])
                    value = run_query("select count(*) from job where request_name ='" + reporter +"' and job_stat='310';")
                    data.append(value[0][0])

                source = pd.DataFrame({
                    'count': data,
                    'reporter': name
                }).set_index('reporter')
                st.bar_chart(source)
            elif filter == "Hospital" and filter_hospital in hospital:
                data = []
                name = []
                for i in range(reporter_cnt): 
                    reporter = reporter_data[i][0]
                    name.append(reporter_data[i][0])
                    hospital = filter_hospital
                    value = run_query("select count(*) from job where request_name ='" + reporter +"' and job_stat='310' and institution_code ='" + hospital + "';")
                    data.append(value[0][0])

                source = pd.DataFrame({
                    'count': data,
                    'reporter': name
                }).set_index('reporter')
                st.bar_chart(source)
            elif filter == "Modality" and filter_modality in modality:
                data = []    
                name = []
                for i in range(reporter_cnt): 
                    reporter = reporter_data[i][0]
                    name.append(reporter_data[i][0])
                    modality = filter_modality        
                    value = run_query("select count(*) from job where request_name ='" + reporter +"' and job_stat='310' and modality ='" + modality + "';")            
                    data.append(value[0][0])

                source = pd.DataFrame({
                    'count': data,
                    'reporter': name
                }).set_index('reporter')
                st.bar_chart(source)
            elif filter == "Reporter" and filter_reporter in reporter:
                name = filter_reporter
                data = []            
                reporter = filter_reporter
                value = run_query("select count(*) from job where request_name ='" + reporter +"' and job_stat='310'")
                data.append(value[0][0])

                source = pd.DataFrame({
                    'count': data,
                    'reporter': name
                }).set_index('reporter')
                st.bar_chart(source)
                
        elif main_job_type == "Request Job" and job_type == "Emergency Job":
            reporter = run_query("select request_name from job group by request_name;")
            reporter = []
            for i in range(len(reporter_data)):
                reporter.append(reporter_data[i][0])
            reporter_cnt = len(reporter)

            name = []
            data = []
            if filter == "None":
                for i in range(reporter_cnt): 
                    reporter = reporter_data[i][0]
                    name.append(reporter_data[i][0])
                    value = run_query("select count(*) from job where request_name ='" + reporter +"' and job_stat='200' and job_priority='E';")
                    data.append(value[0][0])

                source = pd.DataFrame({
                    'Requested Job Count': data,
                    'reporter': name
                }).set_index('reporter')
                st.bar_chart(source)
            elif filter == "Hospital" and filter_hospital in hospital:
                data = []
                name = []
                for i in range(reporter_cnt): 
                    reporter = reporter_data[i][0]
                    name.append(reporter_data[i][0])
                    hospital = filter_hospital
                    value = run_query("select count(*) from job where request_name ='" + reporter +"' and job_stat='200' and institution_code ='" + hospital + "'and job_priority='E';")
                    data.append(value[0][0])

                source = pd.DataFrame({
                    'Requested Job Count': data,
                    'reporter': name
                }).set_index('reporter')
                st.bar_chart(source)
            elif filter == "Modality" and filter_modality in modality:
                data = []    
                name = []
                for i in range(reporter_cnt): 
                    reporter = reporter_data[i][0]
                    name.append(reporter_data[i][0])
                    modality = filter_modality        
                    value = run_query("select count(*) from job where request_name ='" + reporter +"' and job_stat='200' and modality ='" + modality + "'and job_priority='E';")            
                    data.append(value[0][0])

                source = pd.DataFrame({
                    'Requested Job Count': data,
                    'reporter': name
                }).set_index('reporter')
                st.bar_chart(source)
            elif filter == "Reporter" and filter_reporter in reporter:
                name = filter_reporter
                data = []            
                reporter = filter_reporter
                value = run_query("select count(*) from job where request_name ='" + reporter +"' and job_stat='200' and job_priority='E'")
                data.append(value[0][0])

                source = pd.DataFrame({
                    'Requested Job Count': data,
                    'reporter': name
                }).set_index('reporter')
                st.bar_chart(source)

        elif main_job_type == "Complete Job" and job_type == "Emergency Job":
            reporter = run_query("select request_name from job group by request_name;")
            reporter = []
            for i in range(len(reporter_data)):
                reporter.append(reporter_data[i][0])
            reporter_cnt = len(reporter)

            name = []
            data = []
            if filter == "None":
                for i in range(reporter_cnt): 
                    reporter = reporter_data[i][0]
                    name.append(reporter_data[i][0])
                    value = run_query("select count(*) from job where request_name ='" + reporter +"' and job_stat='310' and job_priority='E';")
                    data.append(value[0][0])

                source = pd.DataFrame({
                    'Requested Job Count': data,
                    'reporter': name
                }).set_index('reporter')
                st.bar_chart(source)
            elif filter == "Hospital" and filter_hospital in hospital:
                data = []
                name = []
                for i in range(reporter_cnt): 
                    reporter = reporter_data[i][0]
                    name.append(reporter_data[i][0])
                    hospital = filter_hospital
                    value = run_query("select count(*) from job where request_name ='" + reporter +"' and job_stat='310' and institution_code ='" + hospital + "'and job_priority='E';")
                    data.append(value[0][0])

                source = pd.DataFrame({
                    'Requested Job Count': data,
                    'reporter': name
                }).set_index('reporter')
                st.bar_chart(source)
            elif filter == "Modality" and filter_modality in modality:
                data = []    
                name = []
                for i in range(reporter_cnt): 
                    reporter = reporter_data[i][0]
                    name.append(reporter_data[i][0])
                    modality = filter_modality        
                    value = run_query("select count(*) from job where request_name ='" + reporter +"' and job_stat='310' and modality ='" + modality + "'and job_priority='E';")            
                    data.append(value[0][0])

                source = pd.DataFrame({
                    'Requested Job Count': data,
                    'reporter': name
                }).set_index('reporter')
                st.bar_chart(source)
            elif filter == "Reporter" and filter_reporter in reporter:
                name = filter_reporter
                data = []            
                reporter = filter_reporter
                value = run_query("select count(*) from job where request_name ='" + reporter +"' and job_stat='310' and job_priority='E'")
                data.append(value[0][0])

                source = pd.DataFrame({
                    'Requested Job Count': data,
                    'reporter': name
                }).set_index('reporter')
                st.bar_chart(source)
