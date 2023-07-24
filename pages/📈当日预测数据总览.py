from pydoc import html

import pymysql
import st_aggrid
import streamlit as st
import datetime
import pandas as pd
import numpy as np
import plotly.express as px
import modelTest.predict as pre




def get_data_list(TurbID):

    # 连接到MySQL数据库
    mydb = pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="fd_client"
    )
    today_time = datetime.datetime.now()
    now_time = datetime.datetime.now()
    date_str = today_time.strftime("2022-6-30 00:00:00")
    date_str2 = now_time.strftime("2022-6-30 %H:%M:%S")

    # 查询昨天的YD15数据并按照TurbID分组和加和
    query2 = f"SELECT * FROM output_data WHERE TurbID = '{TurbID}'"
    df = pd.read_sql(query2, mydb)

    if 'DATETIME' in df.columns:
        df = df.drop('DATETIME', axis=1)
    df['DATATIME'] = df['DATATIME'].apply(
        lambda x: x.replace(year=datetime.datetime.today().year, month=datetime.datetime.today().month, day=datetime.datetime.today().day))

    # 将查询结果存储为字典
    result_dict = {}
    for col in df.columns:
        result_dict[col] = df[col].values

    return result_dict

def get_data_line_chart(TurbID, Predict):
    mydb = pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="fd_client"
    )
    # 将Predict列表转换为字符串，并使用反引号引用包含关键字的列名
    predict_str = ", ".join([f"`{col}`" if "ROUND(" in col else col for col in Predict])
    # 查询数据库中的数据
    query = f"SELECT TurbID,DATATIME, {predict_str} FROM output_data WHERE TurbID = {TurbID}"
    df = pd.read_sql(query, mydb)

    if 'DATETIME' in df.columns:
        df = df.drop('DATETIME', axis=1)
    df['DATATIME'] = df['DATATIME'].apply(
        lambda x: x.replace(year=datetime.datetime.today().year, month=datetime.datetime.today().month,
                                day=datetime.datetime.today().day))

    # 将查询结果存储为字典
    result_dict = {}
    for col in df.columns:
        result_dict[col] = df[col].values

    result_dict = pre.add_power_fluctuation3(result_dict,Predict,pre.calculate_groups())

    return result_dict


st.set_page_config(
    page_title="Data Page",
    page_icon="🥰🥰",
    layout="wide",
    initial_sidebar_state="expanded",
)

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""


st.title("当日功率排名及预测")
col1,col2 = st.columns([2,1])
with col2:
    with st.container():
        import streamlit as st
        # 定义风机和TurbID的字典
        turbine_dict = {"一号风机": 1, "二号风机": 2, "三号风机": 3, "四号风机": 4, "五号风机": 5, "六号风机": 6, "七号风机": 7, "八号风机": 8,
                        "九号风机": 9, "十号风机": 10, "十一号风机": 11, "十二号风机": 12, "十三号风机": 13, "十四号风机": 14, "十五号风机": 15,
                        "十六号风机": 16, "十七号风机": 17, "十八号风机": 18, "十九号风机": 19, "二十号风机": 20}

        # 获取下拉框中选定的风机名称和TurbID
        selected_turbine = st.selectbox("Select a turbine", list(turbine_dict.keys()))
        selected_turbine_id = turbine_dict[selected_turbine]

        min_val, max_val = st.slider("显示范围", 0.00, 1.00, (0.0, 1.0), step=0.01)
    with st.container():
        options = ['YD15', 'ROUND(A.POWER,0)']
        default_options = ['YD15']
        options_2_select = st.multiselect('选择特征', options, default_options)
        options_dict = {'YD15': 'YD15', 'ROUND(A.POWER,0)': 'ROUND(A.POWER,0)'}
        options_2 = [options_dict[i] for i in options_2_select]

data_list = get_data_list(selected_turbine_id)
df_list = pd.DataFrame(data_list)

with col1:
    # create AgGrid object
    ag1 = st_aggrid.AgGrid(
        df_list,
        editable=False,
        sortable=False,
        filter=False,
        resizable=False,
        defaultWidth=200,
        fit_columns_on_grid_load=True,
        height=500,
    )



data_line_chart = get_data_line_chart(str(selected_turbine_id),options_2)
df_bar_now = pd.DataFrame(data_line_chart)

# 计算要显示的数据的范围
start_index = int(min_val * len(df_bar_now))
end_index = int(max_val * len(df_bar_now))
df_bar_now = df_bar_now.iloc[start_index:end_index]

fig_2 = px.line(df_bar_now, x='DATATIME', y=options_2)
st.plotly_chart(fig_2,use_container_width=True)