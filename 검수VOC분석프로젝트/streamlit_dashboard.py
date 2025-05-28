import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 환경 설정
st.set_page_config(layout="wide")
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

# 데이터 불러오기
@st.cache_data
def load_data():
    return pd.read_csv("./data/merged_voc_inspection_product.csv", encoding="utf-8-sig", parse_dates=["Date"])

df = load_data()

st.title("📊 VOC & 검수 데이터 대시보드")

# 사이드바 필터
with st.sidebar:
    st.header("📌 필터")
    brand_list = df["브랜드"].dropna().unique()
    selected_brand = st.multiselect("브랜드 선택", brand_list, default=list(brand_list))

    category_list = df["카테고리"].dropna().unique()
    selected_category = st.multiselect("카테고리 선택", category_list, default=list(category_list))

    date_range = st.date_input("날짜 범위 선택", value=(df["Date"].min(), df["Date"].max()))

# 필터 적용
filtered_df = df[
    (df["브랜드"].isin(selected_brand)) &
    (df["카테고리"].isin(selected_category)) &
    (df["Date"] >= pd.to_datetime(date_range[0])) &
    (df["Date"] <= pd.to_datetime(date_range[1]))
]

# KPI 영역
st.subheader("📈 주요 지표")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("VOC 총 건수", len(filtered_df))

with col2:
    fail_rate = (filtered_df["검수결과"] == "FAIL").mean()
    st.metric("검수 실패율", f"{fail_rate:.2%}")

with col3:
    voc_types = filtered_df["분류된유형"].value_counts()
    top_type = voc_types.idxmax() if not voc_types.empty else "없음"
    st.metric("가장 많이 발생한 VOC 유형", top_type)

# 차트 1: SKU별 VOC 건수
st.markdown("### 🧾 SKU별 VOC 건수")
sku_counts = filtered_df["SKU"].value_counts().head(5)
fig1, ax1 = plt.subplots(figsize=(6, 3))
sns.barplot(x=sku_counts.values, y=sku_counts.index, ax=ax1)
ax1.set_xlabel("VOC 건수")
ax1.set_ylabel("SKU")
st.pyplot(fig1)

# 차트 2: 브랜드별 검수 실패율
st.markdown("### ❌ 브랜드별 검수 실패율")
fail_by_brand = (
    filtered_df.groupby("브랜드")["검수결과"]
    .apply(lambda x: (x == "FAIL").mean())
    .sort_values(ascending=False)
    .head(5)
)

fig2, ax2 = plt.subplots(figsize=(6, 3))
sns.barplot(x=fail_by_brand.values, y=fail_by_brand.index, ax=ax2)
ax2.set_xlabel("검수 실패율")
ax2.set_ylabel("브랜드")
st.pyplot(fig2)

# 차트 3: VOC 유형별 월간 추이
st.markdown("### 📅 VOC 유형별 월간 추이")
if "분류된유형" in filtered_df.columns:
    trend = (
        filtered_df.groupby([filtered_df["Date"].dt.to_period("M"), "분류된유형"])
        .size()
        .unstack(fill_value=0)
    )
    trend.index = trend.index.to_timestamp()

    fig3, ax3 = plt.subplots(figsize=(10, 3))
    trend.plot(ax=ax3)
    ax3.set_xlabel("월")
    ax3.set_ylabel("건수")
    ax3.set_title("VOC 유형별 추이")
    ax3.legend(loc="upper left", bbox_to_anchor=(1, 1))
    st.pyplot(fig3)
