import os
import json
import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from huggingface_hub import InferenceClient

# tg authentication
TG_API_ID = os.environ.get("TG_API_ID")

# hf authentication
model_name = "Qwen/Qwen3-1.7B"
client = InferenceClient(model_name, token=os.environ.get("HF_TOKEN"))

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Вставьте сюда описание процесса, и я перескажу его! ')

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text

    def summarize_process(text: str):
      """
      summarizes provided description of the proccess in Russian

      text: provided source
      """
      summarization_prompt = f"""
      Summarize the provided text in Russian. Use Russian language only.
      Extract the main process and briefly summarize it.
      Include key steps, participants and final result in summary.
      Add those who are responsible for the whole process.
      Return the summarized text in Russian only without any comments and explanations.

      Text for summarization:\n\n
      """

      summary = client.chat.completions.create(
        messages=[{"role": "user",
                 "content": text}],
        response_format={
          "type": "json",
          "value":
          {
            "properties":
            {
              "summary":
              {
                "type": "string"
              }
            }
          }
        },
        stream=False,
        max_tokens=1024,
        temperature=0.5,
        top_p=0.1
      ).choices[0].get("message")["content"]

        return json.loads(summary)["summary"]

    response = summarize_text(message_text)

    await update.message.reply_text(f'**Саммари**:\n\n{response}')

async def error_log(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.warning(f'Обновление {update} вызвало ошибку {context.error}')

def main() -> None:
    application = ApplicationBuilder().token(TG_API_ID).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_document))

    application.add_error_handler(error_log)

    application.run_polling()

if __name__ == "__main__":
    main()
