// Command harnesscheck validates Go source formatting without modifying files.
package main

import (
	"bytes"
	"flag"
	"fmt"
	"go/format"
	"io/fs"
	"os"
	"path/filepath"
	"strings"
)

func checkFormatting(root string) error {
	var unformatted []string
	err := filepath.WalkDir(root, func(path string, entry fs.DirEntry, walkErr error) error {
		if walkErr != nil {
			return walkErr
		}
		if entry.IsDir() {
			if path != root && (strings.HasPrefix(entry.Name(), ".") || entry.Name() == "vendor" || entry.Name() == "node_modules") {
				return filepath.SkipDir
			}
			return nil
		}
		if !strings.HasSuffix(path, ".go") {
			return nil
		}
		data, err := os.ReadFile(path)
		if err != nil {
			return fmt.Errorf("read %s: %w", path, err)
		}
		formatted, err := format.Source(data)
		if err != nil {
			return fmt.Errorf("parse %s: %w", path, err)
		}
		if !bytes.Equal(data, formatted) {
			unformatted = append(unformatted, path)
		}
		return nil
	})
	if err != nil {
		return err
	}
	if len(unformatted) > 0 {
		return fmt.Errorf("run gofmt on: %s", strings.Join(unformatted, ", "))
	}
	return nil
}

func main() {
	formatting := flag.Bool("format", false, "check Go formatting without writing")
	flag.Parse()
	if !*formatting {
		fmt.Fprintln(os.Stderr, "usage: harnesscheck -format")
		os.Exit(2)
	}
	if err := checkFormatting("."); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
