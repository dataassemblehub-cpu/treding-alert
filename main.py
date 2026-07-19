import argparse
import logging
import os
from src.repositories.market_repo import MarketRepository
from src.providers.yfinance_provider import YFinanceProvider
from src.services.market_service import MarketService
from src.services.telegram_router import TelegramRouter
from src.strategies.scoring import ScoringEngine
from src.strategies.decision_engine import DecisionEngine
from src.strategies.decision_change_detector import DecisionChangeDetector
from src.strategies.portfolio_ranker import PortfolioRanker
from src.analysis import analyze_quality, analyze_growth, analyze_valuation, analyze_risk
from src.strategies.near_52w_low import Near52WeekLowStrategy

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def parse_args():
    parser = argparse.ArgumentParser(description="Intelligence Engine Phase 3.1")
    parser.add_argument('--dry-run', action='store_true', help="Run without DB writes or Telegram")
    parser.add_argument('--test-symbols', type=str, help="Comma separated list of symbols")
    return parser.parse_args()

def main():
    args = parse_args()
    setup_logging()
    
    if args.dry_run:
        logging.info("[DRY RUN MODE] - No DB writes or Telegram alerts.")
    else:
        logging.info("Starting Phase 3.1 Intelligence Engine...")

    repo = MarketRepository()
    provider = YFinanceProvider()
    market_service = MarketService(repo, provider)
    telegram_router = TelegramRouter(db_path=repo.db_path)
    ranker = PortfolioRanker(db_path=repo.db_path)
    detector = DecisionChangeDetector(repo.db_path)
    
    scoring = ScoringEngine()
    decision_engine = DecisionEngine(scoring)
    entry_strategy = Near52WeekLowStrategy()
    
    if args.test_symbols:
        symbols = [s.strip() for s in args.test_symbols.split(',')]
    else:
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
            
            data_qual = financials.data_quality if financials else "INSUFFICIENT"
            decision = decision_engine.evaluate(symbol, analysis_results, entry_score, data_quality=data_qual)
            
            transition = detector.detect_transition(decision)
            if transition:
                decision.transition_alert = transition
                
            decisions.append(decision)
            
            if not args.dry_run:
                ranker.audit_decision(decision)
                
            logging.info(f"[{symbol}] Decision: {decision.recommendation} | Quality: {decision.data_quality} | Transition: {transition}")
            
        except Exception as e:
            logging.error(f"Error processing {symbol}: {e}")

    ranked_decisions = ranker.rank_and_filter(decisions)
    
    if args.dry_run:
        print("\n--- VALIDATION SUMMARY REPORT ---")
        counts = {}
        for d in ranked_decisions:
            counts[d.recommendation] = counts.get(d.recommendation, 0) + 1
        for rec, count in sorted(counts.items()):
            print(f"{rec}: {count}")
        print("---------------------------------")
    else:
        telegram_router.route_decisions(ranked_decisions)
        
    logging.info("Run completed.")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
