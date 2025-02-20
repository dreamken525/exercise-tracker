import streamlit as st
import json
from datetime import datetime
import pytz
import pandas as pd

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
    
    # 添加統計信息
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("總記錄數", len(data["history"]))
    with col2:
        st.metric("總組數", data["sets"])
    with col3:
        if data["history"]:
            earliest = min(r["timestamp"].split(".")[0].split("+")[0] for r in data["history"])
            latest = max(r["timestamp"].split(".")[0].split("+")[0] for r in data["history"])
            earliest_date = datetime.strptime(earliest.split("T")[0], "%Y-%m-%d")
            latest_date = datetime.strptime(latest.split("T")[0], "%Y-%m-%d")
            st.metric("記錄時間範圍", f"{(latest_date-earliest_date).days + 1} 天")
        else:
            st.metric("記錄時間範圍", "0 天")

    # 使用 expander 來隱藏詳細數據
    with st.expander("查看詳細數據"):
        st.json(data)
    
    # 處理並顯示記錄
    records_data = []
    for record in data["history"]:
        try:
            timestamp = record["timestamp"].split(".")[0]
            if "+" in timestamp:
                timestamp = timestamp.split("+")[0]
            records_data.append({
                "日期": timestamp.split("T")[0],
                "時間": timestamp.split("T")[1],
                "組數": record["sets"]
            })
        except Exception as e:
            continue

    if records_data:
        df = pd.DataFrame(records_data)
        # 每頁顯示10條記錄
        page_size = 10
        total_pages = len(df) // page_size + (1 if len(df) % page_size > 0 else 0)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            page = st.selectbox("選擇頁數", range(1, total_pages + 1)) - 1
        
        start_idx = page * page_size
        end_idx = min(start_idx + page_size, len(df))
        
        st.dataframe(df.iloc[start_idx:end_idx], use_container_width=True)
        st.caption(f"顯示第 {start_idx + 1} 到 {end_idx} 條記錄，共 {len(df)} 條")

except Exception as e:
    st.error(f"讀取數據時發生錯誤: {e}") 