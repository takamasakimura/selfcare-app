import streamlit as st
import base64

def display_base64_gif(file_path, width=600):
    """Base64エンコードされたGIFを画面に表示する"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            base64_gif = f.read().replace("\n", "")
        st.markdown(
            f"""
            <img src="data:image/gif;base64,{base64_gif}" width="{width}" />
            """,
            unsafe_allow_html=True,
        )
    except Exception as e:
        st.error("GIFの表示に失敗しました")
        st.exception(e)

def encode_gif_to_base64(gif_path, output_txt_path):
    """ローカルGIFファイルをBase64に変換してテキストで保存"""
    try:
        with open(gif_path, "rb") as gif_file:
            encoded = base64.b64encode(gif_file.read()).decode("utf-8")
        with open(output_txt_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(encoded)
        print(f"✅ {output_txt_path} にエンコード済みデータを保存しました")
    except Exception as e:
        print("❌ Base64変換失敗:")
        print(e)

def validate_headers(sheet, expected_headers, header_row=1):
    """
    指定されたヘッダー行と `expected_headers` を比較し、完全一致しない場合は ValueError を出す
    """
    sheet_headers = sheet.row_values(header_row)
    if sheet_headers[:len(expected_headers)] != expected_headers:
        raise ValueError(
            f"Google Sheetsのヘッダーと定義が一致しません。\n"
            f"想定: {expected_headers}\n取得: {sheet_headers}"
        )