# -*- coding: utf-8 -*-

import pandas as pd

def load_questions_from_csv(file_path="questions.csv"):
    """CSVファイルから質問データを読み込み、辞書のリスト形式で返す。"""
    try:
        df = pd.read_csv(file_path)
        # 'reverse'列が文字列として読み込まれる可能性があるので、boolに変換
        df['reverse'] = df['reverse'].apply(lambda x: str(x).strip().lower() == 'true')
        return df.to_dict('records')
    except FileNotFoundError:
        # Fallback for safety, though the file should exist.
        return []

# 質問データをロード
questions_data = load_questions_from_csv()

# 評価尺度の定義はそのまま残す
scales = {
    "量的負担": ["A1", "A2", "A3"],
    "質的負担": ["A4", "A5", "A6", "A7"],
    "裁量権": ["A8", "A9", "A10"],
    "仕事の適性": ["A11", "A16"],
    "職場人間関係": ["A12", "A13", "A14"],
    "職場環境": ["A15"],
    "働きがい": ["A17"],
    "活気": ["B1", "B2", "B3"],
    "イライラ感": ["B4", "B5", "B6"],
    "疲労感": ["B7", "B8", "B9"],
    "不安感": ["B10", "B11", "B12"],
    "抑うつ感": ["B13", "B14", "B15", "B16", "B17", "B18"],
    "身体愁訴": ["B19", "B20", "B21", "B22", "B23", "B24", "B25", "B26", "B27", "B28", "B29"],
    "上司のサポート": ["C1", "C4", "C7"],
    "同僚のサポート": ["C2", "C5", "C8"],
    "家族・友人のサポート": ["C3", "C6", "C9"],
    "仕事満足度": ["D1"],
    "家庭満足度": ["D2"],
}