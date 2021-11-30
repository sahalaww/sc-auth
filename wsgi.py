from dotenv import load_dotenv
load_dotenv('.env')

from main import app

if __name__ == '__main__':
    app.run()
