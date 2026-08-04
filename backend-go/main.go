package main

import (
	"bytes"
	"io"
	"mime/multipart"
	"net/http"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

const pythonBase = "http://127.0.0.1:5000"

// proxyFile forwards a multipart file upload to a Python endpoint.
func proxyFile(c *gin.Context, path string) {

	file, err := c.FormFile("file")

	if err != nil {
		c.JSON(
			400,
			gin.H{"error": "file required"},
		)
		return
	}

	src, _ := file.Open()
	defer src.Close()

	body   := &bytes.Buffer{}
	writer := multipart.NewWriter(body)

	part, _ := writer.CreateFormFile("file", file.Filename)
	io.Copy(part, src)
	writer.Close()

	req, _ := http.NewRequest(
		"POST",
		pythonBase+path,
		body,
	)

	req.Header.Set(
		"Content-Type",
		writer.FormDataContentType(),
	)

	client      := &http.Client{}
	resp, err   := client.Do(req)

	if err != nil {
		c.JSON(
			500,
			gin.H{"error": "python service unavailable"},
		)
		return
	}

	defer resp.Body.Close()

	data, _ := io.ReadAll(resp.Body)

	c.Data(200, "application/json", data)
}

// proxyJSON forwards a JSON body to a Python endpoint.
func proxyJSON(c *gin.Context, method, path string) {

	body, _ := io.ReadAll(c.Request.Body)

	req, _ := http.NewRequest(
		method,
		pythonBase+path,
		bytes.NewReader(body),
	)

	req.Header.Set("Content-Type", "application/json")

	client    := &http.Client{}
	resp, err := client.Do(req)

	if err != nil {
		c.JSON(
			500,
			gin.H{"error": "python service unavailable"},
		)
		return
	}

	defer resp.Body.Close()

	data, _ := io.ReadAll(resp.Body)

	c.Data(200, "application/json", data)
}

func Predict(c *gin.Context) {
	proxyFile(c, "/predict")
}

func Feedback(c *gin.Context) {
	proxyFile(c, "/feedback")
}

func GetConfig(c *gin.Context) {
	proxyJSON(c, "GET", "/config")
}

func UpdateConfig(c *gin.Context) {
	proxyJSON(c, "POST", "/config")
}

func main() {

	r := gin.Default()

	r.Use(cors.Default())

	r.POST("/predict",      Predict)
	r.POST("/feedback",     Feedback)
	r.GET("/config",        GetConfig)
	r.POST("/config",       UpdateConfig)

	r.Run(":8080")
}
