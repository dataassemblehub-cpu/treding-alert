import logging
import os
from src.repositories.market_repo import MarketRepository
from src.providers.yfinance_provider import YFinanceProvider
from src.services.market_service import MarketService
from src.services.telegram_router import TelegramRouter
from src.strategies.scoring import ScoringEngine
from src.strategies.decision_engine import DecisionEngine
from src.strategies.portfolio_ranker import PortfolioRanker
from src.analysis import analyze_quality, analyze_growth, analyze_valuation, analyze_risk
from src.strategies.near_52w_low import Near52WeekLowStrategy

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def main():
    setup_logging()
    logging.info("Starting Phase 3 Intelligence Engine...")

    repo = MarketRepository()
    provider = YFinanceProvider()
    market_service = MarketService(repo, provider)
    telegram_router = TelegramRouter(db_path=repo.db_path)
    ranker = PortfolioRanker(db_path=repo.db_path)
    
    scoring = ScoringEngine()
    decision_engine = DecisionEngine(scoring)
    entry_strategy = Near52WeekLowStrategy()
    
    symbols = repo.get_all_symbols()
    if not symbols:
        logging.error("No symbols found.")
        return

    decisions = []

    for symbol in symbols:
        try:
            stock = market_service.prepare_stock(symbol)
            financials = repo.get_financial_metrics(symbol)
            
            analysis_results = {
                "quality": analyze_quality(financials),
                "growth": analyze_growth(financials),
                "valuation": analyze_valuation(financials),
                "risk": analyze_risk(financials)
            }
            
            current_price = float(stock.history['close'].iloc[-1]) if not stock.history.empty else 0.0
            entry_alert = entry_strategy.run(stock, current_price) if current_price > 0 else None
            entry_score = 90.0 if entry_alert else 40.0
            
            decision = decision_engine.evaluate(symbol, analysis_results, entry_score)
            decisions.append(decision)
            
            ranker.audit_decision(decision)
            logging.info(f"[{symbol}] Decision: {decision.recommendation} | Score: {decision.investment_score}")
            
        except Exception as e:
            logging.error(f"Error processing {symbol}: {e}")

    ranked_decisions = ranker.rank_and_filter(decisions)
    telegram_router.route_decisions(ranked_decisions)
    logging.info("Run completed.")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
