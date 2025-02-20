import streamlit as st
import json
import random
from datetime import datetime, timedelta
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import pytz

# 設置頁面和主題
st.set_page_config(
    page_title="運動紀錄器",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自定義CSS樣式
st.markdown("""
<style>
    .stButton > button {
        background: linear-gradient(45deg, #2E7D32, #4CAF50);
        color: white;
        border: none;
        padding: 0.8rem 1.5rem;
        border-radius: 10px;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .metric-card {
        background: white;
        padding: 0.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin: 0.3rem 0;
    }
    .metric-card h4 {
        font-size: 0.9rem;
        margin: 0;
        color: #666;
    }
    .progress-bar-container {
        margin: 0.5rem 0;
    }
    .success-message {
        padding: 0.8rem;
        border-radius: 10px;
        background: linear-gradient(45deg, #43A047, #66BB6A);
        color: white;
        animation: fadeIn 0.5s ease-in;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .header-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
    }
    .header-title {
        margin: 0;
        font-size: 2.5rem;
    }
    .header-stats {
        font-size: 1.5rem;
        color: #2E7D32;
        margin: 0;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 重新组织鼓励语句,添加更多分类和场景
ENCOURAGEMENTS = {
    "normal": [  # 普通鼓励
        {
            "text": "今天也元氣滿滿呢 (๑>ᴗ<๑)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "這一組也完美達成！(๑•̀ᄇ•́)و ✧",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "筋肉君大滿足！(≧∇≦)/",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "今天的努力閃閃發光✨",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "突破極限啦！٩(ˊᗜˋ*)و",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "運動能量全開！( •̀ᄇ• ́)ﻭ✧",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "汗水是鑽石呢～💎",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "超強續航力認證！(๑•̀ㅂ•́)و✧",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "運動小精靈附體！(∩^o^)⊃━☆",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "燃燒吧小宇宙！(๑•̀ㅁ•́ฅ)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "今天的你比昨天更強了！(ง •̀_•́)ง",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "運動魔法生效中～(ﾉ>ω<)ﾉ",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "完美姿勢達成！(๑¯∀¯๑)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "肌肉在說謝謝你喔～(◍•ᴗ•◍)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "耐力全開模式ON！(๑•̀ᄇ•́)و",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "運動完的你好耀眼！(✧ᴥ✧)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "自律就是超能力！(๑•̀ω•́)ノ",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "又向目標邁進一大步！( • ̀ω•́ )✧",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "今天的汗水是明天的笑容～(๑´ڡ`๑)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "運動完的成就感最棒了！(๑˃̵ᴗ˂̵)ﻭ",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "堅持的樣子最帥氣！(๑•̀ω•́)ゞ",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "突破自我新紀錄！(≧ω≦)/",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "運動小達人就是你！(๑•̀ᄇ•́)و ✧",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "每滴汗水都不會白流～(๑•̀ㅂ•́)و",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "今天的你值得掌聲！(拍拍手👏)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "哼..才不是特地誇你呢！(¬‿¬)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "勉強給你個及格分啦～(￣へ￣)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "這種程度..還、還差得遠呢！(＞﹏＜)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "才沒有擔心你會偷懶呢！(´-ω-`)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "做..做得好什麼的..才沒那麼想！(⁄ ⁄•⁄ω⁄•⁄ ⁄)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "繼續保持啦..別讓我失望喔！(◔_◔)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "哼～也就比昨天好一點點而已！(￣^￣)ゞ",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "才不是為你加油呢！(╯▽╰ )",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "這種程度..馬馬虎虎啦～(¬_¬ )",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "別得意忘形了！( ˘•ω•˘ )",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "勉強承認你今天還算努力～(￣ε￣＠)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "我才沒在關注你的進度呢！(♯｀∧´)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "哼..還算沒偷懶嘛～(⌒▽⌒)☆",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "才..才沒有覺得你很厲害！(///ˊㅿˋ///)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "這種程度是應該的吧！(๑•̀ㅂ•́)و",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "別以為我會誇你喔！(´-ω-`=)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "只是剛好達標而已！( ￣ ￣)σ",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "我才沒期待你明天表現呢！(＞＜;)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "哼～還差得遠呢笨蛋！(｀ε´)ﾉ",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "才沒有想督促你運動呢！(´；д；`)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "這種進度..還算可以啦～( ̄▽ ̄;)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "別讓我重複第二遍！繼續加油！(｀Д´)ﾉ",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "才不是想讓你休息呢！(´д⊂)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "勉強給你蓋個合格章啦～(￣∇￣)ゞ",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "寶貝今天的努力我都看見了～繼續保持喔！(๑´ㅂ`๑)♡",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "親愛的好厲害！又離目標更近一步了呢～(≧ω≦)人",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "哇～肌肉線條越來越漂亮了！(✪ω✪)摸摸頭獎勵～",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "認真的樣子超級帥氣！忍不住偷拍下來了～(偷偷舉手機)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "這個動作做得好標準！教練級別了呢～(๑¯∀¯๑)✧",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "流汗的樣子也好有魅力...啊、才不是誇你呢！(⁄ ⁄•⁄ω⁄•⁄ ⁄)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "進步超明顯的！要給寶貝按摩獎勵嗎？(伸手捏肩)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "剛剛那組超性感的！再多做幾組給我看嘛～(拽衣角)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "肌肉君說它今天吃得好飽呢～(戳戳手臂)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "今天的寶貝是滿分男友力爆發！(塞毛巾擦汗)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "呼吸聲好犯規...耳朵要懷孕了啦！(摀臉偷看)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "背肌線條美得像藝術品～(拿手指偷偷描繪)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "這個重量也太厲害了！我家寶貝最棒了～(轉圈撒花)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "汗水在燈光下閃閃發亮的樣子...超迷人的！(✧Д✧)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "核心超穩的！可以當人體旗桿了啦～(๑•̀ᄇ•́)و",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "舉鐵的聲音聽起來超安心～寶貝在身邊真好(蹭蹭)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "又突破自己了！要親親獎勵嗎？(踮起腳尖)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "運動後的沐浴香氣...最喜歡這個味道了～(深呼吸)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "手臂青筋好性感...可以借我靠一下嗎？(悄悄貼近)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "寶貝的毅力是最讓我心動的地方～(捧臉)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "這個爆發力！簡直像漫畫男主角～(雙眼冒愛心)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "肌肉充血的样子好可口...啊、我什麼都沒說！(慌張)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "運動服都被撐得好有型～下次買新衣服獎勵你！(量尺寸)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "呼吸節奏掌控得超專業！可以當ASMR聽了～(戴耳機)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "腰腹力量越來越好了～公主抱轉圈圈沒問題吧？(伸手)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "寶貝的運動規劃好周密！超有安全感的～(埋胸)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "青筋和汗水的組合...是故意讓我心跳加速嗎？(捂胸口)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "訓練時認真的側臉...看入迷了怎麼辦～(臉紅)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "這個肌肉控制力！可以去拍健身教學影片了啦～(架攝影機)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "寶貝今天的能量滿到溢出來了！分我一點嘛～(充電狀)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "運動後泛紅的皮膚...像剛出爐的鬆餅一樣誘人～(咬唇)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "深蹲的姿勢完美！臀部線條又升級了～(鼻血警報)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "寶貝流的每滴汗都變成鑽石了喔～(收集ing)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "喘息聲犯規！耳機都要融化了啦～(///▽///)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "青筋跳動的樣子好迷人...可以摸一下嗎？(伸手指)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "今天的寶貝是巧克力味的～(嗅嗅)努力的味道最香了！",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "肌肉震顫的樣子好藝術！可以畫下來當頭貼嗎？(拿畫板)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "寶貝的運動日記寫得好認真！幫你擦汗獎勵～(拿手帕)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "這個重量提升速度...是要變成超級賽亞人嗎？(測戰鬥力)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "運動後的擁抱最溫暖了～(張開雙手)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "寶貝的自律能力簡直是魔法！被深深吸引了～(抱緊)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "訓練計劃執行得好徹底！果然是值得信賴的人～(蹭)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "肌肉纖維在說話呢～「謝謝主人今天的照顧」！(翻譯腔)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "寶貝的運動節奏像舞蹈一樣優美～(轉圈跟上)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "這個肌肉充血度！簡直是行走的荷爾蒙～(扇風降溫)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "訓練痕跡越來越明顯了！可以當我的私人教練嗎？(舉手)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "寶貝專注的樣子...讓人好想使壞打擾你～(戳腰窩)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "運動後的傻笑最可愛了～像得到肉骨頭的大狗狗！(摸頭)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "今天的努力值轉換成親密度+100%喔～(愛心量表)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "寶貝的健身成果...讓人好有安全感～(環抱測圍度)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "肌肉君說它今天很開心！要給它晚安吻嗎？(啾)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "運動後的寶貝閃閃發亮～像剛打磨好的寶劍！(擦拭)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "這個進步速度...要準備特大號獎盃了！(訂製中)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "寶貝的健身熱情...把我也傳染了！一起加油～(舉啞鈴)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "今天的你，比昨天更令我心動了～(捧心)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "肌肉在月光下起伏的樣子...簡直是藝術品！(架畫架)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "寶貝的運動精神...是最棒的安眠藥～(靠肩睡)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "再來一組吧！我在終點線等你喔～(張開毛巾)",
            "weight": 1,
            "last_shown": None
        }
    ],
    "streak": [  # 连续运动相关
        {
            "text": "連續運動真是太棒了！(๑>ᴗ<๑)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "堅持的樣子最帥氣！(๑•̀ω•́)ゞ",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "連勝達成！你就是運動王者！👑",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "堅持就是勝利，繼續保持！(ง •̀_•́)ง",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "運動等級提升！解鎖新成就！✨",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "連續運動中...戰鬥力持續上升！💪",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "這份毅力真是讓人佩服！(｀・ω・´)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "運動魂在燃燒！٩(๑•̀ω•́๑)۶",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "連續達標！你的表現超神啦！✨",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "堅持的力量無人能擋！(๑•̀ㅂ•́)و✧",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "運動高手就是你！繼續保持！💫",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "連續運動帶來的改變超讚的！(ﾉ>ω<)ﾉ",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "這股運動魄力無人能及！⚡",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "堅持運動的你閃閃發光！(★ω★)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "運動達人養成中...進度良好！📈",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "連續運動帶來超強氣場！(๑˃̵ᴗ˂̵)و",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "堅持的你就是最強的！💪✨",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "運動能量持續上升中！⚡️",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "這份堅持值得表揚！(｀・ω・´)ゞ",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "連續運動的你超有魅力！✨",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "運動等級突破新高峰！🏆",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "堅持運動的勇者就是你！⚔️",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "連續達標！實力持續提升！📈",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "運動之星就是你！閃耀登場！⭐",
            "weight": 1,
            "last_shown": None
        }
    ],
    "milestone": [  # 里程碑达成
        {
            "text": "🎉 恭喜達成連續運動30天！(≧∇≦)/",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "🏆 100天堅持達成！你是我的榜樣！(๑˃̵ᴗ˂̵)و",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "🌟 50天里程碑達成！你太厲害了！(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "🎊 200天堅持紀錄！這就是傳說！(≧∀≦)",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "💫 連續運動150天！你就是運動之神！(๑•̀ㅂ•́)و✧",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "🌈 300天里程碑！你的毅力無人能及！(ﾉ>ω<)ﾉ",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "⭐️ 80天目標達成！你的努力值得表揚！(◕‿◕✿)",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "🎯 250天堅持！這就是實力的證明！(๑˃ᴗ˂)ﻭ",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "🏅 120天里程碑解鎖！你太強了！(≧◡≦)",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "🌟 180天持續運動！這就是傳說中的毅力！(◍•ᴗ•◍)✧*。",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "🎊 400天超級成就！你就是運動界的傳奇！(≧∇≦)ﾉ",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "💪 70天目標達成！你的進步有目共睹！(｀・ω・´)",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "🌈 220天堅持紀錄！這就是王者風範！(๑•̀ㅂ•́)و✧",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "🏆 160天里程碑！你的毅力令人欽佩！(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "⚡️ 90天持續達標！你就是運動達人！(◕‿◕✿)",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "🎯 280天驚人紀錄！這就是堅持的力量！(๑˃ᴗ˂)ﻭ",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "🌟 140天目標達成！你的努力值得讚賞！(≧◡≦)",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "🎊 350天超級里程碑！你就是運動界的傳說！(◍•ᴗ•◍)✧*。",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "💫 60天持續進步！你的表現令人驚嘆！(｀・ω・´)",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "🏅 450天終極成就！你就是運動界的神話！(≧∇≦)ﾉ",
            "weight": 2,
            "last_shown": None
        }
    ],
    "record": [  # 突破记录
        {
            "text": "⚡ 新紀錄誕生！前所未有的突破！(╯✧▽✧)╯",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "🌟 這是你的新巔峰！繼續挑戰極限！(๑•̀ㅂ•́)و✧",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "💥 突破極限！你的潛力無限！(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "🚀 新高度達成！你就是傳說！(≧∇≦)/",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "⭐️ 記錄再更新！無人能擋！(๑•̀ω•́)ゞ",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "💪 超越自我！這就是實力！(ง •̀_•́)ง",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "🌈 新紀錄！你的光芒無人能及！(◕‿◕✿)",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "⚡️ 突破成功！你就是最強！(๑˃ᴗ˂)ﻭ",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "🎯 新高峰！你的潛力無窮！(≧◡≦)",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "💫 記錄刷新！這就是王者實力！(◍•ᴗ•◍)✧*。",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "🔥 極限突破！你就是傳說中的存在！(≧∇≦)ﾉ",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "⚔️ 新境界達成！無人能及！(｀・ω・´)",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "🌟 記錄之王誕生！這就是你的實力！(๑•̀ㅂ•́)و✧",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "💥 突破自我！創造傳奇！(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "🚀 新高度！你就是運動界的神話！(◕‿◕✿)",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "⭐️ 記錄更新！這就是王者風範！(๑˃ᴗ˂)ﻭ",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "💪 超越極限！你的實力無人能敵！(≧◡≦)",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "🌈 新紀錄！你就是運動界的傳說！(◍•ᴗ•◍)✧*。",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "⚡️ 突破成功！創造不可能！(≧∇≦)ﾉ",
            "weight": 2,
            "last_shown": None
        },
        {
            "text": "🎯 新巔峰！你就是最強王者！(｀・ω・´)",
            "weight": 2,
            "last_shown": None
        }
    ],
    "recovery": [  # 恢复期
        {
            "text": "慢慢來，保持良好節奏喔～(◍•ᴗ•◍)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "循序漸進最重要，繼續保持！(๑˃ᴗ˂)ﻭ",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "休息也是運動的一部分喔！(◕‿◕✿)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "調整好節奏，為下次努力做準備！(｀・ω・´)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "今天的休息是為了明天更好的表現！(◍•ᴗ•◍)✧*。",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "適當的休息能讓你變得更強！(๑•̀ㅂ•́)و✧",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "放鬆心情，享受運動的樂趣！(≧◡≦)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "調整好狀態，繼續向前進！(๑˃ᴗ˂)ﻭ",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "休息是為了走更長遠的路！(◕‿◕✿)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "保持良好的恢復節奏！(｀・ω・´)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "讓身體好好休息，明天再衝刺！(◍•ᴗ•◍)✧*。",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "調整步伐，找到最適合的節奏！(๑•̀ㅂ•́)و✧",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "休息也是實力的一部分！(≧◡≦)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "放鬆心情，享受運動的過程！(๑˃ᴗ˂)ﻭ",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "今天的調整是為了明天的進步！(◕‿◕✿)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "保持穩定的恢復節奏！(｀・ω・´)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "休息是為了更好的表現！(◍•ᴗ•◍)✧*。",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "調整好心態，繼續向前！(๑•̀ㅂ•́)و✧",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "享受恢復的過程！(≧◡≦)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "放鬆身心，為下次努力做準備！(๑˃ᴗ˂)ﻭ",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "像春風一樣溫柔地對待自己～(｡♥‿♥｡)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "休息時也要保持愉快的心情！╰(*´︶`*)╯",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "讓身心都得到充分的休息吧！(◍•ᴗ•◍)❤",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "溫柔地調整，穩健地前進！(◕‿◕✿)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "休息日也要保持好心情喔！(｡◕‿◕｡)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "今天就好好放鬆吧～(◠‿◠✿)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "用微笑面對每一天！ヾ(◍°∇°◍)ﾉﾞ",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "休息也是邁向成功的一步！(◍•ᴗ•◍)✧",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "保持平靜的心，繼續前進！(´｡• ᵕ •｡`)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "讓心靈和身體一起休息吧！(◕ᴗ◕✿)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "溫柔地照顧自己，靜待花開！(｡♥‿♥｡)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "休息是為了更好的自己！╰(⸝⸝⸝´꒳`⸝⸝⸝)╯",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "像陽光一樣溫暖地對待自己～(◍•ᴗ•◍)♡",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "保持愉快的心情，繼續加油！(◕‿◕✿)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "休息時也要充滿正能量！(｡◕‿◕｡)♡",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "讓每一天都充滿希望！(◍•ᴗ•◍)✧*。",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "溫柔地前進，堅定地成長！(◕ᴗ◕✿)",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "休息也是一種進步！ヾ(◍°∇°◍)ﾉﾞ",
            "weight": 1,
            "last_shown": None
        },
        {
            "text": "保持平和的心，繼續努力！(´｡• ᵕ •｡`)",
            "weight": 1,
            "last_shown": None
        }
    ],
    "overachievement": [  # 超额完成
        {
            "text": "🚀 超額完成！你的熱情無人能擋！(≧∇≦)ﾉ",
            "weight": 1.5,
            "last_shown": None
        },
        {
            "text": "💪 目標達成度爆表！繼續保持這股氣勢！(๑•̀ㅂ•́)و✧",
            "weight": 1.5,
            "last_shown": None
        },
        {
            "text": "⚡️ 超神表現！你就是運動界的超級賽亞人！(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧",
            "weight": 1.5,
            "last_shown": None
        },
        {
            "text": "🔥 目標完成度200%！這就是實力！(๑•̀ω•́)ゞ",
            "weight": 1.5,
            "last_shown": None
        },
        {
            "text": "💫 超額達標！你的能量超乎想像！(ง •̀_•́)ง",
            "weight": 1.5,
            "last_shown": None
        },
        {
            "text": "🌟 驚人的完成度！這就是王者實力！(◕‿◕✿)",
            "weight": 1.5,
            "last_shown": None
        },
        {
            "text": "⭐️ 目標達成度破表！無人能及！(๑˃ᴗ˂)ﻭ",
            "weight": 1.5,
            "last_shown": None
        },
        {
            "text": "💥 超額完成！你就是最強！(≧◡≦)",
            "weight": 1.5,
            "last_shown": None
        },
        {
            "text": "🎯 完美超標！這就是傳說的開始！(◍•ᴗ•◍)✧*。",
            "weight": 1.5,
            "last_shown": None
        },
        {
            "text": "🚀 目標完成度MAX！你的實力無人能擋！(≧∇≦)ﾉ",
            "weight": 1.5,
            "last_shown": None
        },
        {
            "text": "⚡️ 超神發揮！這就是極限的力量！(｀・ω・´)",
            "weight": 1.5,
            "last_shown": None
        },
        {
            "text": "💪 驚人的表現！你就是運動界的王者！(๑•̀ㅂ•́)و✧",
            "weight": 1.5,
            "last_shown": None
        },
        {
            "text": "🔥 超額達成！你的熱情燃燒一切！(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧",
            "weight": 1.5,
            "last_shown": None
        },
        {
            "text": "💫 目標完成度爆發！這就是真正的力量！(◕‿◕✿)",
            "weight": 1.5,
            "last_shown": None
        },
        {
            "text": "🌟 超神模式開啟！無人能擋！(๑˃ᴗ˂)ﻭ",
            "weight": 1.5,
            "last_shown": None
        },
        {
            "text": "⭐️ 驚人的超額完成！你就是傳說！(≧◡≦)",
            "weight": 1.5,
            "last_shown": None
        },
        {
            "text": "💥 目標達成度破紀錄！這就是王者風範！(◍•ᴗ•◍)✧*。",
            "weight": 1.5,
            "last_shown": None
        },
        {
            "text": "🎯 超額完成！你的實力無人能及！(≧∇≦)ﾉ",
            "weight": 1.5,
            "last_shown": None
        },
        {
            "text": "🚀 極限突破！這就是超越的力量！(｀・ω・´)",
            "weight": 1.5,
            "last_shown": None
        },
        {
            "text": "⚡️ 超神表現！你就是運動界的傳說！(๑•̀ㅂ•́)و✧",
            "weight": 1.5,
            "last_shown": None
        }
    ]
}

def analyze_performance(data, sets):
    """增强版的表现分析函数"""
    # 使用台灣時區
    tw_tz = pytz.timezone('Asia/Taipei')
    current_date = datetime.now(tw_tz).date()
    
    # 获取历史记录
    history = data["history"]
    dates = [datetime.fromisoformat(record["timestamp"]).replace(tzinfo=pytz.UTC).astimezone(tw_tz).date() 
            for record in history]
    dates.sort(reverse=True)
    
    # 分析连续运动
    streak_days = 0
    if dates:
        current_streak = 1
        for i in range(1, len(dates)):
            if (dates[i-1] - dates[i]).days == 1:
                current_streak += 1
            else:
                break
        streak_days = current_streak
    
    # 分析运动强度
    is_high_intensity = sets >= 1.5
    
    # 计算当日总运动量
    today_sets = sum(record["sets"] 
                    for record in history 
                    if datetime.fromisoformat(record["timestamp"]).replace(tzinfo=pytz.UTC).astimezone(tw_tz).date() == current_date)
    
    # 检查是否创造新纪录
    daily_records = {}
    for record in history:
        date = datetime.fromisoformat(record["timestamp"]).replace(tzinfo=pytz.UTC).astimezone(tw_tz).date()
        daily_records[date] = daily_records.get(date, 0) + record["sets"]
    
    previous_max = max(daily_records.values()) if daily_records else 0
    is_new_record = today_sets > previous_max
    
    # 检查是否达到里程碑
    milestones = [30, 50, 100, 200, 365]
    reached_milestone = None
    if streak_days in milestones:
        reached_milestone = streak_days
    
    # 检查是否处于恢复期
    if len(dates) >= 2:
        last_break = (dates[0] - dates[1]).days
        is_recovery = 3 <= last_break <= 7
    else:
        is_recovery = False
    
    # 检查超额完成情况
    daily_goal = data.get("daily_goal", 10)
    is_overachievement = today_sets >= daily_goal * 1.5
    
    # 根据分析结果选择最适合的鼓励类型
    if reached_milestone:
        return "milestone"
    elif is_new_record:
        return "record"
    elif is_recovery:
        return "recovery"
    elif is_overachievement:
        return "overachievement"
    elif streak_days > 1:
        return "streak"
    else:
        return "normal"

def get_smart_encouragement(data, sets):
    """增强版的智能鼓励选择函数"""
    encouragement_type = analyze_performance(data, sets)
    messages = ENCOURAGEMENTS[encouragement_type]
    
    # 使用台灣時區
    tw_tz = pytz.timezone('Asia/Taipei')
    current_time = datetime.now(tw_tz)
    
    # 過濾掉最近使用過的消息
    available_messages = [
        msg for msg in messages
        if msg["last_shown"] is None or 
        (current_time - datetime.fromisoformat(msg["last_shown"]).replace(tzinfo=pytz.UTC).astimezone(tw_tz)).total_seconds() > 3600
    ]
    
    # 如果没有可用消息,重置所有last_shown
    if not available_messages:
        available_messages = messages
        for msg in messages:
            msg["last_shown"] = None
    
    # 根据权重选择消息
    total_weight = sum(msg["weight"] for msg in available_messages)
    r = random.uniform(0, total_weight)
    
    selected_message = None
    cumulative_weight = 0
    for message in available_messages:
        cumulative_weight += message["weight"]
        if r <= cumulative_weight:
            selected_message = message
            break
    
    if selected_message is None:
        selected_message = available_messages[-1]
    
    # 更新最後顯示時間時使用台灣時區
    selected_message["last_shown"] = current_time.isoformat()
    
    return selected_message["text"]

# 確保數據目錄存在
os.makedirs("data", exist_ok=True)

# 添加文件修改時間檢查
def should_reload_data():
    """檢查是否需要重新加載數據"""
    if 'last_load_time' not in st.session_state:
        return True
    
    data_file = "data/exercise_data.json"
    if not os.path.exists(data_file):
        return True
    
    try:
        # 使用台灣時區比較時間
        tw_tz = pytz.timezone('Asia/Taipei')
        current_time = datetime.now(tw_tz).timestamp()
        return current_time > st.session_state.last_load_time
    except:
        return True

# 初始化或重新加載數據
def initialize_or_reload_data():
    if os.path.exists("data/exercise_data.json"):
        with open("data/exercise_data.json", "r", encoding="utf-8") as f:
            st.session_state.data = json.load(f)
            # 使用台灣時區記錄最後加載時間
            tw_tz = pytz.timezone('Asia/Taipei')
            st.session_state.last_load_time = datetime.now(tw_tz).timestamp()
    else:
        st.session_state.data = {
            "sets": 0,
            "daily_goal": 10,
            "weekly_goal": 50,
            "monthly_goal": 200,
            "yearly_goal": 2400,
            "history": []
        }
        with open("data/exercise_data.json", "w", encoding="utf-8") as f:
            json.dump(st.session_state.data, f, ensure_ascii=False, indent=4)
            # 使用台灣時區記錄最後加載時間
            tw_tz = pytz.timezone('Asia/Taipei')
            st.session_state.last_load_time = datetime.now(tw_tz).timestamp()

# 檢查是否需要重新加載數據
if 'data' not in st.session_state or should_reload_data():
    initialize_or_reload_data()

# 初始化鼓勵訊息狀態
if 'show_encouragement' not in st.session_state:
    st.session_state.show_encouragement = False
    st.session_state.encouragement_message = ""

def show_encouragement(message):
    st.session_state.show_encouragement = True
    st.session_state.encouragement_message = message

# 顯示鼓勵訊息
if st.session_state.show_encouragement:
    st.markdown(f'<div class="success-message">{st.session_state.encouragement_message}</div>', unsafe_allow_html=True)
    st.session_state.show_encouragement = False

def save_data():
    # 重新計算總組數
    total_sets = 0
    for record in st.session_state.data["history"]:
        total_sets += record["sets"]
    st.session_state.data["sets"] = total_sets
    
    # 保存數據
    with open("data/exercise_data.json", "w", encoding="utf-8") as f:
        json.dump(st.session_state.data, f, ensure_ascii=False, indent=4)
    
    # 強制更新最後加載時間，使用台灣時區
    tw_tz = pytz.timezone('Asia/Taipei')
    st.session_state.last_load_time = datetime.now(tw_tz).timestamp()

def get_period_sets(days):
    # 使用台灣時區
    tw_tz = pytz.timezone('Asia/Taipei')
    now = datetime.now(tw_tz).date()
    start_time = now - timedelta(days=days-1)  # 修改為包含當天
    total = 0
    for record in st.session_state.data["history"]:
        # 將時間戳轉換為台灣時間
        record_date = datetime.fromisoformat(record["timestamp"]).replace(tzinfo=pytz.UTC).astimezone(tw_tz).date()
        if record_date >= start_time and record_date <= now:
            total += record["sets"]
    return total

# 創建標題區域
st.markdown(f"""
<div class="header-container">
    <h1 class="header-title">🏋️ 運動紀錄器</h1>
    <h2 class="header-stats">總計完成組數: {st.session_state.data['sets']} 組</h2>
</div>
""", unsafe_allow_html=True)

# 使用卡片式設計顯示按鈕
col1, col2 = st.columns(2)
with col1:
    if st.button("完成半組! 💪", use_container_width=True):
        # 使用台灣時間
        tw_tz = pytz.timezone('Asia/Taipei')
        current_time = datetime.now(tw_tz)
        st.session_state.data["history"].append({
            "timestamp": current_time.isoformat(),
            "sets": 0.5
        })
        save_data()
        show_encouragement(get_smart_encouragement(st.session_state.data, 0.5))
        st.rerun()

with col2:
    if st.button("完成一組! 🔥", use_container_width=True):
        # 使用台灣時間
        tw_tz = pytz.timezone('Asia/Taipei')
        current_time = datetime.now(tw_tz)
        st.session_state.data["history"].append({
            "timestamp": current_time.isoformat(),
            "sets": 1
        })
        save_data()
        show_encouragement(get_smart_encouragement(st.session_state.data, 1))
        st.rerun()

# 顯示進度
col1, col2 = st.columns(2)

def create_progress_section(title, days, goal_key, column):
    sets = get_period_sets(days)
    goal = st.session_state.data[goal_key]
    
    with column:
        # 使用卡片式設計
        st.markdown(f"""
        <div class="metric-card">
            <h4>{title}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # 創建橫式進度條
        progress = sets/goal
        progress_percent = progress * 100  # 移除100%的限制
        
        # 使用bar chart代替gauge
        fig = go.Figure()
        
        # 添加背景條
        fig.add_trace(go.Bar(
            x=[100],
            y=[''],
            orientation='h',
            marker=dict(
                color='#E8F5E9',
                line=dict(width=0)
            ),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # 添加進度條
        bar_color = '#4CAF50' if progress_percent <= 100 else '#FF9800'  # 超過100%時改變顏色
        fig.add_trace(go.Bar(
            x=[min(progress_percent, 200)],  # 限制最大顯示200%
            y=[''],
            orientation='h',
            marker=dict(
                color=bar_color,
                line=dict(width=0)
            ),
            showlegend=False,
            text=f'{int(progress_percent)}%',  # 修改為整數顯示
            textposition='inside',
            textfont=dict(
                color='white',
                size=12
            )
        ))
        
        # 更新佈局
        fig.update_layout(
            height=60,
            barmode='overlay',
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showline=False,
                showticklabels=False,
                range=[0, 200]  # 擴大範圍到200%
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showline=False,
                showticklabels=False
            ),
            bargap=0
        )
        
        # 為每個圖表添加唯一的key
        st.plotly_chart(fig, use_container_width=True, key=f"progress_chart_{goal_key}")
        
        # 顯示詳細信息和目標設定
        metric_col, input_col = st.columns(2)
        with metric_col:
            metric_text = f"{sets:.1f}/{goal}組"
            if progress_percent > 100:
                metric_text += " 🎯"  # 超過100%時添加特殊標記
            st.metric("已完成/目標", 
                     value=sets,
                     delta=goal)
        
        with input_col:
            new_goal = st.number_input(
                "設定新目標",
                min_value=1,
                value=int(goal),
                key=goal_key,
                label_visibility="collapsed"
            )
            
            if new_goal != goal:
                st.session_state.data[goal_key] = new_goal
                save_data()
                st.rerun()

# 創建各時期進度區
create_progress_section("📅 今日進度", 1, "daily_goal", col1)
create_progress_section("📅 本週進度", 7, "weekly_goal", col2)
create_progress_section("📅 本月進度", 30, "monthly_goal", col1)
create_progress_section("📅 今年進度", 365, "yearly_goal", col2)

# 添加歷史記錄導航提示
st.markdown("---")
st.info("👉 點擊左側邊欄的「歷史記錄」查看詳細的運動歷史和統計數據") 