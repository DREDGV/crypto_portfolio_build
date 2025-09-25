def open_enhanced_add_dialog():
    """Простой диалог добавления сделки"""
    with ui.dialog() as dialog, ui.card().classes("min-w-[500px] max-w-[600px] p-6"):
        ui.label("Добавить новую сделку").classes("text-xl font-bold mb-4")
        
        # Простые поля формы
        coin = ui.input(label="Монета (например: BTC)", placeholder="BTC").classes("w-full mb-3")
        qty = ui.number(label="Количество", placeholder="0.0", format="%.8f").classes("w-full mb-3")
        price = ui.number(label="Цена за единицу", placeholder="0.0", format="%.2f").classes("w-full mb-3")
        source = ui.input(label="Источник (биржа)", placeholder="Binance").classes("w-full mb-3")
        
        # Простые селекты
        ttype = ui.select(
            options=["trade_buy", "trade_sell", "transfer_in", "transfer_out"],
            value="trade_buy",
            label="Тип операции"
        ).classes("w-full mb-3")
        
        strategy = ui.select(
            options=["long_term", "swing", "scalp", "arbitrage"],
            value="long_term", 
            label="Стратегия"
        ).classes("w-full mb-3")
        
        notes = ui.textarea(label="Заметки (необязательно)", placeholder="Дополнительная информация").classes("w-full mb-4")
        
        # Кнопки
        with ui.row().classes("gap-3 justify-end"):
            ui.button("Отмена").on("click", dialog.close)
            
            def on_add():
                try:
                    if not coin.value or not qty.value or not price.value or not source.value:
                        ui.notify("Заполните все обязательные поля", color="error")
                        return
                    
                    transaction_data = TransactionIn(
                        coin=coin.value.strip().upper(),
                        quantity=float(qty.value),
                        price=float(price.value),
                        type=ttype.value,
                        strategy=strategy.value,
                        source=source.value.strip(),
                        notes=notes.value.strip() if notes.value else None,
                    )
                    
                    result = add_transaction(transaction_data)
                    if result:
                        ui.notify("Сделка добавлена!", color="positive")
                        dialog.close()
                        ui.open("/")
                    else:
                        ui.notify("Ошибка добавления", color="error")
                        
                except Exception as e:
                    ui.notify(f"Ошибка: {e}", color="error")
            
            ui.button("Добавить", icon="add").classes("bg-green-500 text-white").on("click", on_add)
    
    dialog.open()


def create_compact_stat_card(title: str, value: str, subtitle: str, icon: str = "info"):
