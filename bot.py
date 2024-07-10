import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_polling
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Constants
API_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN_HERE'

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Cache for storing search results temporarily
search_results = {}

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    logging.info(f"Received command: {message.text}")
    await message.reply("Hi! I'm your bot. Use /search <movie_name> to search for a movie.")

async def fetch_imdb_data(url):
    logging.info(f"Fetching IMDb data for URL: {url}")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            page = await context.new_page()
            await page.goto(url)
            
            await page.wait_for_selector('h1', timeout=20000)  # Increased timeout

            content = await page.content()
            await browser.close()

            soup = BeautifulSoup(content, 'html.parser')
            title_tag = soup.find('title').text
            title, release_year = title_tag.split(' (')[0], title_tag.split(' (')[1].split(')')[0]
            formatted_title = f"{title} ({release_year})"

            rating = None
            rating_section = soup.find('div', attrs={"data-testid": "hero-rating-bar__aggregate-rating__score"})
            if rating_section:
                rating_value = rating_section.find('span').text.strip()
                rating = f"{rating_value}/10"

            genres = []
            genre_section = soup.find('div', attrs={"data-testid": "genres"})
            if genre_section:
                genre_elems = genre_section.find_all('span', class_='ipc-chip__text')
                genres = [f"#{genre.text.strip()}" for genre in genre_elems]
            formatted_genres = ', '.join(genres)

            cast = []
            cast_section = soup.find_all('a', attrs={"data-testid": "title-cast-item__actor"})
            for actor in cast_section:
                cast.append(actor.text.strip())
            formatted_cast = ', '.join(cast)

            plot_summary = None
            plot_section = soup.find('span', attrs={"data-testid": "plot-xl"})
            if plot_section:
                plot_summary = plot_section.text.strip()

            data = (
                f"**Title 🎬**: {formatted_title}\n\n"
                f"**Quality 💿**: 720p WEB\n\n"
                f"**Audio 🔊**: #Hindi #English\n\n"
                f"**Rating ⭐**: {rating}\n\n"
                f"**Genre 🎑**: {formatted_genres}\n\n"
                f"**Cast 🤹**: {formatted_cast}\n\n"
                f"**Story Line 📖**: {plot_summary}"
            )
            
            logging.info(f"Fetched data: {data}")
            return data
    except Exception as e:
        logging.error(f"Error fetching IMDb data: {e}")
        return None

@dp.message_handler(commands=['search'])
async def search_movie(message: types.Message):
    query = message.get_args()
    logging.info(f"Received search query: {query}")

    if not query:
        await message.reply("Please provide a movie name to search for. Usage: /search <movie_name>")
        return

    try:
        search_url = f"https://www.imdb.com/find?q={query.replace(' ', '+')}&s=tt"
        logging.info(f"Searching IMDb with URL: {search_url}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            page = await context.new_page()
            await page.goto(search_url)
            await page.wait_for_selector('.ipc-metadata-list-summary-item__t', timeout=20000)

            content = await page.content()
            await browser.close()

            soup = BeautifulSoup(content, 'html.parser')
            results = soup.select('.ipc-metadata-list-summary-item__t')
            logging.info(f"Found {len(results)} results")

            if not results:
                await message.reply("No results found.")
                return

            # Store the first 5 results in the cache
            search_results[message.from_user.id] = []
            for result in results[:5]:
                href = result.get('href')
                if href and href.startswith('/title/'):
                    search_results[message.from_user.id].append({
                        'text': result.text,
                        'href': f"https://www.imdb.com{href}"
                    })

            # Create inline keyboard buttons for the results
            buttons = []
            for i, result in enumerate(search_results[message.from_user.id]):
                buttons.append(types.InlineKeyboardButton(text=result['text'], callback_data=f"select_{i}"))
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)

            await message.reply("Select a movie:", reply_markup=keyboard)
            logging.info(f"Sent keyboard with {len(buttons)} buttons to user {message.from_user.id}")
            logging.info(f"Search results for user {message.from_user.id}: {search_results[message.from_user.id]}")

    except Exception as e:
        logging.error(f"Error handling search query: {e}")
        await message.reply("An error occurred while searching for the movie.")

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('select_'))
async def process_selection(callback_query: types.CallbackQuery):
    logging.info(f"Received callback query: {callback_query.data} from user {callback_query.from_user.id}")
    
    try:
        # Acknowledge the callback query immediately
        await bot.answer_callback_query(callback_query.id)
        
        # Send a message to indicate that the selection was received
        await bot.send_message(callback_query.from_user.id, f"You selected: {callback_query.data}")
        
        # Parse the selection
        index = int(callback_query.data.split('_')[1])
        user_id = callback_query.from_user.id

        logging.info(f"User {user_id} selected index {index}")
        logging.info(f"Current search results: {search_results.get(user_id, 'No results')}")

        if user_id not in search_results:
            await bot.send_message(callback_query.from_user.id, "No active search. Please start a new search.")
            return

        if index >= len(search_results[user_id]):
            await bot.send_message(callback_query.from_user.id, "Invalid selection.")
            return

        result = search_results[user_id][index]
        imdb_url = result['href']
        
        await bot.send_message(callback_query.from_user.id, f"Fetching details for: {result['text']}")
        logging.info(f"Fetching details for selected result: {imdb_url}")

        movie_data = await fetch_imdb_data(imdb_url)
        if movie_data:
            await bot.send_message(callback_query.from_user.id, movie_data, parse_mode="Markdown")
        else:
            await bot.send_message(callback_query.from_user.id, "Failed to fetch movie details.")

        # Clear the search results cache for the user
        search_results.pop(user_id, None)

    except Exception as e:
        logging.error(f"Error processing selection: {e}")
        await bot.send_message(callback_query.from_user.id, "An error occurred while processing your selection.")

async def on_startup(dp):
    logging.info("Bot is starting up")
    me = await bot.get_me()
    logging.info(f"Bot info: {me}")

if __name__ == '__main__':
    logging.info("Starting bot...")
    start_polling(dp, skip_updates=True, on_startup=on_startup)
