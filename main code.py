import streamlit as st
import pandas as pd
import time
import streamlit.components.v1 as components

# --- 1. アプリ全体の基本設定 ---
st.set_page_config(page_title="文化祭オリジナルクイズ", layout="centered")

# --- 2. クイズデータの設定 ---
QUESTIONS = [
    {"q": "本校が創立されたのは西暦何年？", "options": ["1985年", "1990年", "2000年", "2004年"], "ans": "2004年"},
    {"q": "情報の単位「1バイト」は何ビット？", "options": ["4ビット", "8ビット", "16ビット", "32ビット"], "ans": "8ビット"},
    {"q": "このアプリを動かしている言語は？", "options": ["Ruby", "Java", "Python", "C++"], "ans": "Python"}
]

# --- 3. 状態管理（セッションステート）の初期化 ---
if 'current_q' not in st.session_state:
    st.session_state.current_q = 0
    st.session_state.score = 0
    st.session_state.start_time = time.time()
    st.session_state.finished = False

# --- 4. JavaScriptコンポーネントの定義 ---
def inject_timer(start_timestamp):
    """右上に固定表示されるストップウォッチ"""
    # Pythonの開始時間をJSのミリ秒に変換して渡す
    js_start_time = int(start_timestamp * 1000)
    timer_html = f"""
    <div style="position: fixed; top: 15px; right: 15px; background: #f0f2f6; padding: 10px 20px; border-radius: 8px; font-size: 20px; font-weight: bold; z-index: 9999; box-shadow: 0 4px 6px rgba(0,0,0,0.1); color: #31333F;">
        ⏱️ <span id="time">00:00</span>
    </div>
    <script>
        let startTime = {js_start_time};
        setInterval(function() {{
            let elapsedTime = Math.floor((Date.now() - startTime) / 1000);
            let m = String(Math.floor(elapsedTime / 60)).padStart(2, '0');
            let s = String(elapsedTime % 60).padStart(2, '0');
            document.getElementById('time').innerText = m + ":" + s;
        }}, 1000);
    </script>
    """
    components.html(timer_html, height=0)

def inject_auto_reset():
    """30秒無操作で自動リロードする監視プログラム"""
    js_code = """
    <script>
        const parentWindow = window.parent;
        let inactivityTime = function () {{
            let time;
            function resetApp() {{ parentWindow.location.reload(); }}
            function resetTimer() {{
                clearTimeout(time);
                time = setTimeout(resetApp, 30000); // 30秒
            }}
            parentWindow.onload = resetTimer;
            parentWindow.document.onmousemove = resetTimer;
            parentWindow.document.onkeypress = resetTimer;
            parentWindow.document.onclick = resetTimer;
            parentWindow.document.ontouchstart = resetTimer;
        }};
        inactivityTime();
    </script>
    """
    components.html(js_code, height=0, width=0)

# --- 5. データベース関数（仮） ---
def load_ranking():
    return pd.DataFrame([
        {"名前": "ゲストA", "スコア": 3, "タイム": 12.5},
        {"名前": "ゲストB", "スコア": 2, "タイム": 15.0}
    ])

def save_score(name, score, time_taken):
    # ※後日、ここにGoogle Sheetsへの保存処理を追加します
    st.success(f"{name}さんの記録（{score}問正解 / {time_taken}秒）を仮登録しました！")

# ==========================================
# メインロジック（画面描画）
# ==========================================
st.title("💡 文化祭オリジナルクイズ")

# ゲーム終了後（結果とランキング画面）
if st.session_state.finished:
    # 無操作オートリセットを起動
    inject_auto_reset()
    
    st.header(f"🎉 結果発表: {st.session_state.score}問正解！")
    
    # 登録UI
    st.write("ランキングに登録しよう！")
    player_name = st.text_input("ニックネーム（最大6文字）", max_chars=6)
    
    if st.button("登録してランキングを見る", type="primary"):
        if player_name:
            time_taken = round(time.time() - st.session_state.start_time, 1)
            save_score(player_name, st.session_state.score, time_taken)
            
            st.subheader("🏆 現在のトップランキング")
            st.dataframe(load_ranking(), use_container_width=True)
            
            if st.button("最初の画面に戻る"):
                st.session_state.clear()
                st.rerun()
        else:
            st.warning("名前を入力してください。")

# クイズ出題中
else:
    # ストップウォッチを起動・表示
    inject_timer(st.session_state.start_time)
    
    # 現在の問題を取得
    q_data = QUESTIONS[st.session_state.current_q]
    
    st.subheader(f"第 {st.session_state.current_q + 1} 問 / 全 {len(QUESTIONS)} 問")
    st.markdown(f"### {q_data['q']}")
    
    # 選択肢ボタンの生成
    for option in q_data["options"]:
        if st.button(option, use_container_width=True):
            # 正解ならスコアを加算
            if option == q_data["ans"]:
                st.session_state.score += 1
            
            # 次の問題へ進む
            st.session_state.current_q += 1
            
            # 最終問題だった場合、終了フラグを立てる
            if st.session_state.current_q >= len(QUESTIONS):
                st.session_state.finished = True
            
            # 画面を再読み込みして更新
            st.rerun()