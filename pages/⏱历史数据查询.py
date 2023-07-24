import base64
import pymysql
import st_aggrid
import streamlit as st
import datetime
import pandas as pd
import numpy as np
import plotly.express as px


def search_data(start_date, end_date, turbineIDs):
    # 连接到MySQL数据库
    mydb = pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="fd_client"
    )

    # 将turbineIDs转换为字符串并拼接到SQL语句中
    turbineID_str = ",".join(str(id) for id in turbineIDs)
    query = f"SELECT * FROM input_data WHERE DATATIME >= '{start_date}' AND DATATIME < '{end_date}' AND TurbID IN ({turbineID_str})"
    df = pd.read_sql(query, mydb)

    # 将查询结果存储为字典
    result_dict = {}
    for col in df.columns:
        result_dict[col] = df[col].values

    return result_dict

st.set_page_config(
    page_title="Predict Page",
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

col1, col2 = st.columns([1, 2])

with col1:
    # 创建一个带有标题为"参数调整"的可折叠框
    with st.expander("参数调整"):
        # 添加一个标题为"选择预测开始日期"的文本输入框
        start_date = st.text_input("开始日期",placeholder='YYYY-MM-DD xx:xx:xx', value='2021-01-31 00:00:00')

        # 添加一个标题为"选择预测结束日期"的文本输入框
        end_date = st.text_input("结束日期",placeholder='YYYY-MM-DD xx:xx:xx', value='2021-01-32 00:00:00')

        # 添加一个标题为"选择风机编号"的
        # 定义风机和TurbID的字典
        turbine_dict = {"一号风机": 1, "二号风机": 2, "三号风机": 3, "四号风机": 4, "五号风机": 5, "六号风机": 6, "七号风机": 7, "八号风机": 8,
                        "九号风机": 9, "十号风机": 10, "十一号风机": 11, "十二号风机": 12, "十三号风机": 13, "十四号风机": 14, "十五号风机": 15,
                        "十六号风机": 16, "十七号风机": 17, "十八号风机": 18, "十九号风机": 19, "二十号风机": 20}

        options = list(turbine_dict.keys())
        selected_turbineIDs = st.multiselect("选择风机编号", options)
        turbineID = [turbine_dict[x] for x in selected_turbineIDs]
        if st.button("执行查询"):
            # 检查参数输入是否合规
            if start_date and end_date  and turbineID:
                df = search_data(start_date, end_date, turbineID)
                df_list = pd.DataFrame(df)
                with col2:
                    # 添加一个带有标题为"数据预览"的展开框
                    st.title("当前功率排名及预测")
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
                    # 添加一个带有标题为"下载数据"的展开框
                    with st.expander("下载数据"):
                        csv = df_list.to_csv(index=False)
                        st.download_button(
                            label="下载CSV文件",
                            data=csv,
                            file_name="data.csv",
                            mime="text/csv",
                        )

            else:
                st.error("请填写所有参数并确保日期格式正确。")

