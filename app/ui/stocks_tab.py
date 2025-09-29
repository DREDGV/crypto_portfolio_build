"""
Вкладка для работы с российскими акциями
"""

import logging
from datetime import datetime
from typing import Any, Optional

try:
    from nicegui import ui
except ModuleNotFoundError:
    # Provide a stub so static analyzers still see ui attributes when NiceGUI is missing.
    class _UnavailableUI:
        def __getattr__(self, name: str) -> Any:
            raise RuntimeError("NiceGUI must be installed to use the stocks tab.")

    ui = _UnavailableUI()

logger = logging.getLogger(__name__)


def create_stocks_tab(ui_instance: Optional[Any] = None):
    """     """
    ui_instance = ui_instance or ui

    #  
    try:
        from app.adapters.tinkoff_adapter import BrokerManager
        from app.models.broker_models import StockTransactionIn
        from app.services.broker_service import StockService

        stock_service = StockService()
        broker_manager = BrokerManager()
    except ImportError as e:
        logger.error(f"  : {e}")
        ui_instance.label("?    ").classes("text-red-500")
        return

    with ui_instance.column().classes("w-full p-4 max-h-[calc(100vh-200px)] overflow-y-auto"):
        # 
        with ui_instance.row().classes("items-center gap-3 mb-6"):
            ui_instance.icon("trending_up").classes("text-3xl text-blue-600")
            ui_instance.label(" ").classes("text-3xl font-bold text-gray-800")

        #  
        with ui_instance.card().classes(
            "w-full p-6 bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-500 mb-6"
        ):
            ui_instance.label("??   ").classes(
                "text-xl font-bold text-blue-800 mb-2"
            )
            ui_instance.label(
                "       ."
            ).classes("text-gray-700 mb-3")

            with ui_instance.column().classes("gap-2 mt-4"):
                ui_instance.label("??  :").classes("font-semibold text-gray-800")
                ui_instance.label("   (, , )").classes(
                    "text-gray-700"
                )
                ui_instance.label("   ").classes("text-gray-700")
                ui_instance.label("    ").classes(
                    "text-gray-700"
                )
                ui_instance.label("    ").classes("text-gray-700")
                ui_instance.label("   ").classes("text-gray-700")

        #  
        with ui_instance.card().classes("w-full p-4 mb-6"):
            ui_instance.label(" ").classes(
                "text-lg font-semibold text-gray-800 mb-4"
            )

            # Dropdown   
            broker_select = ui_instance.select(options={}, label="").classes("w-full mb-4")

            #   
            sync_button = ui_instance.button(
                "??  ", icon="sync"
            ).classes("px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg")

            #  
            def load_brokers():
                try:
                    brokers = broker_manager.get_all_brokers()
                    broker_options = {broker.id: broker.name for broker in brokers}
                    broker_select.options = broker_options

                    if broker_options:
                        broker_select.value = list(broker_options.keys())[0]
                        ui_instance.notify(f" {len(brokers)} ", type="positive")
                    else:
                        ui_instance.notify("  ", type="warning")

                except Exception as e:
                    logger.error(f"  : {e}")
                    ui_instance.notify(f"  : {e}", type="negative")

            #  
            def sync_instruments():
                selected_broker = broker_select.value
                if not selected_broker:
                    ui_instance.notify(" ", type="warning")
                    return

                try:
                    sync_button.loading = True
                    count = stock_service.sync_broker_instruments(selected_broker)
                    ui_instance.notify(f" {count} ", type="positive")
                    load_instruments()
                except Exception as e:
                    logger.error(f" : {e}")
                    ui_instance.notify(f" : {e}", type="negative")
                finally:
                    sync_button.loading = False

            sync_button.on("click", sync_instruments)

            #    
            load_brokers()

        #  
        instruments_container = ui_instance.column().classes("w-full mb-6")

        def load_instruments():
            selected_broker = broker_select.value
            if not selected_broker:
                return

            try:
                instruments = stock_service.get_broker_instruments(selected_broker)

                #  
                instruments_container.clear()

                with instruments_container:
                    ui_instance.label(f"  ({len(instruments)})").classes(
                        "text-lg font-semibold text-gray-800 mb-4"
                    )

                    if instruments:
                        # 
                        search_input = ui_instance.input(
                            placeholder="    ..."
                        ).classes("w-full mb-4")

                        #  
                        columns = [
                            {
                                "name": "ticker",
                                "label": "",
                                "field": "ticker",
                                "align": "left",
                            },
                            {
                                "name": "name",
                                "label": "",
                                "field": "name",
                                "align": "left",
                            },
                            {
                                "name": "sector",
                                "label": "",
                                "field": "sector",
                                "align": "left",
                            },
                            {
                                "name": "lot_size",
                                "label": "",
                                "field": "lot_size",
                                "align": "center",
                            },
                            {
                                "name": "currency",
                                "label": "",
                                "field": "currency",
                                "align": "center",
                            },
                            {
                                "name": "actions",
                                "label": "",
                                "field": "actions",
                                "align": "center",
                            },
                        ]

                        rows = []
                        for instrument in instruments:
                            rows.append(
                                {
                                    "ticker": instrument.ticker,
                                    "name": instrument.name,
                                    "sector": instrument.sector or "-",
                                    "lot_size": instrument.lot_size,
                                    "currency": instrument.currency,
                                    "actions": f"add_{instrument.ticker}",
                                }
                            )

                        table = ui_instance.table(
                            columns=columns, rows=rows, row_key="ticker"
                        ).classes("w-full")

                        #  
                        def filter_instruments():
                            query = search_input.value.lower()
                            if query:
                                filtered_rows = [
                                    row
                                    for row in rows
                                    if query in row["ticker"].lower()
                                    or query in row["name"].lower()
                                ]
                            else:
                                filtered_rows = rows
                            table.rows = filtered_rows

                        search_input.on("input", filter_instruments)

                    else:
                        ui_instance.label("  ").classes(
                            "text-gray-500 italic"
                        )

            except Exception as e:
                logger.error(f"  : {e}")
                ui_instance.notify(f"  : {e}", type="negative")

        #     
        broker_select.on("change", load_instruments)

        #  
        with ui_instance.card().classes("w-full p-4 mb-6"):
            ui_instance.label(" ").classes(
                "text-lg font-semibold text-gray-800 mb-4"
            )

            #   
            with ui_instance.card().classes(
                "w-full p-4 mb-4 bg-blue-50 border-l-4 border-blue-500"
            ):
                ui_instance.label("??  ").classes(
                    "text-lg font-semibold text-blue-800 mb-3"
                )

                #  
                with ui_instance.row().classes("w-full gap-2 mb-3"):
                    search_input = ui_instance.input(
                        label=" ",
                        placeholder="    (: SBER, )",
                    ).classes("flex-1")

                    #   
                    with ui_instance.row().classes("w-full gap-2"):
                        search_all_btn = ui_instance.button(
                            "??   ", icon="search"
                        ).classes(
                            "flex-1 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg"
                        )

                        auto_load_btn = ui_instance.button(
                            "? ", icon="download"
                        ).classes(
                            "flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg"
                        )

                        #      
                        search_all_btn.on("click", lambda: search_all_tinkoff_stocks())
                        auto_load_btn.on("click", lambda: auto_load_all_stocks())

                #  
                search_results_container = ui_instance.column().classes("w-full")

                #  
                selected_stock_container = ui_instance.column().classes("w-full mt-3")

                def search_stocks():
                    query = search_input.value.lower().strip()
                    if not query:
                        search_results_container.clear()
                        return

                    try:
                        #     
                        instruments = stock_service.get_broker_instruments("tinkoff")
                        matching_instruments = []

                        for instrument in instruments:
                            if (
                                query in instrument.ticker.lower()
                                or query in instrument.name.lower()
                            ):
                                matching_instruments.append(instrument)

                        #    ,   MOEX
                        if len(matching_instruments) < 5:
                            try:
                                all_stocks = stock_service.get_all_tinkoff_stocks()
                                for stock in all_stocks:
                                    if (
                                        query in stock["ticker"].lower()
                                        or query in stock["name"].lower()
                                    ):
                                        #     MOEX 
                                        from app.models.broker_models import (
                                            StockInstrument,
                                        )

                                        moex_instrument = StockInstrument(
                                            ticker=stock["ticker"],
                                            name=stock["name"],
                                            sector=stock.get("sector", ""),
                                            currency=stock.get("currency", "RUB"),
                                            lot_size=stock.get("lot_size", 1),
                                            broker_id="tinkoff",
                                        )
                                        matching_instruments.append(moex_instrument)
                            except Exception as e:
                                logger.warning(f"   MOEX: {e}")

                        #   15 
                        matching_instruments = matching_instruments[:15]

                        search_results_container.clear()

                        if matching_instruments:
                            with search_results_container:
                                ui_instance.label(
                                    f" {len(matching_instruments)} :"
                                ).classes("text-sm text-gray-600 mb-2")

                                for instrument in matching_instruments:
                                    with ui_instance.row().classes(
                                        "w-full p-2 bg-white rounded border hover:bg-blue-50 cursor-pointer"
                                    ):
                                        ui_instance.label(f"?? {instrument.ticker}").classes(
                                            "font-bold text-blue-600 w-20"
                                        )
                                        ui_instance.label(f"{instrument.name}").classes(
                                            "flex-1 text-gray-800"
                                        )
                                        ui_instance.label(
                                            f"{instrument.sector or 'N/A'}"
                                        ).classes("text-sm text-gray-500 w-32")

                                        def select_instrument(inst=instrument):
                                            ticker_input.value = inst.ticker
                                            selected_stock_container.clear()
                                            with selected_stock_container:
                                                with ui_instance.row().classes(
                                                    "w-full p-3 bg-green-50 rounded border border-green-200"
                                                ):
                                                    ui_instance.icon("check_circle").classes(
                                                        "text-green-600 text-xl mr-2"
                                                    )
                                                    ui_instance.label(
                                                        f": {inst.ticker} - {inst.name}"
                                                    ).classes(
                                                        "text-green-800 font-medium"
                                                    )
                                            search_results_container.clear()

                                        ui_instance.button("", icon="add").classes(
                                            "px-3 py-1 bg-blue-600 text-white text-xs"
                                        ).on("click", select_instrument)
                        else:
                            with search_results_container:
                                ui_instance.label("  ").classes(
                                    "text-gray-500 italic"
                                )

                    except Exception as e:
                        logger.error(f"  : {e}")
                        ui_instance.notify(f" : {e}", type="negative")

                def search_all_tinkoff_stocks():
                    """    -  """
                    try:
                        print("[DEBUG]  search_all_tinkoff_stocks")

                        #   
                        search_all_btn.loading = True
                        ui_instance.notify(" ...", type="info")

                        #  
                        all_tinkoff_stocks = stock_service.get_all_tinkoff_stocks()
                        print(f"[DEBUG]  {len(all_tinkoff_stocks)} ")

                        if not all_tinkoff_stocks:
                            ui_instance.notify("   ", type="negative")
                            return

                        #  
                        ui_instance.notify(
                            f" {len(all_tinkoff_stocks)} !",
                            type="positive",
                        )

                        #     
                        search_results_container.clear()

                        #     
                        with search_results_container:
                            # 
                            ui_instance.label(
                                f" {len(all_tinkoff_stocks)} :"
                            ).classes("text-lg font-semibold mb-3 text-gray-800")

                            #   (  15)
                            for i, stock in enumerate(all_tinkoff_stocks[:15]):
                                with ui_instance.row().classes(
                                    "w-full p-3 bg-gray-50 rounded mb-2 hover:bg-gray-100 transition-colors"
                                ):
                                    #   
                                    ui_instance.label(f"{i+1}. {stock['ticker']}").classes(
                                        "font-bold w-24 text-blue-600"
                                    )

                                    # 
                                    ui_instance.label(f"{stock['name']}").classes(
                                        "flex-1 text-gray-700"
                                    )

                                    #  ( )
                                    if stock.get("sector"):
                                        ui_instance.label(f"[{stock['sector']}]").classes(
                                            "text-xs text-gray-500"
                                        )

                                    #  
                                    def make_select_handler(s=stock):
                                        def select_stock():
                                            ticker_input.value = s["ticker"]
                                            ui_instance.notify(
                                                f": {s['ticker']}",
                                                type="positive",
                                            )

                                        return select_stock

                                    ui_instance.button("").classes(
                                        "px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded"
                                    ).on("click", make_select_handler())

                            #    
                            if len(all_tinkoff_stocks) > 15:
                                ui_instance.label(
                                    f"...   {len(all_tinkoff_stocks) - 15} "
                                ).classes("text-sm text-gray-500 italic mt-2")

                        print("[DEBUG]   ")

                    except Exception as e:
                        print(f"[DEBUG]   search_all_tinkoff_stocks: {e}")
                        ui_instance.notify(f": {e}", type="negative")
                    finally:
                        #   
                        search_all_btn.loading = False

                def auto_load_all_stocks():
                    """      -  """
                    try:
                        print("[DEBUG]  auto_load_all_stocks")

                        #   
                        auto_load_btn.loading = True
                        ui_instance.notify(" ...", type="info")

                        #     MOEX
                        all_stocks = stock_service.get_all_tinkoff_stocks()
                        print(f"[DEBUG]  {len(all_stocks)}   ")

                        if not all_stocks:
                            ui_instance.notify(
                                "     MOEX", type="negative"
                            )
                            return

                        ui_instance.notify(
                            f" {len(all_stocks)}   ",
                            type="info",
                        )

                        #     
                        loaded_count = 0
                        skipped_count = 0

                        for stock in all_stocks:
                            try:
                                # ,     
                                existing = stock_service.get_broker_instruments(
                                    "tinkoff"
                                )
                                if not any(
                                    instr.ticker == stock["ticker"]
                                    for instr in existing
                                ):
                                    #   
                                    from datetime import datetime

                                    from sqlmodel import Session

                                    from app.models.broker_models import StockInstrument
                                    from app.storage.db import engine

                                    with Session(engine) as session:
                                        new_instrument = StockInstrument(
                                            ticker=stock["ticker"],
                                            name=stock["name"],
                                            sector=stock.get("sector", ""),
                                            currency=stock.get("currency", "RUB"),
                                            lot_size=stock.get("lot_size", 1),
                                            broker_id="tinkoff",
                                            is_active=True,
                                            created_at=datetime.now(),
                                        )
                                        session.add(new_instrument)
                                        session.commit()
                                        loaded_count += 1
                                else:
                                    skipped_count += 1

                            except Exception as e:
                                print(f"[DEBUG]   {stock['ticker']}: {e}")
                                continue

                        #  
                        ui_instance.notify(
                            f" ! : {loaded_count}, : {skipped_count}",
                            type="positive",
                        )

                        print(
                            f"[DEBUG]  : {loaded_count} , {skipped_count} "
                        )

                    except Exception as e:
                        print(f"[DEBUG]   auto_load_all_stocks: {e}")
                        ui_instance.notify(f" : {e}", type="negative")
                    finally:
                        #   
                        auto_load_btn.loading = False

                search_input.on("input", search_stocks)

                #    
                ui_instance.label("??  :").classes(
                    "text-sm font-medium text-gray-700 mt-4 mb-2"
                )

                popular_stocks = [
                    ("SBER", "", "??"),
                    ("GAZP", "", "?"),
                    ("LKOH", "", "???"),
                    ("YNDX", "", "??"),
                    ("NVTK", "", "?"),
                    ("ROSN", "", "???"),
                ]

                with ui_instance.row().classes("flex-wrap gap-2"):
                    for ticker, name, icon in popular_stocks:

                        def quick_select(t=ticker, n=name, i=icon):
                            ticker_input.value = t
                            selected_stock_container.clear()
                            with selected_stock_container:
                                with ui_instance.row().classes(
                                    "w-full p-3 bg-green-50 rounded border border-green-200"
                                ):
                                    ui_instance.icon("check_circle").classes(
                                        "text-green-600 text-xl mr-2"
                                    )
                                    ui_instance.label(f": {t} - {n}").classes(
                                        "text-green-800 font-medium"
                                    )
                            search_results_container.clear()

                        ui_instance.button(f"{icon} {ticker}", icon="add").classes(
                            "px-3 py-1 bg-blue-100 hover:bg-blue-200 text-blue-800 text-xs rounded"
                        ).on("click", quick_select)

            with ui_instance.grid(columns=2).classes("gap-4 w-full"):
                #  (  )
                ticker_input = ui_instance.input(
                    label=" ",
                    placeholder="       (: QIWI, AAPL)",
                ).classes("w-full")

                #      
                ui_instance.label(
                    "??      -    "
                ).classes("text-xs text-blue-600 italic mt-1")

                # 
                quantity_input = (
                    ui_instance.input(label=" ", value="1")
                    .classes("w-full")
                    .props("type=number min=1")
                )

                # 
                price_input = (
                    ui_instance.input(label="  ", value="0.00")
                    .classes("w-full")
                    .props("type=number step=0.01 min=0")
                )

                # 
                commission_input = (
                    ui_instance.input(label="", value="0.00")
                    .classes("w-full")
                    .props("type=number step=0.01 min=0")
                )

                #  
                type_select = ui_instance.select(
                    options={"buy": "", "sell": ""},
                    label=" ",
                    value="buy",
                ).classes("w-full")

                # 
                date_input = (
                    ui_instance.input(label=" ").classes("w-full").props("type=date")
                )

            #    
            def get_current_price():
                ticker = ticker_input.value
                broker_id = broker_select.value

                if not ticker or not broker_id:
                    ui_instance.notify("    ", type="warning")
                    return

                try:
                    price = stock_service.get_current_price(broker_id, ticker)
                    if price:
                        price_input.value = f"{price:.2f}"
                        ui_instance.notify(
                            f"  {ticker}: {price:.2f} ?", type="positive"
                        )
                    else:
                        ui_instance.notify(f"  {ticker}  ", type="warning")
                except Exception as e:
                    logger.error(f"  : {e}")
                    ui_instance.notify(f"  : {e}", type="negative")

            ui_instance.button("??   ", icon="attach_money").classes(
                "px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg mb-4"
            ).on("click", get_current_price)

            #  
            def add_position():
                try:
                    transaction = StockTransactionIn(
                        ticker=ticker_input.value,
                        broker_id=broker_select.value,
                        quantity=int(quantity_input.value),
                        price=float(price_input.value),
                        commission=float(commission_input.value),
                        transaction_type=type_select.value,
                        transaction_date=date_input.value if date_input.value else None,
                    )

                    success = stock_service.add_stock_transaction(transaction)
                    if success:
                        ui_instance.notify(
                            f"[OK]  {transaction.ticker}  ",
                            type="positive",
                        )
                        #  
                        ticker_input.value = ""
                        quantity_input.value = "1"
                        price_input.value = "0.00"
                        commission_input.value = "0.00"
                        load_positions()
                    else:
                        ui_instance.notify("[ERROR]   ", type="negative")

                except Exception as e:
                    logger.error(f"  : {e}")
                    ui_instance.notify(f"  : {e}", type="negative")

            ui_instance.button("?  ", icon="add").classes(
                "px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg"
            ).on("click", add_position)

        #  
        positions_container = ui_instance.column().classes("w-full")

        def load_positions():
            try:
                positions = stock_service.calculate_stock_positions()

                #  
                positions_container.clear()

                with positions_container:
                    ui_instance.label(f"  ({len(positions)})").classes(
                        "text-lg font-semibold text-gray-800 mb-4"
                    )

                    if positions:
                        columns = [
                            {
                                "name": "ticker",
                                "label": "",
                                "field": "ticker",
                                "align": "left",
                            },
                            {
                                "name": "broker",
                                "label": "",
                                "field": "broker_name",
                                "align": "left",
                            },
                            {
                                "name": "quantity",
                                "label": "",
                                "field": "quantity",
                                "align": "right",
                            },
                            {
                                "name": "avg_price",
                                "label": ". ",
                                "field": "average_price",
                                "align": "right",
                            },
                            {
                                "name": "current_price",
                                "label": "",
                                "field": "current_price",
                                "align": "right",
                            },
                            {
                                "name": "value",
                                "label": "",
                                "field": "total_value",
                                "align": "right",
                            },
                            {
                                "name": "pnl",
                                "label": "P&L",
                                "field": "unrealized_pnl",
                                "align": "right",
                            },
                            {
                                "name": "pnl_percent",
                                "label": "P&L %",
                                "field": "unrealized_pnl_percent",
                                "align": "right",
                            },
                            {
                                "name": "first_purchase",
                                "label": " ",
                                "field": "first_purchase_date",
                                "align": "center",
                            },
                            {
                                "name": "transactions",
                                "label": "",
                                "field": "transactions_count",
                                "align": "center",
                            },
                            {
                                "name": "actions",
                                "label": "",
                                "field": "actions",
                                "align": "center",
                            },
                        ]

                        rows = []
                        for position in positions:
                            #    
                            first_purchase_str = "-"
                            if position.first_purchase_date:
                                first_purchase_str = (
                                    position.first_purchase_date.strftime("%d.%m.%Y")
                                )

                            rows.append(
                                {
                                    "ticker": position.ticker,
                                    "broker_name": position.broker_name,
                                    "quantity": f"{position.quantity:,}",
                                    "average_price": f"{position.average_price:.2f} ?",
                                    "current_price": (
                                        f"{position.current_price:.2f} ?"
                                        if position.current_price
                                        else "-"
                                    ),
                                    "total_value": (
                                        f"{position.total_value:.2f} ?"
                                        if position.total_value
                                        else "-"
                                    ),
                                    "unrealized_pnl": (
                                        f"{position.unrealized_pnl:.2f} ?"
                                        if position.unrealized_pnl
                                        else "-"
                                    ),
                                    "unrealized_pnl_percent": (
                                        f"{position.unrealized_pnl_percent:.2f}%"
                                        if position.unrealized_pnl_percent
                                        else "-"
                                    ),
                                    "first_purchase_date": first_purchase_str,
                                    "transactions_count": str(
                                        position.transactions_count or 0
                                    ),
                                    "actions": f"edit_{position.ticker}_{position.broker_id}",  #   
                                }
                            )

                        #      
                        for position in positions:
                            with ui_instance.card().classes(
                                "w-full p-3 mb-2 border-l-4 border-blue-500"
                            ):
                                #     
                                with ui_instance.row().classes(
                                    "w-full justify-between items-center"
                                ):
                                    #   -  
                                    with ui_instance.row().classes("items-center gap-4 flex-1"):
                                        #   
                                        with ui_instance.column().classes("items-start"):
                                            ui_instance.label(f"?? {position.ticker}").classes(
                                                "text-lg font-bold text-blue-600"
                                            )
                                            ui_instance.label(f"{position.broker_name}").classes(
                                                "text-xs text-gray-500"
                                            )

                                        #    
                                        with ui_instance.column().classes("items-center"):
                                            ui_instance.label(
                                                f"{position.quantity:,} "
                                            ).classes("text-sm font-semibold")
                                            ui_instance.label(
                                                f"@{position.average_price:.2f} ?"
                                            ).classes("text-xs text-gray-600")

                                        #    
                                        with ui_instance.column().classes("items-center"):
                                            current_price_str = (
                                                f"{position.current_price:.2f} ?"
                                                if position.current_price
                                                else "N/A"
                                            )
                                            ui_instance.label(current_price_str).classes(
                                                "text-sm font-medium"
                                            )
                                            ui_instance.label(
                                                f"{position.total_value:.2f} ?"
                                            ).classes(
                                                "text-sm font-semibold text-green-600"
                                            )

                                        # P&L
                                        with ui_instance.column().classes("items-center"):
                                            pnl_color = (
                                                "text-green-600"
                                                if position.unrealized_pnl
                                                and position.unrealized_pnl > 0
                                                else "text-red-600"
                                            )
                                            ui_instance.label(
                                                f"{position.unrealized_pnl:.2f} ?"
                                            ).classes(
                                                f"text-sm font-semibold {pnl_color}"
                                            )
                                            ui_instance.label(
                                                f"{position.unrealized_pnl_percent:.2f}%"
                                            ).classes(f"text-xs {pnl_color}")

                                        #  
                                        with ui_instance.column().classes("items-center"):
                                            first_purchase_str = (
                                                position.first_purchase_date.strftime(
                                                    "%d.%m.%Y"
                                                )
                                                if position.first_purchase_date
                                                else "N/A"
                                            )
                                            ui_instance.label(f" {first_purchase_str}").classes(
                                                "text-xs text-gray-500"
                                            )
                                            ui_instance.label(
                                                f"{position.transactions_count or 0} "
                                            ).classes("text-xs text-gray-500")

                                    #   -  
                                    with ui_instance.row().classes("gap-1"):
                                        ui_instance.button("??", icon="edit").classes(
                                            "px-2 py-1 bg-blue-600 text-white text-xs"
                                        ).on(
                                            "click", lambda p=position: edit_position(p)
                                        )
                                        ui_instance.button("??", icon="history").classes(
                                            "px-2 py-1 bg-green-600 text-white text-xs"
                                        ).on(
                                            "click",
                                            lambda p=position: show_position_history(p),
                                        )
                                        ui_instance.button("??", icon="sell").classes(
                                            "px-2 py-1 bg-red-600 text-white text-xs"
                                        ).on(
                                            "click", lambda p=position: sell_position(p)
                                        )

                        # 
                        total_value = sum(p.total_value or 0 for p in positions)
                        total_pnl = sum(p.unrealized_pnl or 0 for p in positions)

                        with ui_instance.row().classes("gap-4 mt-4"):
                            ui_instance.badge(f" : {total_value:.2f} ?").classes(
                                "px-3 py-1 bg-blue-100 text-blue-800"
                            )
                            ui_instance.badge(f" P&L: {total_pnl:.2f} ?").classes(
                                f"px-3 py-1 {'bg-green-100 text-green-800' if total_pnl >= 0 else 'bg-red-100 text-red-800'}"
                            )
                    else:
                        ui_instance.label("  ").classes("text-gray-500 italic")

            except Exception as e:
                logger.error(f"  : {e}")
                ui_instance.notify(f"  : {e}", type="negative")

        #    
        load_positions()

        #     
        def edit_position(position):
            """ """
            with ui_instance.dialog() as dialog, ui_instance.card().classes("w-full max-w-lg"):
                ui_instance.label(f"  {position.ticker}").classes(
                    "text-lg font-semibold mb-4"
                )

                #    
                with ui_instance.card().classes("w-full p-3 mb-4 bg-gray-50"):
                    with ui_instance.row().classes("w-full justify-between text-sm"):
                        ui_instance.label(f": {position.quantity:,} ")
                        ui_instance.label(f" : {position.average_price:.2f} ?")
                        ui_instance.label(f": {position.total_value:.2f} ?")

                #     
                with ui_instance.tabs().classes("w-full mb-4") as tabs:
                    buy_tab = ui_instance.tab("?? ")
                    sell_tab = ui_instance.tab("?? ")

                with ui_instance.tab_panels(tabs, value=buy_tab).classes("w-full"):
                    #  
                    with ui_instance.tab_panel(buy_tab):
                        with ui_instance.column().classes("gap-3 w-full"):
                            ui_instance.label("  ").classes(
                                "text-md font-medium text-green-600"
                            )

                            buy_quantity_input = ui_instance.input(
                                label="  ",
                                placeholder=" ",
                            ).classes("w-full")

                            buy_price_input = ui_instance.input(
                                label="  ", placeholder=" "
                            ).classes("w-full")

                            buy_commission_input = ui_instance.input(
                                label="", value="0.00"
                            ).classes("w-full")

                            buy_date_input = (
                                ui_instance.input(
                                    label=" ",
                                    value=datetime.now().strftime("%Y-%m-%d"),
                                )
                                .classes("w-full")
                                .props("type=date")
                            )

                            #   
                            ui_instance.label(" :").classes(
                                "text-xs text-gray-600 mt-2"
                            )

                            #      
                            if position.current_price:
                                ui_instance.button(
                                    f"??     ({position.current_price:.2f} ?)",
                                    icon="refresh",
                                ).classes("w-full bg-green-100 text-green-800").tooltip(
                                    "   "
                                ).on(
                                    "click",
                                    lambda: set_buy_price(
                                        position.current_price, buy_price_input
                                    ),
                                )

                            #    
                            with ui_instance.row().classes("w-full gap-2 mt-2"):
                                ui_instance.button("+1", icon="add").classes(
                                    "flex-1 bg-green-100 text-green-800"
                                ).tooltip(" 1  ").on(
                                    "click",
                                    lambda: buy_quantity_input.set_value("1"),
                                )
                                ui_instance.button("+10", icon="add").classes(
                                    "flex-1 bg-green-100 text-green-800"
                                ).tooltip(" 10  ").on(
                                    "click",
                                    lambda: buy_quantity_input.set_value("10"),
                                )

                    #  
                    with ui_instance.tab_panel(sell_tab):
                        with ui_instance.column().classes("gap-3 w-full"):
                            ui_instance.label(" ").classes(
                                "text-md font-medium text-red-600"
                            )

                            sell_quantity_input = ui_instance.input(
                                label="  ",
                                value=str(position.quantity),
                                placeholder=f": {position.quantity} ",
                            ).classes("w-full")

                            sell_price_input = ui_instance.input(
                                label=" ", placeholder=" "
                            ).classes("w-full")

                            sell_commission_input = ui_instance.input(
                                label="", value="0.00"
                            ).classes("w-full")

                            sell_date_input = (
                                ui_instance.input(
                                    label=" ",
                                    value=datetime.now().strftime("%Y-%m-%d"),
                                )
                                .classes("w-full")
                                .props("type=date")
                            )

                            #     
                            ui_instance.label("  :").classes(
                                "text-xs text-gray-600 mt-2"
                            )
                            with ui_instance.row().classes("w-full gap-2"):
                                ui_instance.button("50%", icon="percent").classes(
                                    "flex-1 bg-red-100 text-red-800"
                                ).tooltip("    ").on(
                                    "click",
                                    lambda: set_sell_quantity(
                                        position.quantity // 2, sell_quantity_input
                                    ),
                                )
                                ui_instance.button("100%", icon="all_inclusive").classes(
                                    "flex-1 bg-red-100 text-red-800"
                                ).tooltip("  ").on(
                                    "click",
                                    lambda: set_sell_quantity(
                                        position.quantity, sell_quantity_input
                                    ),
                                )

                #  
                with ui_instance.row().classes("w-full gap-2 mt-4"):
                    ui_instance.button("?? ", icon="shopping_cart").classes(
                        "flex-1 bg-green-600 text-white"
                    ).on(
                        "click",
                        lambda: save_transaction(
                            position,
                            "buy",
                            buy_quantity_input.value,
                            buy_price_input.value,
                            buy_commission_input.value,
                            buy_date_input.value,
                            dialog,
                        ),
                    )
                    ui_instance.button("?? ", icon="sell").classes(
                        "flex-1 bg-red-600 text-white"
                    ).on(
                        "click",
                        lambda: save_transaction(
                            position,
                            "sell",
                            sell_quantity_input.value,
                            sell_price_input.value,
                            sell_commission_input.value,
                            sell_date_input.value,
                            dialog,
                        ),
                    )
                    ui_instance.button("", icon="cancel").classes(
                        "flex-1 bg-gray-500 text-white"
                    ).on("click", dialog.close)

            dialog.open()

        def set_buy_price(price, price_input):
            """  """
            price_input.value = str(price)

        def set_sell_quantity(quantity, quantity_input):
            """  """
            quantity_input.value = str(quantity)

        def save_transaction(
            position, transaction_type, quantity, price, commission, date, dialog
        ):
            """ """
            try:
                if not quantity or not price:
                    ui_instance.notify("   ", type="warning")
                    return

                transaction = StockTransactionIn(
                    ticker=position.ticker,
                    broker_id=position.broker_id,
                    quantity=int(quantity),
                    price=float(price),
                    commission=float(commission or 0),
                    transaction_type=transaction_type,
                    transaction_date=date if date else None,
                )

                success = stock_service.add_stock_transaction(transaction)
                if success:
                    action_text = "" if transaction_type == "buy" else ""
                    ui_instance.notify(
                        f"[OK] {action_text.capitalize()} {position.ticker} ",
                        type="positive",
                    )
                    dialog.close()
                    load_positions()
                else:
                    ui_instance.notify("[ERROR]   ", type="negative")

            except Exception as e:
                logger.error(f"  : {e}")
                ui_instance.notify(f": {e}", type="negative")

        def save_position_edit(
            position, quantity, price, commission, transaction_type, date, dialog
        ):
            """  """
            try:
                transaction = StockTransactionIn(
                    ticker=position.ticker,
                    broker_id=position.broker_id,
                    quantity=int(quantity),
                    price=float(price),
                    commission=float(commission),
                    transaction_type=transaction_type,
                    transaction_date=date if date else None,
                )

                success = stock_service.add_stock_transaction(transaction)
                if success:
                    ui_instance.notify(
                        f"[OK]  {position.ticker} ", type="positive"
                    )
                    dialog.close()
                    load_positions()
                else:
                    ui_instance.notify("[ERROR]   ", type="negative")

            except Exception as e:
                logger.error(f"  : {e}")
                ui_instance.notify(f" : {e}", type="negative")

        def show_position_history(position):
            """    """
            with ui_instance.dialog() as dialog, ui_instance.card().classes("w-full max-w-5xl"):
                ui_instance.label(f"  {position.ticker}").classes(
                    "text-lg font-semibold mb-4"
                )

                try:
                    #      
                    transactions = stock_service.get_stock_transactions()
                    position_transactions = [
                        t
                        for t in transactions
                        if t.ticker == position.ticker
                        and t.broker_id == position.broker_id
                    ]

                    if position_transactions:
                        #    ( )
                        position_transactions.sort(
                            key=lambda x: x.transaction_date or datetime.min,
                            reverse=True,
                        )

                        #   
                        with ui_instance.table().classes("w-full text-sm"):
                            # 
                            with ui_instance.table_head():
                                with ui_instance.table_row():
                                    ui_instance.table_header("").classes("text-left")
                                    ui_instance.table_header("").classes("text-center")
                                    ui_instance.table_header("").classes("text-right")
                                    ui_instance.table_header("").classes("text-right")
                                    ui_instance.table_header("").classes("text-right")
                                    ui_instance.table_header("").classes("text-right")
                                    ui_instance.table_header("").classes("text-right")

                            #  
                            with ui_instance.table_body():
                                running_quantity = 0
                                for t in position_transactions:
                                    #    
                                    if t.transaction_type == "buy":
                                        running_quantity += t.quantity
                                    else:
                                        running_quantity -= t.quantity

                                    total_amount = t.quantity * t.price + (
                                        t.commission
                                        if t.transaction_type == "buy"
                                        else -t.commission
                                    )

                                    with ui_instance.table_row():
                                        # 
                                        date_str = (
                                            t.transaction_date.strftime(
                                                "%d.%m.%Y %H:%M"
                                            )
                                            if t.transaction_date
                                            else ""
                                        )
                                        ui_instance.table_cell(date_str).classes("text-xs")

                                        #  
                                        type_color = (
                                            "text-green-600"
                                            if t.transaction_type == "buy"
                                            else "text-red-600"
                                        )
                                        type_text = (
                                            "?? "
                                            if t.transaction_type == "buy"
                                            else "?? "
                                        )
                                        ui_instance.table_cell(type_text).classes(
                                            f"text-center font-medium {type_color}"
                                        )

                                        # 
                                        ui_instance.table_cell(f"{t.quantity:,}").classes(
                                            "text-right"
                                        )

                                        # 
                                        ui_instance.table_cell(f"{t.price:.2f} ?").classes(
                                            "text-right"
                                        )

                                        # 
                                        ui_instance.table_cell(f"{t.commission:.2f} ?").classes(
                                            "text-right text-gray-500"
                                        )

                                        # 
                                        amount_color = (
                                            "text-green-600"
                                            if t.transaction_type == "buy"
                                            else "text-red-600"
                                        )
                                        ui_instance.table_cell(f"{total_amount:.2f} ?").classes(
                                            f"text-right font-medium {amount_color}"
                                        )

                                        # 
                                        ui_instance.table_cell(f"{running_quantity:,}").classes(
                                            "text-right font-semibold"
                                        )

                        #  
                        with ui_instance.card().classes("w-full p-3 mt-4 bg-gray-50"):
                            total_bought = sum(
                                t.quantity
                                for t in position_transactions
                                if t.transaction_type == "buy"
                            )
                            total_sold = sum(
                                t.quantity
                                for t in position_transactions
                                if t.transaction_type == "sell"
                            )
                            total_commission = sum(
                                t.commission for t in position_transactions
                            )

                            with ui_instance.row().classes("w-full justify-between text-sm"):
                                ui_instance.label(f" : {total_bought:,} ")
                                ui_instance.label(f" : {total_sold:,} ")
                                ui_instance.label(f" : {position.quantity:,} ")
                                ui_instance.label(f" : {total_commission:.2f} ?")
                    else:
                        ui_instance.label("   ").classes(
                            "text-gray-500 italic text-center py-8"
                        )

                except Exception as e:
                    logger.error(f"  : {e}")
                    ui_instance.notify(f"  : {e}", type="negative")
                    ui_instance.label(f": {e}").classes("text-red-500 text-center py-8")

                ui_instance.button("", icon="close").classes(
                    "w-full mt-4 bg-gray-500 text-white"
                ).on("click", dialog.close)

            dialog.open()

        def sell_position(position):
            """ """
            with ui_instance.dialog() as dialog, ui_instance.card().classes("w-full max-w-md"):
                ui_instance.label(f"  {position.ticker}").classes(
                    "text-lg font-semibold mb-4"
                )

                with ui_instance.column().classes("gap-3 w-full"):
                    ui_instance.label(f"  : {position.quantity} ")
                    ui_instance.label(f"  : {position.average_price:.2f} ?")

                    quantity_input = ui_instance.input(
                        label="  ", value=str(position.quantity)
                    ).classes("w-full")
                    price_input = ui_instance.input(
                        label=" ", placeholder=" "
                    ).classes("w-full")
                    commission_input = ui_instance.input(label="", value="0.00").classes(
                        "w-full"
                    )
                    date_input = (
                        ui_instance.input(
                            label=" ",
                            value=datetime.now().strftime("%Y-%m-%d"),
                        )
                        .classes("w-full")
                        .props("type=date")
                    )

                    with ui_instance.row().classes("w-full gap-2"):
                        ui_instance.button("", icon="sell").classes(
                            "flex-1 bg-red-600 text-white"
                        ).on(
                            "click",
                            lambda: execute_sell(
                                position,
                                quantity_input.value,
                                price_input.value,
                                commission_input.value,
                                date_input.value,
                                dialog,
                            ),
                        )
                        ui_instance.button("", icon="cancel").classes(
                            "flex-1 bg-gray-500 text-white"
                        ).on("click", dialog.close)

            dialog.open()

        def execute_sell(position, quantity, price, commission, date, dialog):
            """ """
            try:
                transaction = StockTransactionIn(
                    ticker=position.ticker,
                    broker_id=position.broker_id,
                    quantity=int(quantity),
                    price=float(price),
                    commission=float(commission),
                    transaction_type="sell",
                    transaction_date=date if date else None,
                )

                success = stock_service.add_stock_transaction(transaction)
                if success:
                    ui_instance.notify(
                        f"[OK]  {position.ticker} ", type="positive"
                    )
                    dialog.close()
                    load_positions()
                else:
                    ui_instance.notify("[ERROR]  ", type="negative")

            except Exception as e:
                logger.error(f" : {e}")
                ui_instance.notify(f" : {e}", type="negative")
