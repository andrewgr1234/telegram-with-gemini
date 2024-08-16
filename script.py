from telegram.ext import Application, MessageHandler, filters
import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

telegram_token = "7183552004:AAHMZy_ylgJVOk-FGuev2cD4hLsJGfVCuKo"
API_KEY = "AIzaSyB90Dua5Ll7J5JfonMeMNnZpJk0fDx_R9g"

def generate_response(user_input):
    try:
        response = model.generate_content(user_input)
        if response and response.candidates:
            candidate = response.candidates[0]
            generated_text = ""

            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                for part in candidate.content.parts:
                    if hasattr(part, 'text'):
                        generated_text += part.text

            return generated_text if generated_text else "Sorry, I couldn't generate a valid response."
        else:
            return "Sorry, I couldn't generate a response."

    except Exception as e:
        print(f"Error generating response: {e}")
        return "An error occurred while generating a response."


async def handle_messages(update, context):
    try:
        user_input = update.message.text

        if 'http' in user_input or 'https' in user_input:
            result = analyze_site(user_input)
            prompt = "summarize this paragraph from the website: ", result
            response = generate_response(prompt)
            await update.message.reply_text(response)

        else:
            response = generate_response(user_input)
            if response:
                await update.message.reply_text(response)
            else:
                await update.message.reply_text("Sorry, I couldn't generate a response.")

    except Exception as e:
        await update.message.reply_text("An error occurred while processing your request.")
        print(f"Error: {e}")


def analyze_site(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome()
    driver.get(url)

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'p')))
    paragraphs = driver.find_elements(By.TAG_NAME, 'p')
    all_paragraphs = "\n".join([p.text for p in paragraphs])
    driver.quit()
    return all_paragraphs  
    

if __name__ == "__main__":
    try:
        app = Application.builder().token(telegram_token).build()
        print("Token connected!")
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("Gemini connected!")

    except Exception as e:
        print(f"Error: {e}")

    app.add_handler(MessageHandler(filters.TEXT, handle_messages))
    app.run_polling(poll_interval=3)
