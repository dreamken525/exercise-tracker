# 運動紀錄器 Exercise Tracker

一個簡單但功能強大的運動紀錄應用程式，幫助您追蹤每日運動進度。

## 功能特點

- 記錄運動組數（半組/一組）
- 自動追蹤每日、每週、每月和年度進度
- 智能鼓勵系統，提供多樣化的鼓勵訊息
- 午夜自動重置每日組數
- 完整的歷史記錄
- 美觀的進度顯示界面

## 安裝說明

1. 克隆專案：
```bash
git clone https://github.com/[您的用戶名]/exercise-tracker.git
cd exercise-tracker
```

2. 安裝依賴：
```bash
pip install -r requirements.txt
```

3. 運行應用：
```bash
streamlit run app.py
```

## 使用方法

1. 完成運動後，點擊「完成半組」或「完成一組」按鈕記錄
2. 查看進度條了解當前進度
3. 系統會自動給予鼓勵訊息
4. 每天午夜會自動重置組數，但歷史記錄會保留

## 技術棧

- Python
- Streamlit
- Plotly
- PyTZ

## 貢獻指南

歡迎提交 Pull Request 或開 Issue 來改進專案。

## 授權協議

MIT License 