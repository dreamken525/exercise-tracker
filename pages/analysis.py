import streamlit as st
import json
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import os
from dateutil.relativedelta import relativedelta
import calendar
import numpy as np
from plotly.subplots import make_subplots

# 設置頁面配置
st.set_page_config(
    page_title="運動數據分析",
    page_icon="📊",
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
    
    /* 主要內容樣式 */
    .main-content {
        padding: 1rem;
        margin: 0;
        width: 100%;
    }
    
    .analysis-container {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    
    .section-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #2E7D32;
        margin-bottom: 15px;
    }
    
    .highlight-card {
        background: #f8f8f8;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
    }
    
    .highlight-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2E7D32;
        margin: 5px 0;
    }
    
    .highlight-label {
        font-size: 0.9rem;
        color: #666;
    }
    
    .insight-box {
        background: #E8F5E9;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    .insight-title {
        font-weight: bold;
        color: #2E7D32;
        margin-bottom: 5px;
    }
    
    .trend-up {
        color: #4CAF50;
    }
    
    .trend-down {
        color: #F44336;
    }
</style>
""", unsafe_allow_html=True)

def load_data():
    if os.path.exists("data/exercise_data.json"):
        with open("data/exercise_data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def get_exercise_df(data):
    records = []
    for record in data["history"]:
        date = datetime.fromisoformat(record["timestamp"]).date()
        records.append({
            "date": date,
            "year": date.year,
            "month": date.month,
            "week": date.isocalendar()[1],
            "weekday": date.weekday(),
            "sets": record["sets"]
        })
    df = pd.DataFrame(records)
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
    return df

data = load_data()

if data:
    df = get_exercise_df(data)
    
    st.markdown('<div class="section-title">📊 深度數據分析報告</div>', unsafe_allow_html=True)
    
    if not df.empty:
        # 1. 目標達成分析
        st.markdown('<div class="analysis-container">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🎯 目標達成分析</div>', unsafe_allow_html=True)
        
        # 計算各週期的目標達成率
        current_date = datetime.now().date()
        
        # 獲取當日數據
        today_sets = df[df['date'].dt.date == current_date]['sets'].sum()
        daily_goal = data.get('daily_goal', 10)
        daily_achievement = (today_sets / daily_goal) * 100
        
        # 獲取本週數據
        week_start = current_date - timedelta(days=current_date.weekday())
        week_sets = df[df['date'].dt.date >= week_start]['sets'].sum()
        weekly_goal = data.get('weekly_goal', 50)
        weekly_achievement = (week_sets / weekly_goal) * 100
        
        # 獲取本月數據
        month_start = current_date.replace(day=1)
        month_sets = df[df['date'].dt.date >= month_start]['sets'].sum()
        monthly_goal = data.get('monthly_goal', 200)
        monthly_achievement = (month_sets / monthly_goal) * 100
        
        # 顯示目標達成情況
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=daily_achievement,
                title={'text': "今日目標達成率"},
                gauge={'axis': {'range': [0, 150]},
                       'bar': {'color': "#4CAF50"},
                       'steps': [
                           {'range': [0, 60], 'color': "#FFCDD2"},
                           {'range': [60, 90], 'color': "#FFECB3"},
                           {'range': [90, 150], 'color': "#C8E6C9"}
                       ]}))
            fig.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=weekly_achievement,
                title={'text': "本週目標達成率"},
                gauge={'axis': {'range': [0, 150]},
                       'bar': {'color': "#4CAF50"},
                       'steps': [
                           {'range': [0, 60], 'color': "#FFCDD2"},
                           {'range': [60, 90], 'color': "#FFECB3"},
                           {'range': [90, 150], 'color': "#C8E6C9"}
                       ]}))
            fig.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=monthly_achievement,
                title={'text': "本月目標達成率"},
                gauge={'axis': {'range': [0, 150]},
                       'bar': {'color': "#4CAF50"},
                       'steps': [
                           {'range': [0, 60], 'color': "#FFCDD2"},
                           {'range': [60, 90], 'color': "#FFECB3"},
                           {'range': [90, 150], 'color': "#C8E6C9"}
                       ]}))
            fig.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig, use_container_width=True)
        
        # 目標達成趨勢分析
        achievement_insight = f"""
        ### 目標達成趨勢分析
        - 今日達成率: {daily_achievement:.1f}% ({'超額完成！' if daily_achievement > 100 else '需要加油！'})
        - 本週達成率: {weekly_achievement:.1f}% ({'進展順利！' if weekly_achievement >= 90 else '繼續努力！'})
        - 本月達成率: {monthly_achievement:.1f}% ({'表現優異！' if monthly_achievement >= 90 else '仍有進步空間！'})
        
        💡 建議：
        - {'保持目前的運動強度，你的表現很棒！' if daily_achievement >= 90 else '可以考慮增加每天的運動量，循序漸進地達到目標。'}
        - {'週度目標完成情況良好，繼續保持！' if weekly_achievement >= 90 else '建議合理分配每週運動量，避免集中在個別天數。'}
        - {'月度達標情況理想，這是一個好習慣！' if monthly_achievement >= 90 else '可以制定更詳細的月度運動計劃，幫助達成目標。'}
        """
        st.markdown(achievement_insight)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 2. 運動規律性分析
        st.markdown('<div class="analysis-container">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📅 運動規律性分析</div>', unsafe_allow_html=True)
        
        # 計算每週運動天數分布
        weekly_days = df.groupby(['year', 'week'])['date'].nunique()
        
        # 計算連續運動天數
        dates = sorted(df['date'].unique())
        max_streak = 1
        current_streak = 1
        
        for i in range(1, len(dates)):
            if (dates[i] - dates[i-1]).days == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        
        # 計算平均每週運動天數
        avg_weekly_days = weekly_days.mean()
        
        # 計算運動間隔的穩定性
        exercise_dates = pd.Series(dates)
        intervals = exercise_dates.diff().dt.days.dropna()
        interval_stability = intervals.std() if len(intervals) > 0 else 0
        
        # 顯示規律性指標
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('''
            <div class="highlight-card">
                <div class="highlight-label">最長連續運動天數</div>
                <div class="highlight-value">{}</div>
            </div>
            '''.format(max_streak), unsafe_allow_html=True)
        
        with col2:
            st.markdown('''
            <div class="highlight-card">
                <div class="highlight-label">平均每週運動天數</div>
                <div class="highlight-value">{:.1f}</div>
            </div>
            '''.format(avg_weekly_days), unsafe_allow_html=True)
        
        with col3:
            stability_score = max(0, 100 - (interval_stability * 10))
            st.markdown('''
            <div class="highlight-card">
                <div class="highlight-label">運動規律性評分</div>
                <div class="highlight-value">{:.0f}</div>
            </div>
            '''.format(stability_score), unsafe_allow_html=True)
        
        # 繪製每週運動天數分布
        fig = px.histogram(weekly_days, 
                        title='每週運動天數分布',
                        labels={'value': '運動天數', 'count': '週數'},
                        nbins=7)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # 規律性分析見解
        regularity_insight = f"""
        ### 運動規律性分析
        - 最長連續運動記錄：{max_streak}天
        - 平均每週運動：{avg_weekly_days:.1f}天
        - 規律性評分：{stability_score:.0f}分
        
        💡 規律性建議：
        - {'你的運動習慣非常穩定，繼續保持！' if stability_score >= 80 else '建議建立更規律的運動習慣。'}
        - {'連續運動天數表現優秀！' if max_streak >= 7 else '可以嘗試增加連續運動天數，培養習慣。'}
        - {'每週運動頻率達標！' if avg_weekly_days >= 4 else '建議增加每週運動次數，保持運動習慣。'}
        """
        st.markdown(regularity_insight)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 3. 強度分布分析
        st.markdown('<div class="analysis-container">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">💪 強度分布分析</div>', unsafe_allow_html=True)
        
        # 定義強度區間
        df['intensity'] = pd.cut(df['sets'], 
                                bins=[0, 3, 6, 10, float('inf')],
                                labels=['輕度 (1-3組)', '中度 (4-6組)', '重度 (7-10組)', '極限 (10組以上)'])
        
        # 計算強度分布
        intensity_dist = df['intensity'].value_counts()
        
        # 繪製強度分布圓餅圖
        fig = px.pie(values=intensity_dist.values, 
                    names=intensity_dist.index,
                    title='運動強度分布',
                    color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig, use_container_width=True)
        
        # 計算平均每次運動強度
        avg_sets = df['sets'].mean()
        max_sets = df['sets'].max()
        optimal_days = len(df[df['sets'].between(4, 10)])
        
        # 顯示強度指標
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('''
            <div class="highlight-card">
                <div class="highlight-label">平均每次運動強度</div>
                <div class="highlight-value">{:.1f}組</div>
            </div>
            '''.format(avg_sets), unsafe_allow_html=True)
        
        with col2:
            st.markdown('''
            <div class="highlight-card">
                <div class="highlight-label">最高運動強度</div>
                <div class="highlight-value">{:.1f}組</div>
            </div>
            '''.format(max_sets), unsafe_allow_html=True)
        
        with col3:
            st.markdown('''
            <div class="highlight-card">
                <div class="highlight-label">最佳強度天數</div>
                <div class="highlight-value">{}</div>
            </div>
            '''.format(optimal_days), unsafe_allow_html=True)
        
        # 強度分析見解
        intensity_insight = f"""
        ### 強度分布分析
        - 平均運動強度：{avg_sets:.1f}組
        - 最高紀錄：{max_sets:.1f}組
        - 最佳強度範圍（4-10組）天數：{optimal_days}天
        
        💡 強度建議：
        - {'目前的運動強度分配合理，繼續保持！' if 4 <= avg_sets <= 10 else '建議調整運動強度，保持在4-10組之間。'}
        - {'高強度訓練比例適中。' if intensity_dist.get('極限 (10組以上)', 0) <= len(df) * 0.2 else '注意避免過度訓練，適當安排恢復時間。'}
        - {'低強度訓練有助於恢復，繼續保持。' if intensity_dist.get('輕度 (1-3組)', 0) >= len(df) * 0.2 else '可以適當增加恢復性訓練的比例。'}
        """
        st.markdown(intensity_insight)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 4. 長期趨勢分析
        st.markdown('<div class="analysis-container">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📈 長期趨勢分析</div>', unsafe_allow_html=True)
        
        # 計算月度趨勢
        monthly_sets = df.groupby(['year', 'month'])['sets'].agg(['sum', 'count', 'mean']).reset_index()
        monthly_sets['date'] = pd.to_datetime(monthly_sets[['year', 'month']].assign(day=1))
        
        # 繪製月度趨勢圖
        fig = make_subplots(rows=2, cols=1,
                           subplot_titles=('月度總運動量趨勢', '月度平均強度趨勢'))
        
        fig.add_trace(
            go.Scatter(x=monthly_sets['date'], y=monthly_sets['sum'],
                      mode='lines+markers', name='總運動量'),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=monthly_sets['date'], y=monthly_sets['mean'],
                      mode='lines+markers', name='平均強度'),
            row=2, col=1
        )
        
        fig.update_layout(height=500, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
        
        # 計算趨勢指標
        if len(monthly_sets) >= 2:
            last_month = monthly_sets.iloc[-1]
            prev_month = monthly_sets.iloc[-2]
            
            total_change = ((last_month['sum'] - prev_month['sum']) / prev_month['sum'] * 100
                          if prev_month['sum'] > 0 else 0)
            
            intensity_change = ((last_month['mean'] - prev_month['mean']) / prev_month['mean'] * 100
                              if prev_month['mean'] > 0 else 0)
            
            # 顯示趨勢變化
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f'''
                <div class="highlight-card">
                    <div class="highlight-label">月度運動量變化</div>
                    <div class="highlight-value {'trend-up' if total_change > 0 else 'trend-down'}">
                        {total_change:+.1f}%
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col2:
                st.markdown(f'''
                <div class="highlight-card">
                    <div class="highlight-label">月度強度變化</div>
                    <div class="highlight-value {'trend-up' if intensity_change > 0 else 'trend-down'}">
                        {intensity_change:+.1f}%
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            
            # 趨勢分析見解
            trend_insight = f"""
            ### 長期趨勢分析
            - 月度運動量變化：{total_change:+.1f}%
            - 月度強度變化：{intensity_change:+.1f}%
            
            💡 趨勢建議：
            - {'運動量呈上升趨勢，繼續保持！' if total_change > 0 else '建議適當增加運動量。'}
            - {'運動強度提升合理，注意循序漸進。' if 0 <= intensity_change <= 10 else '注意控制強度提升的速度。' if intensity_change > 10 else '可以考慮適當提高運動強度。'}
            - {'整體發展趨勢良好！' if total_change > 0 and 0 <= intensity_change <= 10 else '建議根據身體狀況調整訓練計劃。'}
            """
            st.markdown(trend_insight)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    else:
        st.info("暫無運動記錄數據，開始記錄後即可查看詳細分析報告。")

else:
    st.error("無法讀取運動記錄數據") 