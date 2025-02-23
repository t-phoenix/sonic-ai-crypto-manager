from langchain_openai.chat_models import ChatOpenAI

from agents.state import AgentState
from tools.api import get_price_API_HYPERLIQUID, get_LS_OI_Copin

from datetime import datetime


def check_data_valid(crypto, start_date, end_date):
    """
    Validate if market data is available for the given crypto and date range.

    Args:
        crypto (str): Cryptocurrency symbol
        start_date (str, optional): Start date in 'YYYY-MM-DD' format. If None, defaults to 1 month before end_date
        end_date (str, optional): End date in 'YYYY-MM-DD' format. If None, defaults to current date

    Returns:
        bool: True if both price and insider trade data are available, False otherwise
    """
    # Set default dates
    end_date = end_date or datetime.now().strftime("%Y-%m-%d")
    if not start_date:
        # Calculate 1 months before end_date
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        start_date = (
            end_date_obj.replace(month=end_date_obj.month - 1)
            if end_date_obj.month > 1
            else end_date_obj.replace(
                year=end_date_obj.year - 1, month=end_date_obj.month + 11
            )
        )
        start_date = start_date.strftime("%Y-%m-%d")
    else:
        start_date = start_date

    prices = get_price_API_HYPERLIQUID(
        pair=crypto,
        open_time=start_date,
        close_time=end_date,
    )
    insider_trades = get_LS_OI_Copin(pair=crypto)
    if isinstance(prices, str) | isinstance(insider_trades, str):
        print("Data invalid")
        return False
    else:
        return True


def market_data_agent(state: AgentState):
    """
    Agent responsible for gathering and preprocessing market data.

    This agent:
    1. Sets up the date range (defaults to last month if not specified)
    2. Fetches historical price data from HyperLiquid
    3. Retrieves long/short open interest data from Copin

    Args:
        state (AgentState): Current state containing:
            - messages: List of conversation messages
            - data: Dict containing:
                - crypto: Cryptocurrency symbol
                - start_date: Optional start date
                - end_date: Optional end date

    Returns:
        dict: Updated state with:
            - messages: Original messages
            - data: Original data plus:
                - prices: Historical OHLCV price data
                - start_date: Processed start date
                - end_date: Processed end date
                - insider_trades: Long/short open interest data
    """
    messages = state["messages"]
    data = state["data"]
    # Set default dates
    end_date = data["end_date"] or datetime.now().strftime("%Y-%m-%d")
    if not data["start_date"]:
        # Calculate 1 months before end_date
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        start_date = (
            end_date_obj.replace(month=end_date_obj.month - 1)
            if end_date_obj.month > 1
            else end_date_obj.replace(
                year=end_date_obj.year - 1, month=end_date_obj.month + 11
            )
        )
        start_date = start_date.strftime("%Y-%m-%d")
    else:
        start_date = data["start_date"]

    # Get the historical price data

    prices = get_price_API_HYPERLIQUID(
        pair=data["crypto"],
        open_time=start_date,
        close_time=end_date,
    )

    # Get the insider trades
    insider_trades = get_LS_OI_Copin(pair=data["crypto"])

    return {
        "messages": messages,
        "data": {
            **data,
            "prices": prices,
            "start_date": start_date,
            "end_date": end_date,
            "insider_trades": insider_trades,
        },
    }
