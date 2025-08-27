"""
職業性ストレス簡易調査票（57項目版）のStreamlitアプリケーションです。

このアプリケーションは、ユーザーが57の質問に回答し、その結果に基づいて
ストレスレベルを評価・視覚化する機能を提供します。

機能一覧:
- 57項目の質問票
- 回答に基づくストレスレベルの自動計算
- 結果のヒートマップ表示
- ストレス要因、心身のストレス反応、周囲のサポートに関するグラフ表示
- 高ストレス状態の簡易判定
"""

import streamlit as st
import pandas as pd
import altair as alt
from data import questions_data, scales

# --- 定数定義 ---

# 回答の選択肢とスコア
OPTIONS = ["そうだ", "まあそうだ", "ややちがう", "ちがう"]
SCORE_MAP = {"そうだ": 4, "まあそうだ": 3, "ややちがう": 2, "ちがう": 1}
SCORE_MAP_REVERSE = {"そうだ": 1, "まあそうだ": 2, "ややちがう": 3, "ちがう": 4}

# 高ストレス判定のカテゴリ
STRESSOR_SCALES = ["量的負担", "質的負担", "裁量権", "仕事の適性", "職場人間関係", "職場環境"]
REACTION_SCALES = ["活気", "イライラ感", "疲労感", "不安感", "抑うつ感", "身体愁訴"]
SUPPORT_SCALES = ["上司のサポート", "同僚のサポート", "家族・友人のサポート"]

# グラフのカテゴリと色
CHART_DEFINITIONS = {
    "ストレス要因のバランス": {
        "scales": ["量的負担", "質的負担", "裁量権", "仕事の適性", "職場人間関係", "職場環境", "働きがい"],
        "colors": ["#1f77b4", "#3a8ac1", "#559dce", "#70b0db", "#8bc3e8", "#a6d6f5", "#c1e9ff"],
        "height": 300
    },
    "心身のストレス反応": {
        "scales": ["活気", "イライラ感", "疲労感", "不安感", "抑うつ感", "身体愁訴"],
        "colors": ["#d62728", "#e05757", "#ea7a7a", "#f49d9d", "#ffc0c0", "#ffe3e3"],
        "height": 250
    },
    "周囲からのサポート": {
        "scales": ["上司のサポート", "同僚のサポート", "家族・友人のサポート"],
        "colors": ["#2ca02c", "#55b355", "#7fca7f"],
        "height": 150
    }
}

# --- UI関連の関数 ---

def render_header():
    """アプリケーションのヘッダーと説明を表示します。"""
    st.title("職業性ストレス簡易調査票（57項目版）")
    st.write("ご自身のストレス状態をチェックしてみましょう。各質問について、最も当てはまるものを1つ選んでください。")
    st.info("注意：このツールはあくまでプロトタイプであり、医学的診断に代わるものではありません。")

def render_questionnaire():
    """質問票をページネーションで表示し、ユーザーの回答を収集します。"""
    QUESTIONS_PER_PAGE = 10
    
    # 現在のページに対応する質問を取得
    start_index = st.session_state.current_page * QUESTIONS_PER_PAGE
    end_index = start_index + QUESTIONS_PER_PAGE
    current_questions = questions_data[start_index:end_index]

    # 質問の表示と回答の収集
    for q in current_questions:
        st.markdown(f'<p class="question-text">{q["text"]}</p>', unsafe_allow_html=True)
        
        current_answer = st.session_state.answers.get(q["id"])
        try:
            default_index = OPTIONS.index(current_answer) if current_answer in OPTIONS else 0
        except ValueError:
            default_index = 0
        
        answer = st.radio(
            label="",
            options=OPTIONS,
            key=q["id"],
            horizontal=True,
            index=default_index
        )
        st.session_state.answers[q["id"]] = answer
        st.markdown("---")

