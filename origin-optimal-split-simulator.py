import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Reward Share Simulator", layout="centered")

st.title("📈 Reward Share Simulator – StakeDAO vs Curve (no user boost)")

st.sidebar.header("🧮 Settings")

# Fixed user pool share, simulate over split
stake_dao_vecrv = st.sidebar.number_input("StakeDAO veCRV holdings (in M)", value=118.0, min_value=0.0)
total_vecrv = st.sidebar.number_input("Total veCRV (in M)", value=794.0, min_value=0.1)
pool_share = st.sidebar.slider("Pool dominance (%)", min_value=1, max_value=100, value=93, step=1)
stake_dao_fee = st.sidebar.slider("Stake DAO fee (%)", min_value=0.0, max_value=17.0, value=17.0, step=0.1)

highlight_split = st.sidebar.slider("Highlighted StakeDAO split (%)", min_value=0, max_value=100, value=50, step=1)

stake_dao_fee = stake_dao_fee / 100

# X-axis: split percentage from 0% to 100%
splits = np.linspace(0, 100, 2000)
split_fracs = splits / 100

# Fixed pool domination
pool_user_frac = pool_share / 100
other_pool_frac = 1.0 - pool_user_frac

# Arrays to store reward components
reward_curve_arr = []
reward_stakedao_arr = []
user_reward_share_arr = []

for split_frac in split_fracs:
    user_stake_dao_frac = pool_user_frac * split_frac
    pool_stakedao_frac = other_pool_frac + user_stake_dao_frac
    user_stake_dao_share = user_stake_dao_frac / pool_stakedao_frac if pool_stakedao_frac > 0 else 0

    # Working balances
    stake_dao_working_balance = np.minimum(
        0.4 * pool_stakedao_frac * 100 + 0.6 * (100 * stake_dao_vecrv / total_vecrv),
        pool_stakedao_frac * 100
    )
    curve_deposit_working_balance = 0.4 * (100 - pool_stakedao_frac * 100)
    working_supply = stake_dao_working_balance + curve_deposit_working_balance

    # Reward calculations
    reward_curve = 100 * curve_deposit_working_balance / working_supply if working_supply > 0 else 0
    total_reward_stakedao = (100 * stake_dao_working_balance / working_supply) * (1 - stake_dao_fee) if working_supply > 0 else 0
    reward_stakedao = total_reward_stakedao * user_stake_dao_share

    reward_total = reward_curve + reward_stakedao

    # Store results
    reward_curve_arr.append(reward_curve)
    reward_stakedao_arr.append(reward_stakedao)
    user_reward_share_arr.append(reward_total)

# --- Plot
fig, ax = plt.subplots()
ax.plot(splits, user_reward_share_arr, label="Total user reward share (%)", color="blue")
ax.axvline(highlight_split, color="gray", linestyle="--", label=f"{highlight_split}% split")
ax.set_xlabel("Share deposited on Stake DAO (%)")
ax.set_ylabel("Reward share (%)")
ax.set_title("Reward share vs split to Stake DAO (fixed pool share)")
ax.legend()
ax.grid(True)
st.pyplot(fig)

# --- Summary
highlight_index = np.argmin(np.abs(splits - highlight_split))
highlighted_reward = user_reward_share_arr[highlight_index]

# Find max reward and corresponding split
max_index = np.argmax(user_reward_share_arr)
max_reward = user_reward_share_arr[max_index]
optimal_split = splits[max_index]

st.markdown(f"""
### 🧾 Summary:
- Stake DAO fee: **{int(stake_dao_fee * 100)}%**
- Pool Share (fixed): **{pool_share}%**
- Reward share at **{highlight_split}%** split: **{highlighted_reward:.2f}%**
- Maximum reward share: **{max_reward:.2f}%** at **{optimal_split:.1f}%** split
""")

st.caption("This simulator estimates your share of rewards depending on your split to StakeDAO, for a fixed pool share.")
