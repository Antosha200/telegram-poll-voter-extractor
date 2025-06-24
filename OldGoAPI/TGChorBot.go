package main

import (
	"fmt"
	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"
	"log"
	"strconv"
)

// Глобальная переменная для хранения последнего опроса
var lastPoll *tgbotapi.Poll

func printPoll(poll *tgbotapi.Poll) {
	fmt.Printf("\n📊 Последний опрос: %s\n", poll.Question)
	for _, option := range poll.Options {
		fmt.Printf("- %s: %d голосов\n", option.Text, option.VoterCount)
	}
	fmt.Println("---")
}

func main() {
	bot, err := tgbotapi.NewBotAPI("8154988101:AAEpDS6ZnfcNGhc6lg3FYzVZAW83N13gaHU")
	if err != nil {
		log.Panic(err)
	}

	bot.Debug = true
	log.Printf("🟢 Бот авторизован: %s", bot.Self.UserName)

	u := tgbotapi.NewUpdate(0)
	u.Timeout = 10
	updates := bot.GetUpdatesChan(u)

	for update := range updates {
		if update.Message != nil {
			fmt.Printf("Последнее сообщение от %s: %s\n", update.Message.From.UserName, update.Message.Text)
		}

		chatID := update.Message.Chat.ID
		fmt.Printf(strconv.FormatInt(chatID, 10))

		//Отправляем сообщение от бота
		//msg := tgbotapi.NewMessage(chatID, "Привет! Я бот и получил твоё сообщение.")
		//_, _ = bot.Send(msg)

		for update := range updates {

			// 1) Новое сообщение (просто вывод)
			if update.Message != nil {
				fmt.Printf("📨 Сообщение от %s: %s\n",
					update.Message.From.UserName,
					update.Message.Text,
				)
			}

			// 2) Новый опрос
			if update.Message != nil && update.Message.Poll != nil {
				lastPoll = update.Message.Poll
				fmt.Printf("\n📥 Новый опрос: %s\n", lastPoll.Question)
				for _, opt := range lastPoll.Options {
					fmt.Printf("- %s (0 голосов пока)\n", opt.Text)
				}
				fmt.Println("---")
			}

			// 3) Пользователь проголосовал в неанонимном опросе, отправленном ботом
			if update.PollAnswer != nil {
				pa := update.PollAnswer
				user := pa.User
				// Формируем отображение имени
				fullName := user.FirstName
				if user.LastName != "" {
					fullName += " " + user.LastName
				}
				// Печатаем, кто и за какие варианты проголосовал
				fmt.Printf("✅ Голос от %s", fullName)
				if user.UserName != "" {
					fmt.Printf(" (@%s)", user.UserName)
				}
				fmt.Printf(": выбраны варианты %v\n", pa.OptionIDs)

				// По желанию сразу обновляем и выводим итоги
				if lastPoll != nil {
					printPoll(lastPoll)
				}
			}

			// 4) Обновление результатов опроса (update.Poll)
			if update.Poll != nil {
				lastPoll = update.Poll
				fmt.Println("🔄 Итоги опроса обновились:")
				printPoll(lastPoll)
			}
		}
	}

}
