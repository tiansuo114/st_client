import time

import pandas as pd
import pymysql
import st_aggrid
import streamlit as st
import datetime
import modelTest.predict as pre
import plotly.express as px


def create_dataframe(start_date, end_date, feature, turbineID):
    mydb = pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="fd_client"
    )

    # Construct the SQL query to fetch data between start_date and end_date
    query = f"SELECT TurbID,DATATIME, `{feature}` FROM output_data WHERE TurbID = {turbineID} "

    # Fetch data from the database
    df = pd.read_sql(query, mydb)

    # Create a DatetimeIndex with 15 minutes frequency
    index = pd.date_range(start=start_date, end=end_date, freq='15T')

    df_new = pd.DataFrame(columns=['TurbID', 'DATATIME', feature])

    df_new['DATATIME'] = index
    df_new['TurbID'] = turbineID
    df_new[feature] = df[feature].sample(n=len(index), replace=True).tolist()

    result_dict = df_new.to_dict(orient='list')

    result_dict = pre.add_power_fluctuation4(result_dict, feature)


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
        start_date = st.text_input("选择预测开始日期",placeholder='YYYY-MM-DD xx:xx:xx', value='2021-01-30 00:00:00')

        # 添加一个标题为"选择预测结束日期"的文本输入框
        end_date = st.text_input("选择预测结束日期",placeholder='YYYY-MM-DD xx:xx:xx', value='2021-01-31 00:00:00')

        # 添加一个标题为"选择预测特征"的下拉栏
        feature = st.selectbox("选择预测特征",  ['YD15','ROUND(A.POWER,0)'])

        # 添加一个标题为"选择风机编号"的
        # 定义风机和TurbID的字典
        turbine_dict = {"一号风机": 1, "二号风机": 2, "三号风机": 3, "四号风机": 4, "五号风机": 5, "六号风机": 6, "七号风机": 7, "八号风机": 8,
                        "九号风机": 9, "十号风机": 10, "十一号风机": 11, "十二号风机": 12, "十三号风机": 13, "十四号风机": 14, "十五号风机": 15,
                        "十六号风机": 16, "十七号风机": 17, "十八号风机": 18, "十九号风机": 19, "二十号风机": 20}

        selected_turbine = st.radio("选择风机编号",turbine_dict)
        turbineID = turbine_dict[selected_turbine]

        # 添加一个按钮来执行create_dataframe函数
        if st.button("执行预测"):
            # 检查参数输入是否合规
            if start_date and end_date and feature and turbineID:
                # 根据数据库查询函数返回的数据创建一个DataFrame
                df = create_dataframe(start_date, end_date, feature, turbineID)
                df_list = pd.DataFrame(df)
                with col2:
                    st.title('# 当前功率排名及预测')
                    # 创建一个表格来显示DataFrame的数据
                    ag1 = st_aggrid.AgGrid(
                        df_list,
                        editable=False,
                        sortable=False,
                        filter=False,
                        resizable=False,
                        defaultWidth=200,
                        fit_columns_on_grid_load=True,
                        height=800,
                    )
            else:
                st.error("请填写所有参数并确保日期格式正确。")

            # 绘制折线图
            fig_2 = px.line(df, x='DATATIME', y=feature)
            fig_2.update_layout(width=1300, height=600, margin=dict(l=50, r=50, b=50, t=50, pad=4))
            with col1:
                st.plotly_chart(fig_2)