def handle_navigation():
    """ページネーションのナビゲーションボタンを処理します。"""
    QUESTIONS_PER_PAGE = 10
    total_questions = len(questions_data)
    num_pages = (total_questions + QUESTIONS_PER_PAGE - 1) // QUESTIONS_PER_PAGE if total_questions > 0 else 1
    
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.session_state.current_page > 0:
            if st.button("⬅️ 前へ"):
                st.session_state.current_page -= 1
                st.rerun()

    with col3:
        if st.session_state.current_page < num_pages - 1:
            if st.button("次へ ➡️"):
                st.session_state.current_page += 1
                st.rerun()

    # 最後のページに「診断結果を見る」ボタンを表示
    if st.session_state.current_page == num_pages - 1:
        with col2:
            if st.button("診断結果を見る", type="primary"):
                if len(st.session_state.answers) != total_questions:
                    st.error("すべての質問に回答してください。")
                else:
                    scores = calculate_scores(st.session_state.answers)
                    scale_scores = calculate_scale_scores(scores)
                    st.session_state.results = {"scale_scores": scale_scores}
                    st.session_state.show_results = True
                    st.rerun()

# --- 計算関連の関数 ---

def calculate_scores(answers):
    """ユーザーの回答から各質問の素点を計算します。"""
    scores = {}
    for q in questions_data:
        answer = answers.get(q["id"])
        if answer:
            if q.get("reverse", False):
                scores[q["id"]] = SCORE_MAP_REVERSE[answer]
            else:
                scores[q["id"]] = SCORE_MAP[answer]
    return scores

def calculate_scale_scores(scores):
    """素点から各評価尺度の合計点を計算します。"""
    scale_scores = {}
    for scale_name, question_ids in scales.items():
        scale_scores[scale_name] = sum(scores.get(qid, 0) for qid in question_ids)
    return scale_scores

# --- 結果表示関連の関数 ---

def display_results():
    """診断結果全体を表示します。"""
    results = st.session_state.results
    scale_scores = results["scale_scores"]
    
    display_heatmap(scale_scores)
    display_high_stress_warning(scale_scores)
    display_charts(scale_scores)

    if st.button("最初からやり直す"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def display_heatmap(scale_scores):
    """結果をヒートマップ形式で表示します。"""
    st.header("診断結果ヒートマップ")
    st.write("各尺度のストレスレベルを色で示しています。赤に近いほどストレスが高い状態です。")
    
    max_scores = {name: len(ids) * 4 for name, ids in scales.items()}
    
    html_string = '<div class="heatmap-container">'
    for scale_name, score in scale_scores.items():
        max_score = max_scores.get(scale_name, score) 
        normalized_val = score / max_score if max_score > 0 else 0
        hue = 120 * (1 - normalized_val)
        font_color = 'black' if 50 < hue < 130 else 'white'
        html_string += (f'<div class="heatmap-tile" style="background-color: hsl({hue}, 85%, 55%); color: {font_color};">'
                        f'<div class="tile-scale-name">{scale_name}</div>'
                        f'<div class="tile-score">{score}</div>'
                        f'</div>')
    html_string += '</div>'
    st.markdown(html_string, unsafe_allow_html=True)

def display_high_stress_warning(scale_scores):
    """高ストレス状態の判定と警告を表示します。"""
    st.subheader("総合的なストレスレベルの評価")
    total_stressor = sum(scale_scores.get(s, 0) for s in STRESSOR_SCALES)
    total_reaction = sum(scale_scores.get(s, 0) for s in REACTION_SCALES)
    total_support = sum(scale_scores.get(s, 0) for s in SUPPORT_SCALES)

    is_high_stress = False
    if total_reaction >= 77:
        is_high_stress = True
        st.warning("高ストレス状態にある可能性が高いです。")
        st.write("心身のストレス反応の合計点数が高いレベルにあります。")

    if total_stressor >= 76 and total_support >= 36:
        if not is_high_stress:
            st.warning("高ストレス状態にある可能性が高いです。")
        is_high_stress = True
        st.write("仕事のストレス要因と、周囲のサポートの状況から、高いストレス状態にある可能性が考えられます。")

    if not is_high_stress:
        st.success("現在のところ、総合的なストレスレベルは標準の範囲内と考えられます。")
    st.info("この結果は、あくまで入力に基づく簡易的な評価です。気になる点があれば、専門家（医師、カウンセラーなど）にご相談ください。")

def display_charts(scale_scores):
    """3つのカテゴリについてグラフを表示します。"""
    for title, definition in CHART_DEFINITIONS.items():
        st.subheader(title)
        df = pd.DataFrame(
            [(s, scale_scores.get(s, 0)) for s in definition["scales"]],
            columns=['尺度', '点数']
        )
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('点数', title='合計点'),
            y=alt.Y('尺度', title='', sort=None),
            color=alt.Color('尺度', legend=None, scale=alt.Scale(range=definition["colors"]))
        ).properties(height=definition["height"])
        st.altair_chart(chart, use_container_width=True)

