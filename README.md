# Filter.py

`Filter.py` is a Python script designed to filter songs from a Spotify playlist based on the language of their lyrics, using the Spotify and Genius APIs. This script is particularly useful for users who wish to create a version of a playlist that excludes songs in a specific language.

## Getting Started

### Prerequisites

Before you can use `Filter.py`, you need to have Python and pip installed on your system. If you do not have these installed, follow these steps:

#### Install Python
1. Visit the official [Python website](https://www.python.org/downloads/).
2. Download the latest version of Python for your operating system.
3. Run the installer. Ensure that you check the box that says "Add Python to PATH" before clicking "Install Now."

#### Install pip
Pip is included by default with Python 3.4 and later. If you need to upgrade or install pip, you can do so by running:
```bash
python -m ensurepip --upgrade
```

### Setting Up Developer Accounts

#### Spotify Developer Account
1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
2. Log in with your Spotify account or create a new one if necessary.
3. Click "Create an App". Provide an app name and description, then agree to the terms.
4. Note the `Client ID` and `Client Secret`.

#### Genius API Account
1. Visit the [Genius API clients page](https://genius.com/api-clients).
2. Sign in with your Genius account or create one.
3. Create a new API client. Note the `Client Access Token`.

### Configuring the Script

#### Obtain and Set Credentials
You need to edit `Filter.py` to include your Spotify and Genius credentials, along with a redirect URI used for the Spotify authentication process:

1. Open `Filter.py` with a text editor.
2. Locate the section where `client_id`, `client_secret`, `genius_token`, and `redirect_uri` are defined.
3. Replace the placeholder values with your actual Spotify and Genius credentials.
4. Ensure the `redirect_uri` matches the one configured in your Spotify app, such as `http://localhost:8888/callback`.

#### Set the Desired Language to Filter
Locate the line that checks the language:
```python
if language != 'INSERT-DESIRED-LANGUAGE-CODE':
```
Change `'INSERT-DESIRED-LANGUAGE-CODE'` to the desired language code (ISO 639-1 Code), such as `'en'` for English or `'es'` for Spanish.

### Running the Script

After configuring the script, you can double click or run it from the command line:
```bash
python Filter.py
```

The script will authenticate with Spotify and Genius, fetch the playlist items, check the lyrics' language, and create a new playlist excluding songs in the specified language.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
