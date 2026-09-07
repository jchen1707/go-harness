package main

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestFormatting(t *testing.T) {
	for _, tc := range []struct {
		name, source string
		wantError    bool
	}{
		{"formatted", "package sample\n\nfunc Run() {}\n", false},
		{"unformatted", "package sample;func Run(){}", true},
		{"invalid", "package ???", true},
	} {
		t.Run(tc.name, func(t *testing.T) {
			dir := t.TempDir()
			path := filepath.Join(dir, "sample.go")
			if err := os.WriteFile(path, []byte(tc.source), 0600); err != nil {
				t.Fatal(err)
			}
			err := checkFormatting(dir)
			if (err != nil) != tc.wantError {
				t.Fatalf("error = %v, want error %v", err, tc.wantError)
			}
			if err != nil && !strings.Contains(err.Error(), "sample.go") {
				t.Fatalf("diagnostic omits file: %v", err)
			}
			after, err := os.ReadFile(path)
			if err != nil {
				t.Fatal(err)
			}
			if string(after) != tc.source {
				t.Fatal("check modified source")
			}
		})
	}
}

func TestSkipsDependenciesAndFindsNestedSource(t *testing.T) {
	dir := t.TempDir()
	for _, name := range []string{"vendor", "node_modules", ".git"} {
		sub := filepath.Join(dir, name)
		if err := os.Mkdir(sub, 0700); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(filepath.Join(sub, "bad.go"), []byte("package ???"), 0600); err != nil {
			t.Fatal(err)
		}
	}
	if err := checkFormatting(dir); err != nil {
		t.Fatal(err)
	}
	sub := filepath.Join(dir, "internal")
	if err := os.Mkdir(sub, 0700); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(sub, "bad.go"), []byte("package ???"), 0600); err != nil {
		t.Fatal(err)
	}
	if err := checkFormatting(dir); err == nil {
		t.Fatal("nested source was unchecked")
	}
}

func TestMissingDirectoryFails(t *testing.T) {
	if err := checkFormatting(filepath.Join(t.TempDir(), "missing")); err == nil {
		t.Fatal("missing root passed")
	}
}
