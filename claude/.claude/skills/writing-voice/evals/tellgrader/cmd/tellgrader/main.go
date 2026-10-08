package main

import (
	"errors"
	"fmt"
	"os"
)

func main() {
	cmd := newRootCmd()
	if err := cmd.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		if _, ok := errors.AsType[gateError](err); ok {
			os.Exit(gateExitCode)
		}
		os.Exit(1)
	}
}
