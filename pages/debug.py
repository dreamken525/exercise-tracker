import streamlit as st
import json
from datetime import datetime
import pytz

st.set_page_config(
    page_title="調試信息",
    page_icon="🔧",
    layout="wide"
)

# 設置頁面標題
st.title("🔧 調試信息")

# 讀取數據
try:
    with open("data/exercise_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # 顯示完整數據
    st.subheader("當前數據")
    st.json(data)
    
    # 顯示時間戳分析
    st.subheader("時間戳分析")
    tw_tz = pytz.timezone('Asia/Taipei')
    now = datetime.now(tw_tz)
    
    for record in data["history"]:
        col1, col2 = st.columns(2)
        with col1:
            st.write("原始時間戳:", record["timestamp"])
        with col2:
            try:
                record_time = datetime.strptime(record["timestamp"].split("+")[0], "%Y-%m-%dT%H:%M:%S")
                record_time = tw_tz.localize(record_time)
                st.write("解析後時間:", record_time)
            except Exception as e:
                st.error(f"時間戳解析錯誤: {e}")

    # 添加統計信息
    st.subheader("數據統計")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("總記錄數", len(data["history"]))
    
    with col2:
        st.metric("總組數", data["sets"])
    
    with col3:
        if data["history"]:
            earliest = min(datetime.strptime(r["timestamp"].split("+")[0], "%Y-%m-%dT%H:%M:%S") 
                         for r in data["history"])
            latest = max(datetime.strptime(r["timestamp"].split("+")[0], "%Y-%m-%dT%H:%M:%S") 
                        for r in data["history"])
            st.metric("記錄時間範圍", f"{(latest-earliest).days + 1} 天")
        else:
            st.metric("記錄時間範圍", "0 天")

except Exception as e:
    st.error(f"讀取數據時發生錯誤: {e}") 