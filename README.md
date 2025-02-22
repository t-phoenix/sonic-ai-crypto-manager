# sonic-ai-crypto-manager
Multi AI Agent system to automate the on chain portfolio management/ hedge fund management on sonic.

# Overview

## AIBroker
[AIBrokers - Github](https://github.com/AI-Brokers/AIBrokers)

AI Brokers crypto uses lang graph to decide on what to do with the asset, by deploying a multi agent system.
Currently Employes:
- Market Data Analyst
- Technical Analyst
- Sentiment Analyst

Gather info and data from binance and hyperliquid public api's and decide with openai llm api.

Lastly we have 2 more agents which help make decision based on above Analysts:
- Risk Analyst
- Fund Manager

To run the program:
```
poetry run python src/main.py --crypto ETH  
```

We get an output:
```json
{
'action': 'long', 
'quantity': 10000, 
'confidence': 56.0, 
'reasoning': 'The technical analysis shows a neutral signal overall, but with a bullish trend-following signal at 41%. The sentiment analysis is bullish with a 57% confidence, indicating a potential upward movement. The stop loss and take profit are set at 8.06% based on the calculated volatility of 0.81% and leverage. The maximum position size is adhered to, allowing a quantity of 10,000.', 
'agent_signals': 
    [
        {'agent': 'Technical Analysis', 'signal': 'neutral', 'confidence': 9}, 
        {'agent': 'Trend Following', 'signal': 'bullish', 'confidence': 41}, 
        {'agent': 'Mean Reversion', 'signal': 'neutral', 'confidence': 50}, 
        {'agent': 'Momentum', 'signal': 'neutral', 'confidence': 50},  
        {'agent': 'Volatility', 'signal': 'neutral', 'confidence': 50}, 
        {'agent': 'Statistical Arbitrage', 'signal': 'bearish', 'confidence': 100}, 
        {'agent': 'Sentiment Analysis', 'signal': 'bullish', 'confidence': 57}
    ]
}
```

## Eliza
[ElizaOS - github](https://github.com/elizaOS/eliza)

Eliza provides an open source agentic program written in Javacript, for running and completing tasks, and helps completing on-chain actions.

***Character: Portfolio-Manager*** 
- Connected to discord 
- Connected to Sonic Blockchain
- Provide an Sonic Wallet with initial USDT funds
- Enabled with decentralised swapping/ trading actions 
- Auto Rebalancing portfolio based on time (1hr/ 1day)
- Enabled with auto running pluggin

***Custom Plugin***
- Invoke AIBroker to get the decision with action, quantity, confidence and reasoning
- Complete Swap Transaction
- Present Info to the administrator on Discord.
    - AIBroker 
    - Transaction 
    - Portfolio Balance    


## How to Run

### Developer Setup
- Run and Deploy AIBroker
- Run the Eliza bot with Portfolio-Manager character connecting AIBroker, Sonic Blockchain, and Discord

### How to Use
- Discord:
    - Input by user
    - presets to rebalance Portfolio Automatically