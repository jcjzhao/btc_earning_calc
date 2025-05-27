import streamlit as st
import requests

# --- Consistent font and compact line-style section divider ---
st.markdown(
    """
    <style>
    .stTextInput > label, .stNumberInput > label, .stSelectbox > label {
        font-size: 16px !important;
        font-weight: normal !important;
        line-height: 1.4 !important;
    }
    input, select, textarea {
        font-size: 16px !important;
        font-weight: normal !important;
        line-height: 1.4 !important;
    }
    .framed-section {
        border: none !important;
        border-bottom: 0.5px solid #eee !important;
        background-color: transparent !important;
        padding: 12px 0 2px 0;
        margin-bottom: 0.05em;
    }
    th, td {
        border: none !important;
        border-bottom: 1px solid #eee !important;
        padding: 4px !important;
        text-align: center !important;
        font-size: 16px !important;
        background-color: transparent !important;
    }
    th {
        font-weight: bold !important;
    }
    /* Further reduce space between KPI rows */
    .element-container .stMarkdown p {
        margin-bottom: 0.12em !important;
        margin-top: 0.12em !important;
    }
    .element-container .stMarkdown h3, 
    .element-container .stMarkdown h4, 
    .element-container .stMarkdown h5, 
    .element-container .stMarkdown h6 {
        margin-bottom: 0.1em !important;
        margin-top: 0.1em !important;
    }
    input[type="number"]::-webkit-inner-spin-button,
    input[type="number"]::-webkit-outer-spin-button {
        -webkit-appearance: none !important;
        margin: 0 !important;
        display: none !important;
    }
    input[type="number"] {
        -moz-appearance: textfield !important;
    }
    input[type="number"]::-ms-input-spinner {
        display: none !important;
    }
    .main .block-container {
        max-width: 420px;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    @media (max-width: 480px) {
        .main .block-container {
            max-width: 98vw;
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Title ---
st.markdown(
    """
    <h3 style="text-align: center;">比特币挖矿收益</h3>
    """,
    unsafe_allow_html=True
)

# --- System specs ---
systems = {
    "S19XP": {"hash_rate": 140, "power_consumption": 3010, "unit_price": 4315},
    "S21+": {"hash_rate": 216, "power_consumption": 3564, "unit_price": 3240},
    "S21XP": {"hash_rate": 270, "power_consumption": 3645, "unit_price": 5802},
    "S21 Pro": {"hash_rate": 234, "power_consumption": 3510, "unit_price": 3744}
}

# --- Real-time BTC price (fetch every run, but cache for 60s to avoid rate limit) ---
@st.cache_data(ttl=60)
def get_btc_price():
    try:
        resp = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", timeout=5)
        return resp.json()["bitcoin"]["usd"], ""
    except Exception:
        return 30000.0, "⚠️ 实时比特币价格获取失败，已使用默认值 $30,000"

@st.cache_data(ttl=60)
def get_network_hashrate():
    try:
        resp = requests.get("https://blockchain.info/q/hashrate", timeout=5)
        return resp.json() / 1e3, ""
    except Exception:
        return 350000.0, "⚠️ 实时全网算力获取失败，已使用默认值 350,000 TH/s"

real_time_btc_price, btc_price_warning = get_btc_price()
real_time_network_hash_rate, hashrate_warning = get_network_hashrate()

# --- Inputs (modern layout) ---
st.markdown('<div class="framed-section">', unsafe_allow_html=True)
st.markdown("##### 输入参数")
col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    system_choice = st.selectbox("矿机型号", options=list(systems.keys()))
with col2:
    num_systems = st.number_input("矿机数量", min_value=1, value=1, step=1, help="请输入正整数")
with col3:
    electricity_cost = st.number_input("电费($/kWh)", min_value=0.0, value=0.05, step=0.001, format="%.3f", help="每度电的价格")
with col4:
    management_charge_percent = st.number_input("管理费(%)", min_value=0.0, value=2.0, step=0.1, format="%.2f", help="年化管理费率 (%)")
with col5:
    annual_hashrate_growth = st.number_input("算力增长(%)", min_value=0.0, value=40.0, step=0.1, format="%.1f", help="全网算力年均增长率") / 100
with col6:
    annual_btc_price_growth = st.number_input("币价增长(%)", min_value=-100.0, value=10.0, step=0.1, format="%.1f", help="比特币价格年均增长率") / 100
st.markdown('</div>', unsafe_allow_html=True)

# --- Add a divider line for better visual separation ---
st.markdown('<hr style="margin-top: -0.2em; margin-bottom: 0.2em; border: 0; border-top: 1px solid #eee;">', unsafe_allow_html=True)

# --- Show real-time BTC price and network hashrate as read-only, using Streamlit's default code formatting ---
st.markdown(
    f"**比特币价格**: `${real_time_btc_price:,.2f}`  |  **全网算力**: `{real_time_network_hash_rate:,.2f} TH/s`"
)
if btc_price_warning:
    st.warning(btc_price_warning)
if hashrate_warning:
    st.warning(hashrate_warning)

# --- System config ---
selected_system = systems[system_choice]
hash_rate_per_system = selected_system["hash_rate"]
power_consumption_per_system = selected_system["power_consumption"]
unit_price_per_system = selected_system["unit_price"]
total_system_cost = num_systems * unit_price_per_system

# --- Calculation and Output ---
if st.button("计算收益"):
    try:
        final_btc_price = real_time_btc_price
        final_network_hash_rate = real_time_network_hash_rate

        total_hash_rate = num_systems * hash_rate_per_system
        block_reward = 3.125
        blocks_per_day = 144

        # Daily earnings with network hashrate and BTC price growth
        daily_btc_earnings_list = []
        daily_usd_earnings_list = []
        for day in range(365):
            network_hashrate_today = final_network_hash_rate * ((1 + annual_hashrate_growth) ** (day / 365))
            btc_per_th_today = (block_reward * blocks_per_day) / network_hashrate_today
            btc_earned_today = total_hash_rate * btc_per_th_today
            btc_price_today = final_btc_price * ((1 + annual_btc_price_growth) ** (day / 365))
            usd_earned_today = btc_earned_today * btc_price_today
            daily_btc_earnings_list.append(btc_earned_today)
            daily_usd_earnings_list.append(usd_earned_today)

        yearly_btc_earnings = sum(daily_btc_earnings_list)
        monthly_btc_earnings = sum(daily_btc_earnings_list[:30])
        daily_btc_earnings = daily_btc_earnings_list[0]

        yearly_usd_earnings = sum(daily_usd_earnings_list)
        monthly_usd_earnings = sum(daily_usd_earnings_list[:30])
        daily_usd_earnings = daily_usd_earnings_list[0]

        total_power_consumption = num_systems * power_consumption_per_system
        daily_electricity_cost = (total_power_consumption / 1000) * electricity_cost * 24
        monthly_electricity_cost = daily_electricity_cost * 30
        yearly_electricity_cost = daily_electricity_cost * 365

        yearly_management_fee = total_system_cost * management_charge_percent / 100
        monthly_management_fee = yearly_management_fee / 12
        daily_management_fee = yearly_management_fee / 365

        daily_total_cost = daily_electricity_cost + daily_management_fee
        monthly_total_cost = monthly_electricity_cost + monthly_management_fee
        yearly_total_cost = yearly_electricity_cost + yearly_management_fee

        daily_net_earnings = daily_usd_earnings - daily_total_cost
        monthly_net_earnings = monthly_usd_earnings - monthly_total_cost
        yearly_net_earnings = yearly_usd_earnings - yearly_total_cost

        if daily_btc_earnings > 0:
            cost_to_mine_one_btc = daily_total_cost / daily_btc_earnings
        else:
            cost_to_mine_one_btc = float('inf')

        # --- General Metrics (no BTC price or network hashrate) ---
        st.markdown(
            f"**挖矿成本/BTC**: `{'无法计算' if cost_to_mine_one_btc == float('inf') else f'${cost_to_mine_one_btc:,.2f}'}`  |  "
            f"**矿机成本**: `${total_system_cost:,.0f}`  |  "
            f"**总算力**: `{total_hash_rate:,.0f} TH/s`  |  "
            f"**总功耗**: `{total_power_consumption:,.0f} W`"
        )

        # --- KPI Categories as Columns (with divider) ---
        st.markdown('<div class="framed-section"></div>', unsafe_allow_html=True)
        col_day, col_month, col_year = st.columns(3)
        with col_day:
            st.markdown("**第1天**")
            st.markdown(f"BTC 收益: `{daily_btc_earnings:,.6f}`")
            st.markdown(f"美元收益: `${daily_usd_earnings:,.2f}`")
            st.markdown(f"成本(电+管理): `${daily_total_cost:,.2f}`")
            st.markdown(f"净收益(税前): `${daily_net_earnings:,.2f}`")
        with col_month:
            st.markdown("**前30天累计**")
            st.markdown(f"BTC 收益: `{monthly_btc_earnings:,.6f}`")
            st.markdown(f"美元收益: `${monthly_usd_earnings:,.2f}`")
            st.markdown(f"成本(电+管理): `${monthly_total_cost:,.2f}`")
            st.markdown(f"净收益(税前): `{monthly_net_earnings:,.2f}`")
        with col_year:
            st.markdown("**前365天累计**")
            st.markdown(f"BTC 收益: `{yearly_btc_earnings:,.6f}`")
            st.markdown(f"美元收益: `${yearly_usd_earnings:,.2f}`")
            st.markdown(f"成本(电+管理): `${yearly_total_cost:,.2f}`")
            st.markdown(f"净收益(税前): `${yearly_net_earnings:,.2f}`")

    except Exception as e:
        st.error(f"发生错误: {e}")