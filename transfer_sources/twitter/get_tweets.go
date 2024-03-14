package main

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"

	_ "github.com/go-sql-driver/mysql"
	twitterscraper "github.com/n0madic/twitter-scraper"
)

func ReadFileLines(filename string) ([]string, error) {
	content, err := os.ReadFile(filename)
	if err != nil {
		return nil, err
	}
	lines := strings.Split(string(content), "\n")
	return lines, nil
}

func GetTweets(sources []string, timeAllowed int64, username string, password string) ([][]string, error) {
	scraper := twitterscraper.New()
	f, err := os.Open("cookies.json")

	if err == nil {
		// deserialize from JSON
		var cookies []*http.Cookie
		json.NewDecoder(f).Decode(&cookies)
		// load cookies
		scraper.SetCookies(cookies)
		// check login status
	}

	if !scraper.IsLoggedIn() {

		errLogin := scraper.Login(username, password)
		if errLogin != nil {
			return nil, errLogin
		}

		cookies := scraper.GetCookies()
		// serialize to JSON
		js, _ := json.Marshal(cookies)
		// save to file
		f, _ = os.Create("cookies.json")
		f.Write(js)
	}

	tweets := [][]string{}

	currentTimestamp := time.Now().Unix()

	for _, source := range sources {
		num := 3

		// Remove carriage returns, -1 for replacing all occurences (no limit) - essentially standardising the txt file
		cleanedSource := strings.Replace(source, "\r", "", -1)

		for tweet := range scraper.GetTweets(context.Background(), cleanedSource, num) {
			if tweet.Error != nil {
				fmt.Println("Error retrieving tweets for " + source + "    Error: ")
				fmt.Println(tweet.Error)
				continue
			}

			fmt.Println(source)

			if !tweet.IsRetweet {
				if (currentTimestamp - tweet.Timestamp) < int64(timeAllowed) {
					tweets = append(tweets, []string{tweet.ID, tweet.Text, tweet.Username, strconv.FormatInt(tweet.Timestamp, 10)}) // Append a single-element string slice, converts int64 to string
				}
			}
		}
	}
	return tweets, nil
}

// test function to test GetTweets function is working
func main_test() {
	sources := []string{"FabrizioRomano"}

	timeAllowed := 1800 // 30 minutes

	twitterUsername := ""
	twitterPassword := ""

	tweets, err := GetTweets(sources, int64(timeAllowed), twitterUsername, twitterPassword)

	if err != nil {
		panic(err)
	}

	for _, row := range tweets {
		fmt.Println(row)
	}
}

func main() {
	mydir, err := os.Getwd()
	if err != nil {
		fmt.Println(err)
	}
	fmt.Println(mydir)

	args := os.Args[1:]

	// Get twitter users from twitter_sources.txt
	sources, err := ReadFileLines("twitter_sources.txt")
	if err != nil {
		panic(err)
	}

	timeAllowed, err := strconv.Atoi(args[3]) // 30 minutes
	if err != nil {
		panic(err)
	}

	twitterUsername := os.Getenv("TWITTER_USERNAME")
	twitterPassword := os.Getenv("TWITTER_PASSWORD")

	tweets, err := GetTweets(sources, int64(timeAllowed), twitterUsername, twitterPassword)

	if err != nil {
		panic(err)
	}

	//Write tweets to MySQL database

	//Get command line arguments

	for _, row := range tweets {
		fmt.Println(row)
	}

	username := args[0]
	password := args[1]
	port := args[2]

	// Open database connection
	db, err := sql.Open("mysql", fmt.Sprintf("%s:%s@tcp(mysql:%s)/transfer_data", username, password, port))
	if err != nil {
		panic(err.Error())
	}
	defer db.Close()

	stmt, err := db.Prepare("INSERT INTO sources (source_link, text, author_name, timestamp, source_type) VALUES (?, ?, ?, ?, 'twitter')")
	if err != nil {
		panic(err.Error())
	}
	defer stmt.Close()

	for _, row := range tweets {
		_, err := stmt.Exec(row[0], row[1], row[2], row[3])
		if err != nil {
			panic(err.Error())
		}
	}

	fmt.Println("Tweets saved to MySQL database")

}
