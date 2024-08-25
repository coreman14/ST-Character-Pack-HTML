package main

import (
	"crypto/md5"
	"encoding/hex"
	"fmt"
	"html/template"
	"io"
	"log"
	"math"
	"os"
	"path/filepath"
	"slices"
	"strings"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

var (
	DIR_OF_HOLDING = "tmp"
	DIR_OF_LOGGING = "serverConfig/logs"
)

type Templates struct {
	templates *template.Template
}

func (t *Templates) Render(w io.Writer, name string, data interface{}, c echo.Context) error {
	return t.templates.ExecuteTemplate(w, name, data)
}

func newTemplate() *Templates {
	return &Templates{
		templates: template.Must(template.ParseGlob("views/*.html")),
	}
}

/*
filehash, isCharacterParsed(Have all character been looped through), progress (String of current/total) object
errorText Object
filename, linkToFile object
*/
type FileHash struct {
	FileHash          string
	IsCharacterParsed bool
	Progress          string
}

func newFileHash(fileHash string, isCharacterParsed bool, progress string) FileHash {
	return FileHash{
		FileHash:          fileHash,
		IsCharacterParsed: isCharacterParsed,
		Progress:          progress,
	}
}
func newBasicFileHash(fileHash string) FileHash {
	return FileHash{
		FileHash:          fileHash,
		IsCharacterParsed: false,
		Progress:          "",
	}
}

type ErrorText struct {
	ErrorText string
}

func newErrorText(errorText string) *ErrorText {
	return &ErrorText{
		ErrorText: errorText,
	}
}

type Filename struct {
	Filename   string
	LinkToFile string
}

func newFilename(filename string, linkToFile string) *Filename {
	return &Filename{
		Filename:   filename,
		LinkToFile: linkToFile,
	}
}

func decideDivReturn(c echo.Context, fileHash string) error {
	files, err := os.ReadDir(DIR_OF_HOLDING)
	if err != nil {
		fmt.Println("First error")
		log.Fatal(err)
	}
	var unZippedFolderPath string
	for _, file := range files {
		if strings.HasPrefix(file.Name(), fileHash) && file.IsDir() {
			unZippedFolderPath = filepath.Join(DIR_OF_HOLDING, file.Name())
			break
		}
	}

	files = slices.DeleteFunc(files, func(file os.DirEntry) bool {
		//Get only relevant files
		return file.IsDir() || !strings.HasPrefix(file.Name(), fileHash)
	})
	files = slices.DeleteFunc(files, func(file os.DirEntry) bool {
		//Remove original zip file
		return strings.HasSuffix(file.Name(), ".zip")
	})

	if len(files) > 0 {
		completedFilesSlice := slices.Clone(files)
		errorFile := slices.DeleteFunc(files, func(file os.DirEntry) bool {
			//Remove original zip file
			return !strings.HasSuffix(file.Name(), ".error")
		})
		if len(errorFile) == 1 {
			data, err := os.ReadFile(DIR_OF_HOLDING + "/" + errorFile[0].Name())
			if err != nil {
				fmt.Println("4th error")
				log.Fatal(err)
			}
			data_string := string(data)
			folderName := strings.ReplaceAll(errorFile[0].Name(), ".error", "")
			fullPath, err := filepath.Abs(DIR_OF_HOLDING)
			if err != nil {
				fmt.Println("5th error")
				log.Fatal(err)
			}
			sep := string(os.PathSeparator)
			fullPath = strings.ToUpper(string(fullPath[0])) + fullPath[1:]
			data_string = strings.ReplaceAll(data_string, fullPath, "")
			data_string = strings.ReplaceAll(data_string, folderName+sep, folderName+".zip"+sep)
			data_string = strings.ReplaceAll(data_string, sep+fileHash+".", "")
			return c.Render(200, "error", newErrorText(data_string))
		}
		completedFile := slices.DeleteFunc(completedFilesSlice, func(file os.DirEntry) bool {
			//Remove original zip file
			return !strings.HasSuffix(file.Name(), ".zip-completed")
		})
		if len(completedFile) == 1 {
			linkToFile := strings.ReplaceAll(completedFile[0].Name(), ".zip-completed", "")
			return c.Render(200, "finishedhtml", newFilename(strings.Split(linkToFile, ".")[1]+".zip", "/downloadCompletedZip/"+linkToFile))
		}
	} else if unZippedFolderPath != "" {
		err = filepath.WalkDir(unZippedFolderPath, func(path string, info os.DirEntry, err error) error {
			if err != nil {
				return err
			}
			if !info.IsDir() && info.Name() == "scenario.yml" {
				unZippedFolderPath = filepath.Dir(path)
				return os.ErrExist
			}
			return nil
		})
		if err != os.ErrExist {
			return c.Render(200, "waitingforthread", newBasicFileHash(fileHash))
		}
		err = nil
		files, err := os.ReadDir(unZippedFolderPath)
		if err != nil {
			fmt.Println("third error")
			log.Fatal(err)
		}
		files = slices.DeleteFunc(files, func(file os.DirEntry) bool {
			//Remove original zip file
			return !strings.HasPrefix(file.Name(), "progress.")
		})
		if len(files) == 1 {
			file := strings.Split(files[0].Name(), ".")
			total := file[len(file)-1]
			current := file[len(file)-2]
			return c.Render(200, "progress", newFileHash(fileHash, total == current, current+"/"+total))
		}
	}
	return c.Render(200, "waitingforthread", newBasicFileHash(fileHash))
}
func sizeof_fmt(num float64, suffix string) string {
	if suffix == "" {
		suffix = "b"
	}
	for _, unit := range []string{"", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"} {
		if math.Abs(num) < 1024.0 {
			return fmt.Sprintf("%3.1f%s%s", num, unit, suffix)
		}
		num /= 1024.0
	}
	return fmt.Sprintf("%.1fYi%s", num, suffix)
}
func upload(c echo.Context) error {
	// Read form fields

	//-----------
	// Read file
	//-----------

	// Source
	file, err := c.FormFile("file")
	if err != nil {
		return err
	}

	fmt.Printf("File was uploaded, %s, with size of: %s\n", file.Filename, sizeof_fmt(float64(file.Size), ""))
	src, err := file.Open()
	if err != nil {
		return err
	}
	defer src.Close()
	md5 := md5.New()
	if _, err := io.Copy(md5, src); err != nil {
		log.Fatal(err)
	}
	src.Seek(0, io.SeekStart)
	file_hash := hex.EncodeToString(md5.Sum(nil))
	filename := DIR_OF_HOLDING + "/" + file_hash + "." + file.Filename

	files, err := os.ReadDir(DIR_OF_HOLDING)
	if err != nil {
		fmt.Println("First error")
		log.Fatal(err)
	}
	files = slices.DeleteFunc(files, func(file os.DirEntry) bool {
		//Remove original zip file
		return !strings.HasPrefix(file.Name(), file_hash)
	})
	// Destination
	if len(files) == 0 {
		dst, err := os.Create(filename)
		if err != nil {
			return err
		}
		defer dst.Close()

		// Copy
		if _, err = io.Copy(dst, src); err != nil {
			return err
		}
		fmt.Printf("File %s was saved at \"%s\"\n", file.Filename, filename)
	} else {
		fmt.Printf("File %s is a duplicate, returning correct Div\n", filename)
	}

	return decideDivReturn(c, file_hash)
}
func renderBase(c echo.Context) echo.Context {
	c.Render(200, "headers", nil)
	c.Render(200, "htmlstart", nil)
	return c
}
func renderBaseEnd(c echo.Context) error {
	return c.Render(200, "htmlend", nil)
}

func main() {
	e := echo.New()
	e.Use(middleware.Logger())

	e.Renderer = newTemplate()

	e.GET("/", func(c echo.Context) error {
		c = renderBase(c)
		c.Render(200, "index", nil)
		return renderBaseEnd(c)
	})
	e.GET("/info", func(c echo.Context) error {
		c = renderBase(c)
		c.Render(200, "informationBlock", nil)
		return renderBaseEnd(c)
	})
	e.GET("/progress/:fileHash", func(c echo.Context) error {
		return decideDivReturn(c, c.Param("fileHash"))
	})
	e.GET("/downloadCompletedZip/:fName", func(c echo.Context) error {
		return c.Attachment(DIR_OF_HOLDING+"/"+c.Param("fName")+".zip-completed", strings.Split(c.Param("fName"), ".")[1]+".zip")
	})
	e.POST("/uploadFile", func(c echo.Context) error {
		return upload(c)
	})
	e.Logger.Fatal(e.Start(":80"))
	/*Last things to do. 1. Make the post and download routes 2. Make the file response routes (favicon.ico and stuff) 3. Move go into main folder 4. Make python server only do the files processing. 5. Do go logging. */

}
