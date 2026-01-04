# test_integration.py
import pandas as pd
import sys
import os

# Add core directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

from metrics_calculator import TradeMetricsCalculator
from risk_rules import RiskRuleEngine
from risk_scorer import RiskScorer

def test_full_pipeline():
    """Test the complete risk analysis pipeline"""
    
    print("Testing Complete Risk Analysis Pipeline")
    print("="*60)
    
    # Create sample data
    print("1. Creating sample trade data...")
    data = {
        'trade_id': list(range(1, 21)),
        'symbol': ['EURUSD'] * 10 + ['GBPUSD'] * 5 + ['BTCUSD'] * 5,
        'entry_time': [f'2024-01-{str(i).zfill(2)} 10:00:00' for i in range(1, 21)],
        'exit_time': [f'2024-01-{str(i).zfill(2)} 12:00:00' for i in range(1, 21)],
        'trade_type': ['BUY', 'SELL'] * 10,
        'lot_size': [0.2] * 20,
        'entry_price': [1.1000 + i*0.001 for i in range(20)],
        'exit_price': [1.1020 + i*0.001 for i in range(20)],
        'stop_loss': [1.0980 + i*0.001 for i in range(15)] + [0] * 5,  # 5 trades without SL
        'take_profit': [1.1050 + i*0.001 for i in range(20)],
        'profit_loss': [20, -30, 40, -25, 35, -20, 45, -15, 50, -10, 
                       20, -30, 40, -25, 35, -20, 45, -15, 50, -10],
        'account_balance_before': [10000] * 20
    }
    
    df = pd.DataFrame(data)
    print(f"   Created {len(df)} sample trades")
    
    # Step 1: Calculate Metrics
    print("\n2. Calculating trading metrics...")
    calculator = TradeMetricsCalculator(df)
    metrics = calculator.compute_all_metrics()
    
    print(f"   Win Rate: {metrics.get('win_rate', 0):.1f}%")
    print(f"   Avg Position Size: {metrics.get('avg_position_size_pct', 0):.1f}%")
    print(f"   SL Usage: {metrics.get('sl_usage_rate', 0):.1f}%")
    
    # Step 2: Detect Risks
    print("\n3. Detecting trading risks...")
    engine = RiskRuleEngine(metrics, df)
    risk_results = engine.detect_all_risks()
    
    print(f"   Detected {len(risk_results['detected_risks'])} risks:")
    for risk in risk_results['detected_risks']:
        details = risk_results['risk_details'].get(risk, {})
        print(f"   • {risk}: {details.get('message', '')}")
    
    # Step 3: Calculate Risk Score
    print("\n4. Calculating risk score...")
    scorer = RiskScorer()
    score_result = scorer.calculate_score(risk_results['risk_details'])
    
    print(f"   Overall Score: {score_result['score']}/100")
    print(f"   Grade: {score_result['grade']}")
    print(f"   Improvement Potential: {score_result['improvement_potential']}%")
    
    # Display scorecard
    print("\n" + "="*60)
    print("FINAL SCORECARD:")
    print("="*60)
    print(scorer.generate_scorecard(score_result))
    
    print("\nRECOMMENDATION:")
    print("-"*30)
    print(score_result['recommendation'])
    
    print("\nPipeline test completed successfully!")
    
    return {
        'metrics': metrics,
        'risk_results': risk_results,
        'score_result': score_result
    }

if __name__ == "__main__":
    results = test_full_pipeline()