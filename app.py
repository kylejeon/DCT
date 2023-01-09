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
    # modality = cur.execute("select modality from job group by modality")
    # reporter = cursor.execute("select requester_name from job group by requester_name")
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

st.header("LiveMeter Simulation")
main_job_type = st.selectbox('Select a main job type',("Request Job","Complete Job","Cancel Job"))
if main_job_type == "Request Job":
    job_type = st.radio('Select a job type',("Requested Job","Emergency Job"), horizontal=True)
elif main_job_type == "Complete Job":
    job_type = st.radio('Select a job type',("Completed Job","Emergency Job"), horizontal=True)
criteria = st.radio('Select a criteria',("All","Day","Week","Month"), horizontal=True)
value_type = st.radio('Select a value type',("Count","Ratio(%)","Count/Ratio"), horizontal=True)
filter = st.radio('Select a filter',("None","Hospital","Modality","Reporter"), horizontal=True)
if filter == "Hospital":
    filter_hospital = st.selectbox('select a hospital',("A병원","B병원","C병원"))
elif filter == "Modality":
    filter_modality = st.selectbox('select a modality',(modality))
elif filter == "Reporter":
    filter_reporter = st.selectbox('select a reporter',(reporter))

group = st.radio('Select a group',("None","Hospital","Modality","Reporter"), horizontal=True)
st.title("\n")
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
                # elif filter == "Reporter" and filter_reporter in reporter:
                #     requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and modality='" + filter_modality + "';")                    
                #     st.metric(label="Reuqested Job Count",value=requested_job_cnt[0][0])
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

        elif criteria == "Day":
            requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm =current_date;")
            total = run_query("select count(*) from job where job_dttm = current_date;")
            try:               
                ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)
            except ZeroDivisionError:
                ratio = 0
            if value_type == "Count":
                st.metric(label="Reuqested Job Count",value=requested_job_cnt[0][0])
            elif value_type == "Ratio(%)":
                st.metric(label="Reuqested Job Ratio(%)",value=str(ratio)+"%")
            else:
                st.metric(label="Reuqested Job Count/Ratio(%)",value=str(requested_job_cnt[0][0]) + "/" + str(ratio)+ "%")

        elif criteria == "Week":
            requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '1 week' and current_date;")
            total = run_query("select count(*) from job where job_dttm between current_date - interval '1 week' and current_date;")
            try:               
                ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)
            except ZeroDivisionError:
                ratio = 0
            if value_type == "Count":
                st.metric(label="Reuqested Job Count",value=requested_job_cnt[0][0])
            elif value_type == "Ratio(%)":
                st.metric(label="Reuqested Job Ratio(%)",value=str(ratio)+"%")
            else:
                st.metric(label="Reuqested Job Count/Ratio(%)",value=str(requested_job_cnt[0][0]) + "/" + str(ratio)+ "%")

        elif criteria == "Month":
            requested_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '1 month' and current_date;")
            total = run_query("select count(*) from job where job_dttm between current_date - interval '1 month' and current_date;")
            try:               
                ratio = round((requested_job_cnt[0][0] * 100) / total[0][0],1)
            except ZeroDivisionError:
                ratio = 0
            if value_type == "Count":
                st.metric(label="Reuqested Job Count",value=requested_job_cnt[0][0])
            elif value_type == "Ratio(%)":
                st.metric(label="Reuqested Job Ratio(%)",value=str(ratio)+"%")
            else:
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
                st.metric(label="Completed Job Count",value=completed_job_cnt[0][0])
            elif value_type == "Ratio(%)":
                st.metric(label="Completed Job Ratio(%)",value=str(ratio)+"%")
            else:
                st.metric(label="Completed Job Count/Ratio(%)",value=str(completed_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
        elif criteria == "Day":
            completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_dttm =current_date;")
            total = run_query("select count(*) from job where job_dttm =current_date;")
            try:               
                ratio = round((completed_job_cnt[0][0] * 100) / total[0][0],1)
            except ZeroDivisionError:
                ratio = 0
            if value_type == "Count":
                st.metric(label="Completed Job Count",value=completed_job_cnt[0][0])
            elif value_type == "Ratio(%)":
                st.metric(label="Completed Job Ratio(%)",value=str(ratio)+"%")
            else:
                st.metric(label="Completed Job Count/Ratio(%)",value=str(completed_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
        elif criteria == "Week":
            completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '1 week' and current_date;")
            total = run_query("select count(*) from job where job_dttm between current_date - interval '1 week' and current_date;")
            try:               
                ratio = round((completed_job_cnt[0][0] * 100) / total[0][0],1)
            except ZeroDivisionError:
                ratio = 0
            if value_type == "Count":
                st.metric(label="Completed Job Count",value=completed_job_cnt[0][0])
            elif value_type == "Ratio(%)":
                st.metric(label="Completed Job Ratio(%)",value=str(ratio)+"%")
            else:
                st.metric(label="Completed Job Count/Ratio(%)",value=str(completed_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
        elif criteria == "Month":
            completed_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '1 month' and current_date;")
            total = run_query("select count(*) from job where job_dttm between current_date - interval '1 month' and current_date;")
            try:               
                ratio = round((completed_job_cnt[0][0] * 100) / total[0][0],1)
            except ZeroDivisionError:
                ratio = 0
            if value_type == "Count":
                st.metric(label="Completed Job Count",value=completed_job_cnt[0][0])
            elif value_type == "Ratio(%)":
                st.metric(label="Completed Job Ratio(%)",value=str(ratio)+"%")
            else:
                st.metric(label="Completed Job Count/Ratio(%)",value=str(completed_job_cnt[0][0]) + "/" + str(ratio)+ "%",)

    elif main_job_type == "Request Job" and job_type == "Emergency Job":
        if criteria == "All":
            emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E';")
            total = run_query("select count(*) from job where job_stat = '200';")
            try:               
                ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
            except ZeroDivisionError:
                ratio = 0
            if value_type == "Count":
                st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
            elif value_type == "Ratio(%)":
                st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
            else:
                st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
        elif criteria == "Day":
            emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and job_dttm =current_date;")
            total = run_query("select count(*) from job where job_stat = '200' and job_dttm =current_date;")
            try:               
                ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
            except ZeroDivisionError:
                ratio = 0
            if value_type == "Count":
                st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
            elif value_type == "Ratio(%)":
                st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
            else:
                st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
        elif criteria == "Week":
            emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and job_dttm between current_date - interval '1 week' and current_date;")
            total = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '1 week' and current_date;")
            try:               
                ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
            except ZeroDivisionError:
                ratio = 0
            if value_type == "Count":
                st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
            elif value_type == "Ratio(%)":
                st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
            else:
                st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
        elif criteria == "Month":
            emgerency_job_cnt = run_query("select count(*) from job where job_stat = '200' and job_priority = 'E' and job_dttm between current_date - interval '1 month' and current_date;")
            total = run_query("select count(*) from job where job_stat = '200' and job_dttm between current_date - interval '1 month' and current_date;")
            try:               
                ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
            except ZeroDivisionError:
                ratio = 0
            if value_type == "Count":
                st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
            elif value_type == "Ratio(%)":
                st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
            else:
                st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
    elif main_job_type == "Complete Job" and job_type == "Emergency Job":
        if criteria == "All":
            emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E';")
            total = run_query("select count(*) from job where job_stat = '310';")
            try:               
                ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
            except ZeroDivisionError:
                ratio = 0
            if value_type == "Count":
                st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
            elif value_type == "Ratio(%)":
                st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
            else:
                st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
        elif criteria == "Day":
            emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and job_dttm =current_date;")
            total = run_query("select count(*) from job where job_stat = '310' and job_dttm =current_date;")
            try:               
                ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
            except ZeroDivisionError:
                ratio = 0
            if value_type == "Count":
                st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
            elif value_type == "Ratio(%)":
                st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
            else:
                st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
        elif criteria == "Week":
            emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and job_dttm between current_date - interval '1 week' and current_date;")
            total = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '1 week' and current_date;")
            try:               
                ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
            except ZeroDivisionError:
                ratio = 0
            if value_type == "Count":
                st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
            elif value_type == "Ratio(%)":
                st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
            else:
                st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)
        elif criteria == "Month":
            emgerency_job_cnt = run_query("select count(*) from job where job_stat = '310' and job_priority = 'E' and job_dttm between current_date - interval '1 month' and current_date;")
            total = run_query("select count(*) from job where job_stat = '310' and job_dttm between current_date - interval '1 month' and current_date;")
            try:               
                ratio = round((emgerency_job_cnt[0][0] * 100) / total[0][0],1)
            except ZeroDivisionError:
                ratio = 0
            if value_type == "Count":
                st.metric(label="Emergency Job Count",value=emgerency_job_cnt[0][0])
            elif value_type == "Ratio(%)":
                st.metric(label="Emergency Job Ratio(%)",value=str(ratio)+"%")
            else:
                st.metric(label="Emergency Job Count/Ratio(%)",value=str(emgerency_job_cnt[0][0]) + "/" + str(ratio)+ "%",)

elif group == "Hospital":
    if job_type == "Requested Job":
        hospital = run_query("select institution_code from job group by institution_code;")
        hospital_cnt = len(hospital)

        name = []
        data = []
        for i in range(hospital_cnt): 
            exam = hospital[i][0]
            name.append(hospital[i][0])
            value = run_query("select count(*) from job where institution_code ='" + exam +"' and job_stat='200';")
            data.append(value[0][0])

        source = pd.DataFrame({
            'count': data,
        },index=name)
        st.bar_chart(source)
    elif job_type == "Completed Job":
        hospital = run_query("select institution_code from job group by institution_code;")
        hospital_cnt = len(hospital)

        name = []
        data = []
        for i in range(hospital_cnt): 
            exam = hospital[i][0]
            name.append(hospital[i][0])
            value = run_query("select count(*) from job where institution_code ='" + exam +"' and job_stat='310';")
            data.append(value[0][0])

        source = pd.DataFrame({
            'count': data,
        }, index=name) 
        st.bar_chart(source)

elif group == "Modality":
    if job_type == "Requested Job":
        modality = run_query("select modality from job group by modality;")
        modality_cnt = len(modality)

        name = []
        data = []
        for i in range(modality_cnt): 
            exam = modality[i][0]
            name.append(modality[i][0])
            value = run_query("select count(*) from job where modality ='" + exam +"' and job_stat='200';")
            data.append(value[0][0])

        source = pd.DataFrame({
            'count': data,
        },index=name)
        st.bar_chart(source)
    elif job_type == "Completed Job":
        modality = run_query("select modality from job group by modality;")
        modality_cnt = len(modality)

        name = []
        data = []
        for i in range(modality_cnt): 
            exam = modality[i][0]
            name.append(modality[i][0])
            value = run_query("select count(*) from job where modality ='" + exam +"' and job_stat='310';")
            data.append(value[0][0])

        source = pd.DataFrame({
            'count': data,
        },index=name)
        st.bar_chart(source)

# elif group == "Reporter":
#     if job_type == "Requested Job":
#         reporter = run_query("select reporter from job group by reporter;")
#         reporter_cnt = len(reporter)

#         name = []
#         data = []
#         for i in range(reporter_cnt): 
#             exam = reporter[i][0]
#             name.append(reporter[i][0])
#             value = run_query("select count(*) from job where reporter ='" + exam +"' and job_stat='200';")
#             data.append(value[0][0])

#         source = pd.DataFrame({
#             'count': data,
#         },index=name)
#         st.bar_chart(source)
#     elif job_type == "Completed Job":
#         reporter = run_query("select request_name from job group by request_name;")
#         reporter_cnt = len(reporter)

#         name = []
#         data = []
#         for i in range(reporter_cnt): 
#             exam = reporter[i][0]
#             name.append(reporter[i][0])
#             value = run_query("select count(*) from job where request_name ='" + exam +"' and job_stat='310';")
#             data.append(value[0][0])

#         source = pd.DataFrame({
#             'count': data,
#         },index=name)
#         st.bar_chart(source)
