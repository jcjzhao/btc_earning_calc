import streamlit as st
import requests

# --- Consistent font and style for all input/output ---
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
    .kpi-row {
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.4 !important;
        font-size: 16px !important;
        font-weight: normal !important;
    }
    .kpi-header {
        font-size: 18px !important;
        font-weight: bold !important;
        line-height: 1.4 !important;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 1em;
    }
    th, td {
        border: 1px solid #ddd !important;
        padding: 8px !important;
        text-align: center !important;
        font-size: 16px !important;
    }
    th {
        background-color: #f2f2f2 !important;
        font-weight: bold !important;
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
    </style>
    """,
    unsafe_allow_html=True
)

# --- Title ---
st.markdown(
    """
    <h2 style="text-align: center;">比特币挖矿收益</h2>
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

# --- Real-time BTC price (fetch every run) ---
try:
    btc_price_response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")
    real_time_btc_price = btc_price_response.json()["bitcoin"]["usd"]
except Exception:
    real_time_btc_price = 30000.0

# --- Real-time network hash rate ---
try:
    hash_rate_response = requests.get("https://blockchain.info/q/hashrate")
    real_time_network_hash_rate = hash_rate_response.json() / 1e3  # Convert GH/s to TH/s
except Exception:
    real_time_network_hash_rate = 350000.0

# --- Inputs (all as text_input, no +/-) ---
st.markdown("#### 输入参数")
col1, col2, col3 = st.columns(3)
with col1:
    system_choice = st.selectbox("选择矿机型号", options=list(systems.keys()))
with col2:
    num_systems_str = st.text_input("矿机数量", value="1")
with col3:
    electricity_cost_str = st.text_input("电费($/kWh)", value="0.050")

col4, col5, col6 = st.columns(3)
with col4:
    efficiency_str = st.text_input("电力效率(%)", value="95.0")
with col5:
    management_fee_str = st.text_input("管理费($/kWh)", value="0.006")
with col6:
    maintenance_fee_str = st.text_input("运营费($/kWh)", value="0.002")

col7, col8 = st.columns(2)
with col7:
    btc_price_str = st.text_input("比特币价格($)", value=str(real_time_btc_price))
with col8:
    network_hash_rate_str = st.text_input("全网算力(TH/s)", value=str(real_time_network_hash_rate))

# --- Validation and conversion ---
try:
    num_systems = int(num_systems_str)
    electricity_cost = float(electricity_cost_str)
    efficiency = float(efficiency_str)
    management_fee = float(management_fee_str)
    maintenance_fee = float(maintenance_fee_str)
    btc_price = float(btc_price_str)
    network_hash_rate = float(network_hash_rate_str)
    if num_systems < 1 or electricity_cost < 0 or efficiency < 0 or management_fee < 0 or maintenance_fee < 0 or btc_price < 0 or network_hash_rate < 0:
        st.error("所有输入必须为正数")
        st.stop()
except ValueError:
    st.error("请输入有效的数字")
    st.stop()

# --- System config ---
selected_system = systems[system_choice]
hash_rate_per_system = selected_system["hash_rate"]
power_consumption_per_system = selected_system["power_consumption"]
unit_price_per_system = selected_system["unit_price"]
total_system_cost = num_systems * unit_price_per_system

# --- Calculation and Output ---
if st.button("计算收益"):
    try:
        final_btc_price = btc_price
        final_network_hash_rate = network_hash_rate

        total_hash_rate = num_systems * hash_rate_per_system
        block_reward = 3.125
        blocks_per_day = 144
        btc_per_th = (block_reward * blocks_per_day) / final_network_hash_rate

        daily_btc_earnings = total_hash_rate * btc_per_th
        monthly_btc_earnings = daily_btc_earnings * 30
        yearly_btc_earnings = daily_btc_earnings * 365
        daily_usd_earnings = daily_btc_earnings * final_btc_price
        monthly_usd_earnings = monthly_btc_earnings * final_btc_price
        yearly_usd_earnings = yearly_btc_earnings * final_btc_price

        true_electricity_cost = electricity_cost / (efficiency / 100)
        total_power_consumption = num_systems * power_consumption_per_system
        daily_electricity_cost = (total_power_consumption / 1000) * true_electricity_cost * 24
        monthly_electricity_cost = daily_electricity_cost * 30
        yearly_electricity_cost = daily_electricity_cost * 365

        daily_management_fee = management_fee * (total_power_consumption / 1000) / (efficiency / 100)
        daily_maintenance_fee = maintenance_fee * (total_power_consumption / 1000) / (efficiency / 100)
        monthly_management_fee = daily_management_fee * 30
        yearly_management_fee = daily_management_fee * 365
        monthly_maintenance_fee = daily_maintenance_fee * 30
        yearly_maintenance_fee = daily_maintenance_fee * 365

        daily_total_cost = daily_electricity_cost + daily_management_fee + daily_maintenance_fee
        monthly_total_cost = monthly_electricity_cost + monthly_management_fee + monthly_maintenance_fee
        yearly_total_cost = yearly_electricity_cost + yearly_management_fee + yearly_maintenance_fee

        daily_net_earnings = daily_usd_earnings - daily_total_cost
        monthly_net_earnings = daily_net_earnings * 30
        yearly_net_earnings = daily_net_earnings * 365

        if daily_btc_earnings > 0:
            cost_to_mine_one_btc = daily_total_cost / daily_btc_earnings
        else:
            cost_to_mine_one_btc = float('inf')

        # --- General Metrics ---
        st.markdown("#### 比特币关键指标")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"**实时比特币价格**: ${final_btc_price:,.2f}")
        with col2:
            st.markdown(f"**实时全网算力**: {final_network_hash_rate:,.2f} TH/s")
        with col3:
            st.markdown(f"**BTC/1TH/s/天**: {btc_per_th:,.10f} ")
        with col4:
            if cost_to_mine_one_btc == float('inf'):
                st.markdown("**挖矿成本/BTC**: 无法计算")
            else:
                st.markdown(f"**挖矿成本/BTC**: ${cost_to_mine_one_btc:,.2f}")

        # --- System Configuration Metrics ---
        st.markdown("#### 系统配置指标")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"**矿机成本**: ${total_system_cost:,.0f}")
        with col2:
            st.markdown(f"**总算力**: {total_hash_rate:,.2f} TH/s")
        with col3:
            st.markdown(f"**总功耗**: {total_power_consumption:,.2f} W")
        with col4:
            st.markdown(f"**电费效率**: {efficiency:.2f}%")

        # --- KPI Categories as Table ---
        st.markdown("#### 关键绩效指标")
        kpi_table = f"""
        | 指标              | 每日                    | 每月                    | 每年                    |
        |-------------------|-------------------------|-------------------------|-------------------------|
        | BTC 收益          | {daily_btc_earnings:,.6f}  | {monthly_btc_earnings:,.6f} | {yearly_btc_earnings:,.6f} |
        | 美元收益          | ${daily_usd_earnings:,.2f}    | ${monthly_usd_earnings:,.2f}    | ${yearly_usd_earnings:,.2f}    |
        | 成本(电,管理,维护)| ${daily_total_cost:,.2f}      | ${monthly_total_cost:,.2f}      | ${yearly_total_cost:,.2f}      |
        | 净收益(税前)      | ${daily_net_earnings:,.2f}    | ${monthly_net_earnings:,.2f}    | ${yearly_net_earnings:,.2f}    |
        """
        st.markdown(kpi_table)

    except Exception as e:
        st.error(f"发生错误: {e}")