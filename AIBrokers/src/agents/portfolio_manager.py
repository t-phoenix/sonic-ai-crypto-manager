from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai.chat_models import ChatOpenAI
from config.analysis_weights import (
    TECHNICAL_ANALYSIS_WEIGHT,
    SENTIMENT_ANALYSIS_WEIGHT,
)

from agents.state import AgentState, show_agent_reasoning
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), "../../.env")

load_dotenv(dotenv_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


##### Portfolio Management Agent #####
def portfolio_management_agent(state: AgentState):
    """Makes final trading decisions and generates orders"""
    show_reasoning = state["metadata"]["show_reasoning"]
    portfolio = state["data"]["portfolio"]

    # Get the technical analyst, fundamentals agent, and risk management agent messages
    technical_message = next(
        msg for msg in state["messages"] if msg.name == "technical_analyst_agent"
    )
    sentiment_message = next(
        msg for msg in state["messages"] if msg.name == "sentiment_agent"
    )
    risk_message = next(
        msg for msg in state["messages"] if msg.name == "risk_management_agent"
    )

    # Create the prompt template
    template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"""You are a portfolio manager making final trading decisions.
                Your job is to make a trading decision based on the team's analysis while strictly adhering
                to risk management constraints.

                RISK MANAGEMENT CONSTRAINTS:
                - You MUST NOT exceed the max_position_size specified by the risk manager
                - You MUST follow the stop loss, price to set stop loss recommended by risk management
                - These are hard constraints that cannot be overridden by other signals

                When weighing the different signals for direction and timing:

                1. Technical Analysis ({TECHNICAL_ANALYSIS_WEIGHT}% weight)
                   - Secondary confirmation
                   - Helps with entry/exit timing
                
                2. Sentiment Analysis ({SENTIMENT_ANALYSIS_WEIGHT}% weight)
                   - Final consideration
                   - Can influence sizing within risk limits
                
                The decision process should be:
                1. First check risk management constraints
                2. Use technical analysis for timing
                3. Consider sentiment for final adjustment
                Provide the following in your output:
                - "action": "long" | "short" 
                - "volatility": <volatility from Risk manager>
                - "stop loss" : <stop loss from Risk Management>
                - "take profit" : <take profit from Risk Management>
                - "quantity": <positive integer>
                - "confidence": <float between 0 and 1>
                - "agent_signals": <list of agent signals including agent name, signal (bullish | bearish | neutral), and their confidence>
                - "reasoning": <concise explanation of the decision including how you weighted the signals>
                Format the output so it is easy for users to read.
                Trading Rules:
                - Never exceed risk management position limits
                - Quantity must be ≤ current position for sells
                - Quantity must be ≤ max_position_margin from risk management""",
            ),
            (
                "human",
                """Based on the team's analysis below, make your trading decision.

                Technical Analysis Trading Signal: {technical_message}
                Sentiment Analysis Trading Signal: {sentiment_message}
                Risk Management : {risk_message}

                Here is the current portfolio:
                Portfolio:
                : 
                | Cash         | {portfolio_cash}     |
                |---------     |---------|
                | Leverage     | {portfolio_leverage} | 
                |---------     |---------|
                | Risk     | {portfolio_risk} | 
                
                # Add these points to reasoning: 
                # - Stop Loss and Take profit values based on cryptocurrency volatility and leverage and the leverage
                # - Quantity value based on risk 
                
                Output strictly in JSON with the following structure:
                {{
                  "decisions": {{
                    "action": "buy/sell/short/cover/hold",
                    "quantity": integer,
                    "confidence": float,
                    "reasoning": "string"
                  }}
                }}

                # Never use bullet points or numbered lists for data presentation.
                
                # Only include the Portfolio, action, quantity, volatility, stop loss, reasoning, confidence, and agent_signals in your output as response. 
                # Just for reasoning, Use bullet points to separate main ideas
                # Use percentage to represent the confidence
                # Remember, the action must be either long, short.
                """,
            ),
        ]
    )

    # Generate the prompt
    prompt = template.invoke(
        {
            "technical_message": technical_message.content,
            "sentiment_message": sentiment_message.content,
            "risk_message": risk_message.content,
            "portfolio_cash": f"{portfolio['cash']:.2f}",
            "portfolio_leverage": f"{portfolio['leverage']:.2f}",
            "portfolio_risk": f"{portfolio['risk']:.2f}",
        }
    )
    # Invoke the LLM
    llm = ChatOpenAI(
        openai_api_key=OPENAI_API_KEY, temperature=0.3, model="gpt-4o-mini"
    )
    result = llm.invoke(prompt)

    # Create the portfolio management message
    message = HumanMessage(
        content=result.content,
        name="portfolio_management",
    )

    # Print the decision if the flag is set
    if show_reasoning:
        show_agent_reasoning(message.content, "Portfolio Management Agent")

    return {"messages": state["messages"] + [message]}
