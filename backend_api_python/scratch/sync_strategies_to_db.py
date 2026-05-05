import os
import sys

# Add app directory to path robustly
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from app.utils.db import get_db_connection

strategies = [
    {
        'name': 'SMA_Cross_RSI_Basic',
        'file': 'research/examples/strategies/sma_cross_rsi_basic.py',
        'desc': '基础双均线金叉 + RSI 超买过滤'
    },
    {
        'name': 'SMA_Cross_RSI_ATR_Dynamic_Stop',
        'file': 'research/examples/strategies/sma_cross_rsi_atr_dynamic_stop.py',
        'desc': '均线策略 + ATR 波动率过滤 + 动态止损'
    },
    {
        'name': 'SMA_Cross_RSI_ADX_Trend_Filter',
        'file': 'research/examples/strategies/sma_cross_rsi_adx_trend_filter.py',
        'desc': '均线策略 + ADX 趋势强度过滤 + 趋势确认'
    },
    {
        'name': 'Factor Trend Momentum',
        'file': 'research/examples/factors/factor_trend_momentum.py',
        'desc': '纯因子：多空动量综合得分'
    },
    {
        'name': 'Factor Volatility Squeeze',
        'file': 'research/examples/factors/factor_volatility_squeeze.py',
        'desc': '纯因子：布林带与肯特纳通道挤压'
    },
    {
        'name': 'Factor Mean Reversion',
        'file': 'research/examples/factors/factor_mean_reversion.py',
        'desc': '纯因子：价格偏离均线的Z-Score'
    },
    {
        'name': 'Factor_Funding_Rate',
        'file': 'research/examples/factors/factor_funding_rate.py',
        'desc': '纯因子：币安历史资金费率'
    },
    {
        'name': 'FundingRate_BottomFisher',
        'file': 'research/examples/strategies/funding_rate_bottom_fisher.py',
        'desc': '策略：资金费率抄底策略'
    },
    {
        'name': 'KOL_Range_Fade_4H_Long',
        'file': 'research/examples/strategies/kol_range_fade_4h_long.py',
        'desc': '策略：4H区间震荡做多 (BNB最佳)'
    }
]

def sync_to_db():
    try:
        with get_db_connection() as db:
            cur = db.cursor()
            # Workspace root is the QuantDinger directory
            WORKSPACE_ROOT = PROJECT_ROOT
            
            for s in strategies:
                try:
                    # Read code from file
                    full_path = os.path.join(WORKSPACE_ROOT, s['file'])
                    if not os.path.exists(full_path):
                        print(f"File not found: {full_path}")
                        continue
                        
                    with open(full_path, 'r', encoding='utf-8') as f:
                        code = f.read()
                    
                    # Check if exists (User ID 1 is the default admin)
                    cur.execute("SELECT id FROM qd_indicator_codes WHERE name = %s AND user_id = 1", (s['name'],))
                    row = cur.fetchone()
                    
                    if row:
                        # Update
                        cur.execute(
                            "UPDATE qd_indicator_codes SET code = %s, description = %s, updated_at = NOW() WHERE id = %s",
                            (code, s['desc'], row['id'])
                        )
                        print(f"Sync success (Updated): {s['name']}")
                    else:
                        # Insert
                        cur.execute(
                            """
                            INSERT INTO qd_indicator_codes 
                            (user_id, name, code, description, is_buy, pricing_type, price, review_status, created_at, updated_at)
                            VALUES (1, %s, %s, %s, 0, 'free', 0, 'approved', NOW(), NOW())
                            """,
                            (s['name'], code, s['desc'])
                        )
                        print(f"Sync success (Inserted): {s['name']}")
                except Exception as e:
                    print(f"Failed to sync {s['name']}: {e}")
            db.commit()
            cur.close()
    except Exception as e:
        print(f"Database connection failed: {e}")

if __name__ == "__main__":
    sync_to_db()
