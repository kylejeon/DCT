import streamlit as st
import psycopg2

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
# cursor = connection.cursor()
# connection.commit()

# data =[100,200,300,400]

# st.bar_chart(data)

@st.experimental_memo(ttl=660)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()
    # modality = cur.execute("select modality from job group by modality")
    # reporter = cursor.execute("select requester_name from job group by requester_name")
modality = run_query("select modality from job group by modality;")
reporter = run_query("select request_name from job group by request_name;")


st.header("Job Type")
job_type = st.selectbox('Select a job type',("Requested Job","Completed Job","Scheduled Job","Emergency Job"))
criteria = st.radio('Select a criteria',("All","Day","Week","Month"))
value_type = st.radio('Select a value type',("Count","Ratio(%)","Count/Ratio"))
filter = st.radio('Select a filter',("None","Hospital","Modality","Reporter"))
filter_hospital = st.selectbox('select a hospital',("A병원","B병원","C병원"))
filter_modality = st.selectbox('select a modality',(modality))
filter_reporter = st.selectbox('select a reporter',(reporter))
