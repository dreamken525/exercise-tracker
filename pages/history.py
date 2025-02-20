import streamlit as st
import json
from datetime import datetime, timedelta, date
import plotly.graph_objects as go
import pandas as pd
import os
import calendar
from dateutil.relativedelta import relativedelta
import time

# 設置頁面配置
st.set_page_config(
    page_title="運動記錄歷史",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 完全重寫CSS樣式
st.markdown("""
<style>
    /* 重置所有Streamlit默認樣式 */
    #root > div:first-child {
        padding: 0 !important;
    }
    
    .main {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
    }
    
    section[data-testid="stSidebar"] {
        width: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* 移除所有頂部元素 */
    header[data-testid="stHeader"],
    .stDeployButton,
    .stToolbar,
    .stDecoration,
    div[data-testid="stToolbar"],
    div[data-testid="stDecoration"],
    div[data-baseweb="tab-list"],
    div[role="tablist"] {
        display: none !important;
    }

    /* 移除所有可能的頂部間距 */
    .element-container:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    .stApp {
        margin: 0 !important;
        padding: 0 !important;
    }

    div[data-testid="stAppViewContainer"] > div:first-child {
        margin: 0 !important;
        padding: 0 !important;
    }

    div[data-testid="stAppViewContainer"] {
        margin: 0 !important;
        padding: 0 !important;
    }

    div[data-testid="stVerticalBlock"] {
        gap: 0 !important;
        padding-top: 0 !important;
    }
    
    /* 主要內容樣式 */
    .main-content {
        padding: 1rem;
        margin: 0;
        width: 100%;
    }
    
    .calendar-container {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    
    .month-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    
    .month-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2E7D32;
    }
    
    .calendar-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 8px;
        margin-top: 10px;
    }
    
    .weekday-header {
        text-align: center;
        padding: 8px;
        font-weight: bold;
        color: #666;
        font-size: 0.9rem;
    }
    
    .calendar-day {
        background: white;
        border: 1px solid #eee;
        border-radius: 8px;
        padding: 8px;
        min-height: 80px;
        position: relative;
        display: flex;
        flex-direction: column;
    }
    
    .calendar-day.other-month {
        background: #f8f8f8;
    }
    
    .calendar-day.today {
        border: 2px solid #4CAF50;
    }
    
    .day-number {
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 4px;
        text-align: right;
    }
    
    .sets-display {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
    }
    
    .sets-number {
        font-size: 1.1rem;
        font-weight: bold;
        text-align: center;
    }
    
    .sets-number.zero {
        color: #CCCCCC;
        font-size: 0.8rem;
        font-weight: normal;
    }
    
    .sets-number.light {
        color: #00BCD4;
    }
    
    .sets-number.medium {
        color: #009688;
    }
    
    .sets-number.heavy {
        color: #FF9800;
    }
    
    .sets-number.intense {
        color: #F44336;
    }
    
    .edit-button {
        position: absolute;
        top: 4px;
        right: 4px;
        padding: 2px 6px;
        font-size: 0.8rem;
        color: #999;
        background: none;
        border: none;
        cursor: pointer;
        transition: color 0.3s;
    }
    
    .edit-button:hover {
        color: #666;
    }
    
    .edit-form {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 15px rgba(0,0,0,0.2);
        z-index: 1000;
        width: 90%;
    }
    
    .stats-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        margin-top: 20px;
        padding: 20px;
        background: white;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .stat-card {
        text-align: center;
        padding: 15px;
        border-radius: 8px;
        background: #f8f8f8;
    }
    
    .stat-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2E7D32;
        margin: 5px 0;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

def load_data():
    if os.path.exists("data/exercise_data.json"):
        with open("data/exercise_data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_data(data):
    # 重新計算總組數
    total_sets = 0
    for record in data["history"]:
        total_sets += record["sets"]
    data["sets"] = total_sets
    
    # 保存數據
    with open("data/exercise_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    time.sleep(0.2)  # 確保文件寫入完成

# 初始化session state
if 'editing_date' not in st.session_state:
    st.session_state.editing_date = None

data = load_data()

if data:
    # 初始化或獲取當前顯示的月份
    if 'current_month' not in st.session_state:
        st.session_state.current_month = datetime.now().date().replace(day=1)
    
    # 月份導航和標題
    st.markdown('<div class="calendar-container">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("◀ 上個月"):
            st.session_state.current_month -= relativedelta(months=1)
            st.session_state.editing_date = None
            st.rerun()
    
    with col2:
        st.markdown(f'<div class="month-title" style="text-align: center;">{st.session_state.current_month.strftime("%Y年%m月")}</div>', unsafe_allow_html=True)
    
    with col3:
        if st.button("下個月 ▶"):
            st.session_state.current_month += relativedelta(months=1)
            st.session_state.editing_date = None
            st.rerun()
    
    # 顯示星期標題
    weekdays = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]
    cols = st.columns(7)
    for i, col in enumerate(cols):
        with col:
            st.markdown(f'<div class="weekday-header">{weekdays[i]}</div>', unsafe_allow_html=True)
    
    # 獲取月曆數據
    current_month = st.session_state.current_month
    first_day = current_month
    last_day = (current_month + relativedelta(months=1, days=-1))
    first_weekday = first_day.weekday()
    calendar_start = first_day - timedelta(days=first_weekday)
    
    # 創建日期網格
    dates = []
    current_date = calendar_start
    while current_date <= last_day or len(dates) < 35:
        dates.append(current_date)
        current_date += timedelta(days=1)
    
    # 創建每週的行
    for week_start in range(0, len(dates), 7):
        week_dates = dates[week_start:week_start + 7]
        cols = st.columns(7)
        
        for i, day in enumerate(week_dates):
            with cols[i]:
                # 計算當天運動組數
                day_sets = 0
                for record in data["history"]:
                    record_date = datetime.fromisoformat(record["timestamp"]).date()
                    if record_date == day:
                        day_sets += record["sets"]
                
                # 設置日期格子的類別
                classes = ["calendar-day"]
                if day.month != current_month.month:
                    classes.append("other-month")
                if day == datetime.now().date():
                    classes.append("today")
                
                # 創建日期格子
                st.markdown(f'''
                <div class="{' '.join(classes)}">
                    <div class="day-number">{day.day}</div>
                    <div class="sets-display">
                        <div class="sets-number {'zero' if day_sets == 0 else
                                              'light' if day_sets <= 3 else
                                              'medium' if day_sets <= 6 else
                                              'heavy' if day_sets <= 10 else
                                              'intense'}">
                            {f"{day_sets:.1f}組" if day_sets > 0 else "0組"}
                        </div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
                # 編輯按鈕
                if day.month == current_month.month:
                    if st.button("⋮", key=f"edit_{day.strftime('%Y%m%d')}"):
                        st.session_state.editing_date = day
                
                # 編輯表單
                if st.session_state.editing_date == day:
                    with st.form(key=f"edit_form_{day.strftime('%Y%m%d')}"):
                        new_sets = st.number_input(
                            "運動組數",
                            min_value=0.0,
                            value=float(day_sets),
                            step=0.5
                        )
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("保存"):
                                # 刪除原有記錄
                                data["history"] = [
                                    record for record in data["history"]
                                    if datetime.fromisoformat(record["timestamp"]).date() != day
                                ]
                                
                                # 添加新記錄
                                if new_sets > 0:
                                    current_time = datetime.now().time()
                                    record_datetime = datetime.combine(day, current_time)
                                    data["history"].append({
                                        "timestamp": record_datetime.isoformat(),
                                        "sets": new_sets
                                    })
                                
                                save_data(data)
                                st.session_state.editing_date = None
                                st.rerun()
                        
                        with col2:
                            if st.form_submit_button("取消"):
                                st.session_state.editing_date = None
                                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 計算並顯示月度統計
    month_sets = 0
    exercise_days = set()
    for record in data["history"]:
        record_date = datetime.fromisoformat(record["timestamp"]).date()
        if record_date.year == current_month.year and record_date.month == current_month.month:
            month_sets += record["sets"]
            exercise_days.add(record_date)
    
    avg_sets = month_sets / len(exercise_days) if exercise_days else 0
    
    st.markdown('''
    <div class="stats-container">
        <div class="stat-card">
            <div class="stat-label">本月運動總組數</div>
            <div class="stat-value">{:.1f} 組</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">本月運動天數</div>
            <div class="stat-value">{} 天</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">平均每天組數</div>
            <div class="stat-value">{:.1f} 組</div>
        </div>
    </div>
    '''.format(month_sets, len(exercise_days), avg_sets), unsafe_allow_html=True)

else:
    st.error("無法讀取運動記錄數據") 