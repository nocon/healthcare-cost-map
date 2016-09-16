package main

import (
  "fmt"
  "net/http"
  "bytes"
  "io/ioutil"
  "strings"
)

func main() {
  var urls = []string{
  "http://www.rubyconf.com/",
  "https://espanol.yahoo.com/",
  "http://www.onet.pl/",
  }
  fmt.Printf(strings.Join(urls))
  for _, url := range urls {
      go func(url string) {
          fmt.Printf("Fetching %s \n", url)
          resp, err := http.Post("http://textalytics.com/core/lang-1.1",
            "application/x-www-form-urlencoded",
          	bytes.NewBufferString(
          		"key=bbbfc287834611e955c3c131c2e55345&of=json&txt=&url=" + url))
          if err != nil {
		        fmt.Printf("Failed to fetch %s \n", url)
		        return
		  } 
		  bodyBytes, err2 := ioutil.ReadAll(resp.Body)
		  if err2 != nil {
		  	    fmt.Printf("Failed to decode %s \n", url)
		        return
		  }
          fmt.Printf(string(bodyBytes))
      }(url)
  }
}