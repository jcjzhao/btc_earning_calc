import streamlit as st
import requests

# Title
st.title("BTC Mining Earnings Calculator")

# Inputs in a compact layout
col1, col2, col3 = st.columns(3)
with col1:
    num_systems = st.text_input("Number of Systems", value="1")
with col2:
    hash_rate_per_system = st.text_input("Hash Rate/System (TH/s)", value="0.0")
with col3:
    power_consumption = st.text_input("Power/System (Watts)", value="0.0")

col4, col5 = st.columns(2)
with col4:
    electricity_cost = st.text_input("Electricity Cost ($/kWh)", value="0.000")

# Validate inputs
try:
    num_systems = int(num_systems)
    hash_rate_per_system = float(hash_rate_per_system)
    power_consumption = float(power_consumption)
    electricity_cost = float(electricity_cost)
except ValueError:
    st.error("Please enter valid numeric values for all inputs.")
    st.stop()

# Button to start calculation
if st.button("Calculate Earnings"):
    try:
        # Fetch BTC price
        btc_price_response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")
        btc_price = btc_price_response.json()["bitcoin"]["usd"]

        # Fetch network difficulty
        difficulty_response = requests.get("https://blockchain.info/q/getdifficulty")
        network_difficulty = difficulty_response.json()

        # Constants
        block_reward = 3.125  # Current BTC block reward
        blocks_per_day = 144  # Average blocks mined per day
        seconds_per_block = 600  # Average time to mine a block (10 minutes)
        network_hash_rate = (network_difficulty * 2**32) / seconds_per_block / 1e12  # Convert to TH/s

        # Total hash rate (in TH/s)
        total_hash_rate = num_systems * hash_rate_per_system

        # BTC earned per TH/s
        btc_per_th = (block_reward / network_difficulty) * (2**32 / 1e12) * seconds_per_block

        # Mining rewards calculation
        mining_reward_per_second = (total_hash_rate * 1e12 / (network_difficulty * 2**32)) * block_reward
        daily_btc_earnings = mining_reward_per_second * 24 * 3600  # Daily BTC earnings
        monthly_btc_earnings = daily_btc_earnings * 30  # Monthly BTC earnings
        yearly_btc_earnings = daily_btc_earnings * 365  # Yearly BTC earnings
        daily_usd_earnings = daily_btc_earnings * btc_price  # Daily USD earnings
        monthly_usd_earnings = monthly_btc_earnings * btc_price  # Monthly USD earnings
        yearly_usd_earnings = yearly_btc_earnings * btc_price  # Yearly USD earnings

        # Electricity cost calculation
        total_power_consumption = num_systems * power_consumption  # Total power in watts
        daily_electricity_cost = (total_power_consumption / 1000) * electricity_cost * 24  # Daily cost in USD
        monthly_electricity_cost = daily_electricity_cost * 30  # Monthly cost in USD
        yearly_electricity_cost = daily_electricity_cost * 365  # Yearly cost in USD

        # Net earnings
        daily_net_earnings = daily_usd_earnings - daily_electricity_cost
        monthly_net_earnings = monthly_usd_earnings - monthly_electricity_cost
        yearly_net_earnings = yearly_usd_earnings - yearly_electricity_cost

        # Display Outputs in Three Columns
        col1, col2, col3 = st.columns(3)

        # Column 1: General Metrics
        with col1:
            st.markdown('<div style="font-weight:bold;">BTC Price</div>', unsafe_allow_html=True)
            st.markdown(f'<div>${btc_price:.2f}</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-weight:bold;">Network Hash Rate</div>', unsafe_allow_html=True)
            st.markdown(f'<div>{network_hash_rate:.2f} TH/s</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-weight:bold;">Block Reward</div>', unsafe_allow_html=True)
            st.markdown(f'<div>{block_reward:.3f} BTC</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-weight:bold;">Blocks per Day</div>', unsafe_allow_html=True)
            st.markdown(f'<div>{blocks_per_day}</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-weight:bold;">Total BTC Mined per Day</div>', unsafe_allow_html=True)
            st.markdown(f'<div>{block_reward * blocks_per_day:.3f} BTC</div>', unsafe_allow_html=True)

        # Column 2: Earnings
        with col2:
            st.markdown('<div style="font-weight:bold;">BTC Earned per 1 TH/s</div>', unsafe_allow_html=True)
            st.markdown(f'<div>{btc_per_th * 24 * 3600:.10f} BTC/day</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-weight:bold;">Daily BTC Earnings</div>', unsafe_allow_html=True)
            st.markdown(f'<div>{daily_btc_earnings:.6f} BTC</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-weight:bold;">Monthly BTC Earnings</div>', unsafe_allow_html=True)
            st.markdown(f'<div>{monthly_btc_earnings:.6f} BTC</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-weight:bold;">Yearly BTC Earnings</div>', unsafe_allow_html=True)
            st.markdown(f'<div>{yearly_btc_earnings:.6f} BTC</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-weight:bold;">Daily Earnings (USD)</div>', unsafe_allow_html=True)
            st.markdown(f'<div>${daily_usd_earnings:.2f}</div>', unsafe_allow_html=True)

        # Column 3: Costs and Net Earnings
        with col3:
            st.markdown('<div style="font-weight:bold;">Daily Electricity Cost</div>', unsafe_allow_html=True)
            st.markdown(f'<div>${daily_electricity_cost:.2f}</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-weight:bold;">Monthly Electricity Cost</div>', unsafe_allow_html=True)
            st.markdown(f'<div>${monthly_electricity_cost:.2f}</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-weight:bold;">Yearly Electricity Cost</div>', unsafe_allow_html=True)
            st.markdown(f'<div>${yearly_electricity_cost:.2f}</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-weight:bold;">Daily Net Earnings</div>', unsafe_allow_html=True)
            st.markdown(f'<div>${daily_net_earnings:.2f}</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-weight:bold;">Yearly Net Earnings</div>', unsafe_allow_html=True)
            st.markdown(f'<div>${yearly_net_earnings:.2f}</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"An error occurred: {e}")