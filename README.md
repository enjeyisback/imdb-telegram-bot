# IMDb Telegram Bot

This is a Telegram bot that allows users to search for movies on IMDb and get detailed information about them, including the title, quality, audio, rating, genre, cast, and story line.

## Features

- Search for movies on IMDb using the `/search` command.
- Get detailed information about a selected movie, including:
  - Title 🎬
  - Quality 💿
  - Audio 🔊
  - Rating ⭐
  - Genre 🎑
  - Cast 🤹
  - Story Line 📖

## Prerequisites

- Python 3.7+
- Telegram bot token (you can obtain one by creating a new bot via [BotFather](https://core.telegram.org/bots#botfather) on Telegram)

## Setup

1. Clone this repository:

    ```sh
    git clone https://github.com/yourusername/imdb-telegram-bot.git
    cd imdb-telegram-bot
    ```

2. Install the required dependencies:

    ```sh
    pip install -r requirements.txt
    ```

3. Replace `'YOUR_TELEGRAM_BOT_TOKEN_HERE'` in `bot.py` with your actual Telegram bot token.

4. Run the bot:

    ```sh
    python bot.py
    ```

## Usage

1. Start the bot by sending `/start` or `/help` to your bot on Telegram.
2. Use the `/search <movie_name>` command to search for a movie on IMDb. For example:

    ```sh
    /search The Lord of the Rings
    ```

3. The bot will return the first 5 search results as buttons. Click on a button to get detailed information about the selected movie.

## Example

```sh
/search The Lord of the Rings
You will receive the following response:
Select a movie:
1. The Lord of the Rings: The Fellowship of the Ring
2. The Lord of the Rings: The Two Towers
3. The Lord of the Rings: The Return of the King
4. The Lord of the Rings: The Rings of Power
5. The Lord of the Rings: The War of the Rohirrim
Click on a movie title to get detailed information.

Detailed Information Format
The detailed information will be displayed in the following format:
**Title 🎬**: The Lord of the Rings: The Fellowship of the Ring (2001)

**Quality 💿**: 720p WEB

**Audio 🔊**: #Hindi #English

**Rating ⭐**: 8.9/10

**Genre 🎑**: #Action, #Adventure, #Drama

**Cast 🤹**: Elijah Wood, Ian McKellen, Orlando Bloom, Sean Bean, ...

**Story Line 📖**: A meek Hobbit from the Shire and eight companions set out on a journey to destroy the powerful One Ring and save Middle-earth from the Dark Lord Sauron.

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
Feel free to customize this `README.md` file further based on your specific needs and details.
