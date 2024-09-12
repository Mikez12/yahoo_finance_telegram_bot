from matplotlib import pyplot as plt
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import CommandHandler, CallbackQueryHandler, Application, ContextTypes
import yfinance as yf
import mplfinance as mpf
import datetime
import os

# Replace 'YOUR_API_TOKEN' with your actual bot token from BotFather
API_TOKEN = 'YOUR_API_TOKEN'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Welcome to the Simple Telegram Bot!")
    await show_option_buttons(update, context)


async def show_option_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Option 1", callback_data='button_1')],
        [InlineKeyboardButton("Option 2", callback_data='button_2')],
        [InlineKeyboardButton("Option 3", callback_data='button_3')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Please choose an option:', reply_markup=reply_markup)


async def button_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(f'You selected option: {query.data.split("_")[1]}')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'I can respond to the following commands:\n/start - Start the bot\n/help - Get help information\n/stock [ticker] - Get stock price and graph\n/stock_candlestick [ticker] - Get stock price and candlestick chart'
    )


# Command to fetch stock price and candlestick graph
async def stock_candlestick_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # Get the ticker from the user input
        ticker = context.args[0].upper()
        stock = yf.Ticker(ticker)

        # Fetch historical data for the last 14 days
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=14)
        data = stock.history(start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))

        # Check if data is available
        if data.empty:
            await update.message.reply_text(f"No data found for {ticker}. Please check the ticker symbol.")
            return

        # Get the latest price
        latest_price = data['Close'].iloc[-1]

        # Create a candlestick plot using mplfinance
        chart_filename = f'{ticker}_candlestick_chart.png'
        mpf.plot(data, type='candle', mav=(3, 6), volume=True, show_nontrading=True, savefig=chart_filename)

        # Send the stock price to the user
        await update.message.reply_text(f'The current price of {ticker} is ${latest_price:.2f}.')

        # Send the candlestick chart as an image
        with open(chart_filename, 'rb') as chart:
            await update.message.reply_photo(photo=InputFile(chart))

        # Send a link to the Yahoo Finance page for the ticker
        yahoo_finance_url = f'https://finance.yahoo.com/quote/{ticker}'
        await update.message.reply_text(f'View more details here: {yahoo_finance_url}')

        # Remove the image file after sending it
        os.remove(chart_filename)

    except IndexError:
        # Handle the case when no ticker is provided
        await update.message.reply_text('Please provide a valid ticker symbol. Usage: /stock_candlestick [ticker]')
    except Exception as e:
        # Handle any other exceptions
        await update.message.reply_text(f"An error occurred: {str(e)}")



# New command to fetch stock price and candlestick graph
async def stock_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # Get the ticker from the user input
        ticker = context.args[0].upper()
        stock = yf.Ticker(ticker)

        # Fetch historical data for the last 14 days
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=14)
        data = stock.history(start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))

        # Check if data is available
        if data.empty:
            await update.message.reply_text(f"No data found for {ticker}. Please check the ticker symbol.")
            return

        # Get the latest price
        latest_price = data['Close'].iloc[-1]

        # Create a candlestick plot
        fig, ax = plt.subplots(figsize=(10, 5))
        data['Date'] = data.index
        ax.plot(data.index, data['Close'], label='Close Price')

        # Customize the plot
        ax.set_title(f'{ticker} Price - Last 14 Days', fontsize=14)
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax.legend()

        # Save the plot to an image
        chart_filename = f'{ticker}_chart.png'
        plt.savefig(chart_filename)
        plt.close()

        # Send the stock price to the user
        await update.message.reply_text(f'The current price of {ticker} is ${latest_price:.2f}.')

        # Send the candlestick chart as an image
        with open(chart_filename, 'rb') as chart:
            await update.message.reply_photo(photo=InputFile(chart))

        # Send a link to the Yahoo Finance page for the ticker
        yahoo_finance_url = f'https://finance.yahoo.com/quote/{ticker}'
        await update.message.reply_text(f'View more details here: {yahoo_finance_url}')

        # Remove the image file after sending it
        os.remove(chart_filename)

    except IndexError:
        # Handle the case when no ticker is provided
        await update.message.reply_text('Please provide a valid ticker symbol. Usage: /stock [ticker]')
    except Exception as e:
        # Handle any other exceptions
        await update.message.reply_text(f"An error occurred: {str(e)}")


def main():
    # Create the Application instance
    application = Application.builder().token(API_TOKEN).build()

    # Register command and message handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('stock', stock_command))
    application.add_handler(CommandHandler('stock_candlestick', stock_candlestick_command))

    # Register a CallbackQueryHandler to handle button selections
    application.add_handler(CallbackQueryHandler(button_selection_handler, pattern='^button_'))

    # Start the bot
    application.run_polling()


if __name__ == '__main__':
    main()
