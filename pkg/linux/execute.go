// +build linux

package linux

import (
	"bytes"
	"fmt"
	"os/exec"
	"strings"

	"github.com/n00py/Slackor/pkg/command"
)

var cmdName = "sh"

// Execute runs an arbitrary command
type Execute struct{}

// Name is the name of the command
func (e Execute) Name() string {
	return "execute"
}

// Run runs an arbitrary command
func (e Execute) Run(clientID string, jobID string, args []string) (string, error) {
	cmdArgs := []string{"-c"}
	cmdArgs = append(cmdArgs, strings.Join(args, " "))
	cmd := exec.Command(cmdName, cmdArgs...)
	fmt.Println("Running command: " + strings.Join(args, " "))
	var out bytes.Buffer
	var stderr bytes.Buffer
	cmd.Stdout = &out
	cmd.Stderr = &stderr
	err := cmd.Run()
	if err != nil {
		return stderr.String(), err
	}
	return out.String(), nil
}

func init() {
	command.RegisterCommand(Execute{})
}
