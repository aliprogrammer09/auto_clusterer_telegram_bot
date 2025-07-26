import logging
import asyncio
import nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, MessageHandler
import pandas as pd
import os
import model




nest_asyncio.apply()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

token = "YOUR_BOT_TOKEN"
bot_username = "@testpoweryBot"





async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " Hello, Welcome to bot! This bot is used for auto clustering.\n\nYou should give it 2 datasets, df_main.csv (the main dataset) and df_X.csv (the X part of dataset).\n\nPay attention, the file name must be exact same.\n\nWhen you upload files with the exact name, it automatically detects them and set them.\n\nThere is another option called pca, it lowers the number of features, it usually makes the model perform better and the other advantage is you can see the plot visually. If you turn on pca, you get the image of plot beside the model score. You should choose it with command /pca true or false, like: /pca true .\n\nWhen you set parameters (datasets and pca) you can run the model to predict (cluster) the dataset and it gives you a model score. You can run the model with /autoClusterer , it will take some time. in pca mode or when your X dataset has just 2 features, it gives you an image of the plot too.\n\nYou cannot change the parameters straightly, you should first delete the parameters first. You can delete all parameters with command /delete , You can specify a special parameter too like: /delete df_main.csv .\n\n You can know what parameters you have set by using /getStatuse ."

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)




async def handle_files(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.document:
        file_id = update.message.document.file_id
        file_name = update.message.document.file_name

        if file_name == "df_main.csv":
          try:
            df_main = pd.read_csv("files/df_main.csv")
            await update.message.reply_text(f"df_X.csv is saved already. Please delete the parameter first.")
          except:
            new_file = await context.bot.get_file(file_id)
            await new_file.download_to_drive(custom_path="files/df_main.csv")
            await update.message.reply_text(f"File {file_name} is saved successfully.")


        elif file_name == "df_X.csv":
          try:
            df_X = pd.read_csv("files/df_X.csv")
            await update.message.reply_text(f"df_X.csv is saved already. Please delete the parameter first.")
          except:
            new_file = await context.bot.get_file(file_id)
            await new_file.download_to_drive(custom_path="files/df_X.csv")
            await update.message.reply_text(f"File {file_name} is saved successfully.")

        else:
          await update.message.reply_text(f"Please change name of your file to df_main.csv or df_X.csv")




async def PCA(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
      pca = open("files/pca.txt", "r").read()
      await update.message.reply_text(text=f"PCA is set already as {pca}. Please delete the parameter first.")

    except:
      pca_user = ' '.join(context.args).lower()
      if pca_user == "true":
        pca = True
        await update.message.reply_text(text=f"PCA is set successfully as {pca}.")
        open("files/pca.txt", "w").write("True")

      elif pca_user == "false":
        pca = False
        await update.message.reply_text(text=f"PCA is set successfully as {pca}.")
        open("files/pca.txt", "w").write("False")

      else:
        await update.message.reply_text(text="Please enter true or false.")






async def getStatuse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if os.path.exists('files/df_main.csv'):
      file1_st = "\u2714"
    else:
      file1_st = "\u274C"

    if os.path.exists('files/df_X.csv'):
      file2_st = "\u2714"
    else:
      file2_st = "\u274C"

    if os.path.exists('files/pca.txt'):
      pca_st = "\u2714"
      if open("files/pca.txt", "r").read().lower() == "true":
        pca = True
      else:
        pca = False
    else:
      pca = None
      pca_st = "\u274C"


    await update.message.reply_text(text=f"df_main.csv: {file1_st}\ndf_X.csv: {file2_st}\npca: {pca_st} - {pca}")





async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    delete_parameter = ' '.join(context.args).lower()

    if delete_parameter == "" or delete_parameter == " ":
      for f in os.listdir('files'):
          os.remove(f"files/{f}")
          await update.message.reply_text(text="All parameters are deleted successfully.")


    elif delete_parameter == "df_main.csv":
      if os.path.exists("files/df_main.csv"):
          os.remove("files/df_main.csv")
          await update.message.reply_text(text="df_main.csv is deleted successfully.")
      else:
          await update.message.reply_text(text="df_main.csv is already deleted.")


    elif delete_parameter == "df_X.csv":
      if os.path.exists("files/df_X.csv.csv"):
          os.remove("files/df_X.csv")
          await update.message.reply_text(text="df_X.csv is deleted successfully.")
      else:
          await update.message.reply_text(text="df_X.csv is already deleted.")


    elif delete_parameter.lower() == "pca":
      if os.path.exists("filespca.txt"):
          os.remove("files/pca.txt")
          await update.message.reply_text(text="PCA is deleted successfully.")
      else:
          await update.message.reply_text(text="PCA is already deleted.")


    else:
        await update.message.reply_text(text="Unknown parameter.")





async def answer_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    def answer(text):
        if text == "hello" or text == "hi":
            return context.bot.send_message(chat_id=update.effective_chat.id, text="Hi, there.")

        elif text == "bye":
            return context.bot.send_message(chat_id=update.effective_chat.id, text="Bye, see you later.")

        else:
          return context.bot.send_message(chat_id=update.effective_chat.id, text="I don't understand what are you saying...")


    chat_type = update.effective_chat.type
    text = update.message.text
    if chat_type == 'private':
        text = text.lower()
        await answer(text)


    else:
        if bot_username in text:
            text = text.replace(bot_username, "").strip()
            text = text.lower()
            await answer(text)





async def auto_clusterer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if os.path.exists('files/pca.txt') and os.path.exists('files/df_X.csv') and os.path.exists('files/df_main.csv'):
      pca = open("files/pca.txt", "r").read()
      if pca.lower() == "true":
        pca = True
      else:
        pca = False

      df_X = "files/df_X.csv"
      df_main = "files/df_main.csv"

      model_score = model.autoClusterer(df_main, df_X, pca)
      image = 'results/images/plot.jpg'


      with open(image, 'rb') as img:
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=img)
      await update.message.reply_text(text=f"The score of model is {round(model_score *100, 3)}%")






async def main():

    if os.path.exists("files") == False:
        os.mkdir("files")


    application = ApplicationBuilder().token(token).build()


    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('getStatuse', getStatuse))
    application.add_handler(CommandHandler('delete', delete))
    application.add_handler(CommandHandler('autoClusterer', auto_clusterer))
    application.add_handler(CommandHandler('pca', PCA))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.Regex(r'^/pca')), answer_chat))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_files))


    print("The bot is running...")
    await application.run_polling()




if __name__ == '__main__':
    asyncio.run(main())