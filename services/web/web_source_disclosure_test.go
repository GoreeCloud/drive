package web_test

import (
	"bytes"
	"io/fs"
	"strings"
	"testing"

	"github.com/opencloud-eu/opencloud/services/web"
)

// Prevent accidentally shipping a browser bundle without the public
// corresponding-source link when the AGPL-covered frontend is rebuilt.
func TestEmbeddedClientIncludesAGPLSourceLink(t *testing.T) {
	const sourceURL = "https://github.com/GoreeCloud/drive/tree/main/web-client"
	root, err := fs.Sub(web.Assets, "assets/core")
	if err != nil {
		t.Fatal(err)
	}

	found := false
	err = fs.WalkDir(root, "js", func(path string, entry fs.DirEntry, walkErr error) error {
		if walkErr != nil {
			return walkErr
		}
		if entry.IsDir() || !strings.HasSuffix(path, ".mjs") {
			return nil
		}
		data, err := fs.ReadFile(root, path)
		if err != nil {
			return err
		}
		if bytes.Contains(data, []byte(sourceURL)) {
			found = true
			return fs.SkipAll
		}
		return nil
	})
	if err != nil {
		t.Fatal(err)
	}
	if !found {
		t.Fatalf("embedded AGPL browser client missing source URL %q", sourceURL)
	}
}
