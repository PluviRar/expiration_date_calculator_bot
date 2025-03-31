from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from datetime import datetime, timedelta

# Состояния для обработки диалога
WAITING_FOR_PRODUCTION_DATE = 1
WAITING_FOR_EXPIRY_DAYS = 2

# Функция для обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Запрашиваем дату производства товара
    await update.message.reply_text(
        "Введите дату производства товара в формате ДД.ММ.ГГГГ (например, 01.01.2023):"
    )

    # Устанавливаем состояние ожидания даты производства
    return WAITING_FOR_PRODUCTION_DATE

# Функция для обработки ввода даты производства
async def get_production_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text.strip()

    try:
        # Преобразуем введённую дату в объект datetime
        production_date = datetime.strptime(user_input, "%d.%m.%Y")
        context.user_data["production_date"] = production_date

        # Запрашиваем срок хранения товара
        await update.message.reply_text(
            "Введите срок хранения товара в днях (например, 90):"
        )

        # Устанавливаем состояние ожидания срока хранения
        return WAITING_FOR_EXPIRY_DAYS

    except ValueError:
        # Обработка ошибки, если дата введена некорректно
        await update.message.reply_text(
            "Некорректный формат даты. Введите дату в формате ДД.ММ.ГГГГ:"
        )
        return WAITING_FOR_PRODUCTION_DATE

# Функция для обработки ввода срока хранения
async def calculate_expiry_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text.strip()

    try:
        # Получаем срок хранения в днях
        expiry_days = int(user_input)
        if expiry_days <= 0:
            raise ValueError("Срок хранения должен быть положительным числом.")

        # Получаем дату производства из контекста
        production_date = context.user_data.get("production_date")

        # Рассчитываем дату окончания срока годности
        expiry_date = production_date + timedelta(days=expiry_days)

        # Форматируем дату для вывода
        formatted_expiry_date = expiry_date.strftime("%d.%m.%Y")

        # Отправляем результат пользователю
        await update.message.reply_text(
            f"Дата окончания срока годности: {formatted_expiry_date}"
        )

        # Предлагаем начать заново
        await update.message.reply_text(
            "Хотите рассчитать ещё одну дату? Введите новую дату производства в формате ДД.ММ.ГГГГ:"
        )

        # Возвращаемся к состоянию ожидания даты производства
        return WAITING_FOR_PRODUCTION_DATE

    except ValueError:
        # Обработка ошибки, если введено некорректное значение
        await update.message.reply_text(
            "Пожалуйста, введите корректное количество дней (положительное число)."
        )
        return WAITING_FOR_EXPIRY_DAYS

# Основная функция для запуска бота
def main() -> None:
    # Вставьте ваш токен бота здесь
    token = "7799224779:AAERu7X4IGLrejgxp9ZDQyhFWbbMjSWRWkA"

    # Создаем объект Application
    application = Application.builder().token(token).build()

    # Создаем обработчик диалога
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAITING_FOR_PRODUCTION_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_production_date)],
            WAITING_FOR_EXPIRY_DAYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, calculate_expiry_date)],
        },
        fallbacks=[],
    )

    # Регистрируем обработчик диалога
    application.add_handler(conv_handler)

    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()