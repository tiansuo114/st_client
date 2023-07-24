import pymysql
import streamlit as st
import st_aggrid
import datetime
import pandas as pd
import numpy as np
import plotly.express as px
import modelTest.predict as pre

st.set_page_config(
    page_title="Main Page",
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



def get_data_list():
    mydb = pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="fd_client"
    )
    now = datetime.datetime.now()
    next_time = datetime.datetime.now() + datetime.timedelta(minutes=15)
    next_next_time = datetime.datetime.now() + datetime.timedelta(minutes=30)
    date_str = now.strftime("2022-06-30 %H:%M:%S")
    date_str2 = next_time.strftime("2022-06-30 %H:%M:%S")
    date_str3 = next_next_time.strftime("2022-06-30 %H:%M:%S")
    now_sql = f"SELECT TurbID, SUM(YD15) as YD15_sum FROM output_data WHERE DATATIME > '{date_str}' AND DATATIME < '{date_str2}' GROUP BY TurbID"
    next_sql = f"SELECT TurbID, SUM(YD15) as YD15_sum FROM output_data WHERE DATATIME > '{date_str2}' AND DATATIME < '{date_str3} ' GROUP BY TurbID"

    df_now = pd.read_sql(now_sql, mydb)
    df_next = pd.read_sql(next_sql, mydb)

    result_dict = {
        '风机号': df_now['TurbID'].values,
        '当前YD15': df_now['YD15_sum'].values,
        '下一时刻预测YD15': df_next['YD15_sum'].values,
    }

    result_dict = pre.add_yd15_fluctuation(result_dict)

    return result_dict

def get_data_yes():
    # 连接到MySQL数据库
    mydb = pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="fd_client"
    )
    today = datetime.datetime.now()
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    date_str = yesterday.strftime("2022-06-30 00:00:00")
    date_str2 = today.strftime("2022-06-30 23:59:00")
    # 查询昨天的YD15数据并按照TurbID分组和加和
    query = f"SELECT TurbID, SUM(YD15) as YD15_sum FROM output_data WHERE DATATIME >= '{date_str}' AND DATATIME < '{date_str2}' GROUP BY TurbID"
    df = pd.read_sql(query, mydb)

    # 将查询结果存储为字典
    result_dict = {
        '风机号': df['TurbID'].values,
        '发电量': df['YD15_sum'].values,
    }

    result_dict = pre.add_power_fluctuation(result_dict)

    return result_dict

def get_data_now():
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
    query2 = f"SELECT TurbID, SUM(YD15) as YD15_sum FROM output_data WHERE DATATIME >= '{date_str}' AND DATATIME < '{date_str2} ' GROUP BY TurbID"
    df = pd.read_sql(query2, mydb)

    count = pre.calculate_groups()

    # 将查询结果存储为字典
    result_dict = {
        '风机号': df['TurbID'].values,
        '发电量': df['YD15_sum'].values,
    }

    result_dict = pre.add_power_fluctuation2(result_dict, count)

    return result_dict


st.write("# 龙源风电赛道-LSTMYYDS队伍软件作品展示")
current_time = datetime.datetime.now()
st.write("当前时间:" + current_time.strftime("%Y-%m-%d %H:%M:%S"))
st.write("下一次更新的时间:" + (current_time + datetime.timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S"))

# 创建表格数据
data_list = get_data_list()
data_now = get_data_now()
data_yes = get_data_yes()

df_list = pd.DataFrame(data_list)
df_now = pd.DataFrame(data_now)
# 创建柱状图数据
df_bar_yes = pd.DataFrame(data_yes)

# 显示表格和柱状图
col1, col2 = st.columns([2,4])


with col1:
    st.title("近期功率预测")
    ag1 = st_aggrid.AgGrid(
        df_list,
        editable=False,
        sortable=False,
        filter=False,
        resizable=False,
        defaultWidth=200,
        fit_columns_on_grid_load=True,
        height=450,
    )

    st.title("今日截至目前总发电量")
    ag2 = st_aggrid.AgGrid(
        df_now,
        editable=False,
        sortable=False,
        filter=False,
        resizable=False,
        defaultWidth=200,
        fit_columns_on_grid_load=True,
        height=400,
    )


with col2:
    st.title("昨日各风机发电量")
    fig_1 = px.bar(df_bar_yes, x='风机号', y='发电量')
    fig_1.update_layout(yaxis_range=[min(df_bar_yes['发电量']) - 5000,max(df_bar_yes['发电量']) + 500 ])
    st.plotly_chart(fig_1, use_container_width=True)
    st.title("昨日各风机发电量比例")
    df_pie = data_yes
    fig_2 = px.pie(df_pie, values='发电量', names='风机号')
    st.plotly_chart(fig_2, use_container_width=True)

col3, col4 = st.columns([4,2])
with col3:
    df_bar_now = pd.DataFrame(data_now)

    st.title("今日截至目前各风机发电量")
    fig_2 = px.bar(df_bar_now, x='风机号', y='发电量')
    fig_2.update_layout(yaxis_range=[min(df_bar_now['发电量']) - 5000,max(df_bar_now['发电量']) + 500 ])
    st.plotly_chart(fig_2, use_container_width=True)

with col4:
    st.title("今日截至目前各风机发电量比例")
    df_pie = data_now
    fig_3 = px.pie(df_pie, values='发电量', names='风机号')
    st.plotly_chart(fig_3, use_container_width=True)

