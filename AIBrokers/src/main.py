from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph

from agents.market_data import market_data_agent, check_data_valid
from agents.portfolio_manager import portfolio_management_agent
from agents.technicals import technical_analyst_agent
from agents.risk_manager import risk_management_agent
from agents.sentiment import sentiment_agent
from agents.state import AgentState

import argparse
from datetime import datetime


def parse_hedge_fund_response(response):
    import json

    try:
        # Attempt to load the response as JSON
        action_data = json.loads(response)   
        return action_data
    except json.JSONDecodeError:
        print(f"Error parsing response: {response}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


##### Run the AIBrokers #####
def run_hedge_fund(
    crypto: str,
    start_date: str,
    end_date: str,
    portfolio: dict,
    show_reasoning: bool = False,
):
    # """Run the AI-powered hedge fund trading system.

    # Args:
    #     crypto: Symbol of the cryptocurrency to trade
    #     start_date: Start date for analysis (YYYY-MM-DD)
    #     end_date: End date for analysis (YYYY-MM-DD)
    #     portfolio: Dictionary containing portfolio information:
    #         - cash: Available capital
    #         - leverage: Trading leverage
    #         - risk: Risk tolerance per trade
    #     show_reasoning: Whether to display agent reasoning

    # Returns:
    #     str: Trading decision in JSON format containing action and quantity
    # """
    try:
        workflow = create_workflow()
        app = workflow.compile()
    
        valid = check_data_valid(crypto, start_date, end_date)
        if valid:
            final_state = app.invoke(
                {
                    "messages": [
                        HumanMessage(
                            content="Make a trading decision based on the provided data.",
                        )
                    ],
                    "data": {
                        "crypto": crypto,
                        "portfolio": portfolio,
                        "start_date": start_date,
                        "end_date": end_date,
                        "analyst_signals": {},
                    },
                    "metadata": {
                        "show_reasoning": show_reasoning,
                    },
                },
            )
            # Log the content for debugging
            action_content = final_state["messages"][-1].content
            
            # Ensure action is a valid JSON string
            if not action_content:
                raise ValueError("Received empty action content from agent.")
            
            action_data = parse_hedge_fund_response(action_content)  # Parse the action string
            return action_data.get("decisions")  # Return as JSON string
        else:
            return "Cant Run AI"
    except Exception as e:
        print(f"Error in run_hedge_fund: {e}")
        return {"action": "hold", "quantity": 0}  # Return default action on error


def create_workflow():
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("market_data_agent", market_data_agent)
    workflow.add_node("technical_analyst_agent", technical_analyst_agent)
    workflow.add_node("sentiment_agent", sentiment_agent)
    workflow.add_node("risk_management_agent", risk_management_agent)
    workflow.add_node("portfolio_management_agent", portfolio_management_agent)

    # Define the workflow
    workflow.set_entry_point("market_data_agent")
    workflow.add_edge("market_data_agent", "technical_analyst_agent")
    workflow.add_edge("market_data_agent", "sentiment_agent")
    workflow.add_edge("technical_analyst_agent", "risk_management_agent")
    workflow.add_edge("sentiment_agent", "risk_management_agent")
    workflow.add_edge("risk_management_agent", "portfolio_management_agent")
    workflow.add_edge("portfolio_management_agent", END)

    return workflow




# Add this at the bottom of the file
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the hedge fund trading system")
    parser.add_argument("--crypto", type=str, required=True, help="Stock crypto symbol")
    parser.add_argument(
        "--balance",
        type=float,
        help="Your balance available to trade. Default: 100000$",
    )
    parser.add_argument(
        "--leverage", type=float, help="Leverage you want to set. Default: 10"
    )
    parser.add_argument(
        "--risk",
        type=float,
        help="Proportion of the total balance that can be lost per trade. Default: 0.05",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        help="Start date (YYYY-MM-DD). Defaults to 1 months before end date",
    )
    parser.add_argument(
        "--end-date", type=str, help="End date (YYYY-MM-DD). Defaults to today"
    )
    parser.add_argument(
        "--show-reasoning", action="store_true", help="Show reasoning from each agent"
    )

    args = parser.parse_args()

    workflow = create_workflow()
    app = workflow.compile()


    # Validate dates if provided
    if args.start_date:
        try:
            datetime.strptime(args.start_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Start date must be in YYYY-MM-DD format")

    if args.end_date:
        try:
            datetime.strptime(args.end_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("End date must be in YYYY-MM-DD format")

    # Ensure portfolio is initialized with default values
    portfolio = {
        "cash": args.balance if args.balance is not None else 100000,
        "leverage": args.leverage if args.leverage is not None else 10,
        "risk": args.risk if args.risk is not None else 0.05,
    }

    result = run_hedge_fund(
        crypto=args.crypto,
        start_date=args.start_date,
        end_date=args.end_date,
        portfolio=portfolio,
        show_reasoning=args.show_reasoning,
    )
    print("\nFinal Result:")

    print(result)