def apply_styling():
    """ページ全体に適用するカスタムCSSを定義します。"""
    st.markdown("""<style>
    .question-text { font-size: 1.1rem; font-weight: bold; margin-bottom: 10px; }
    div.row-widget.stRadio > div { flex-direction: row; justify-content: space-around; padding-top: 0px; }
    div.row-widget.stRadio > div > label { display: inline-block; padding: 8px 20px; border: 1px solid #ccc; border-radius: 25px; margin: 0 5px; transition: all 0.2s ease-in-out; cursor: pointer; background-color: #f8f9fa; }
    div.row-widget.stRadio > div > label:has(input:checked) { background-color: #28a745; color: white; border-color: #28a745; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    div.row-widget.stRadio > div > label:hover { background-color: #e9ecef; border-color: #adb5bd; }
    div.row-widget.stRadio > div > label > input { display: none; }
    .heatmap-container { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; margin-top: 20px; }
    .heatmap-tile { border-radius: 8px; padding: 15px; color: white; text-align: center; flex: 1 1 160px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); transition: transform 0.2s ease-in-out; display: flex; flex-direction: column; justify-content: center; min-height: 100px; }
    .heatmap-tile:hover { transform: scale(1.05); }
    .tile-scale-name { font-weight: bold; font-size: 1rem; margin-bottom: 8px; }
    .tile-score { font-size: 2.2rem; font-weight: bold; }
    </style>""", unsafe_allow_html=True)

# --- メイン処理 ---

def main():
    """アプリケーションのメイン実行関数。"""
    apply_styling()

    # セッション状態の初期化
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 0
    if 'answers' not in st.session_state:
        st.session_state.answers = {}
    if 'show_results' not in st.session_state:
        st.session_state.show_results = False

    # --- サイドバー ---
    st.sidebar.title("職業性ストレス簡易調査票")
    st.sidebar.write("ご自身のストレス状態をチェックしてみましょう。各質問について、最も当てはまるものを1つ選んでください。")
    st.sidebar.info("注意：このツールはあくまでプロトタイプであり、医学的診断に代わるものではありません。")

    if not st.session_state.show_results:
        st.sidebar.markdown("---")
        st.sidebar.subheader("進捗")
        total_questions = len(questions_data)
        answered_count = len(st.session_state.answers)
        progress = answered_count / total_questions if total_questions > 0 else 0
        
        st.sidebar.progress(progress)
        st.sidebar.write(f"進捗: {answered_count} / {total_questions} 問")

    # --- メインコンテンツ ---
    if st.session_state.show_results:
        st.title("診断結果")
        display_results()
    else:
        # questions_dataが空でないことを確認
        if not questions_data:
            st.error("質問データを読み込めませんでした。questions.csvファイルを確認してください。")
            return
        
        render_questionnaire()
        handle_navigation()

if __name__ == "__main__":
    main()
