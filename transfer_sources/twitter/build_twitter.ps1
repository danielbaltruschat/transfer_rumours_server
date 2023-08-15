$Env:GOOS = "linux"
go build -o get_tweets.bin get_tweets.go
$Env:GOOS = "windows"