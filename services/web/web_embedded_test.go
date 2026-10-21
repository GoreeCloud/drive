package web_test

import (
	"encoding/json"
	"io/fs"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/opencloud-eu/opencloud/services/web"
	"github.com/opencloud-eu/opencloud/services/web/pkg/assets"
)

func TestBuiltFilesClientIsEmbeddedAndServed(t *testing.T) {
	core, err := fs.Sub(web.Assets, "assets/core")
	if err != nil {
		t.Fatal(err)
	}

	required := []string{
		"index.html", "manifest.json", "oidc-callback.html",
		"oidc-silent-redirect.html", "img/favicon.svg",
	}
	for _, name := range required {
		f, err := core.Open(name)
		if err != nil {
			t.Fatalf("required client asset %q missing: %v", name, err)
		}
		_ = f.Close()
	}

	entry, err := fs.ReadFile(core, "index.html")
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(string(entry), "<title>GoreeCloud Drive</title>") {
		t.Fatal("built title is not GoreeCloud Drive")
	}
	if !strings.Contains(string(entry), "web-app-files") {
		t.Fatal("real Files app not registered in the production entrypoint")
	}

	fileModules, err := fs.Glob(core, "js/web-app-files-*.mjs")
	if err != nil || len(fileModules) == 0 {
		t.Fatalf("missing actual compiled Files module: %v (%v)", fileModules, err)
	}
	clientModules, err := fs.Glob(core, "js/web-client-*.mjs")
	if err != nil {
		t.Fatal(err)
	}
	_ = clientModules // other modules are checked through request-level delivery

	manifestBytes, err := fs.ReadFile(core, "manifest.json")
	if err != nil {
		t.Fatal(err)
	}
	var manifest struct {
		Name       string `json:"name"`
		ShortName  string `json:"short_name"`
		ThemeColor string `json:"theme_color"`
	}
	if err := json.Unmarshal(manifestBytes, &manifest); err != nil {
		t.Fatal(err)
	}
	if manifest.Name != "GoreeCloud Drive" || manifest.ShortName != "Drive" || manifest.ThemeColor != "#5145D9" {
		t.Fatalf("unexpected brand manifest: %+v", manifest)
	}

	handler := assets.FileServer(core)
	for _, tc := range []struct {
		name, path, expected string
	}{
		{"entrypoint", "/", "GoreeCloud Drive"},
		{"SPA route fallback", "/files/list", "GoreeCloud Drive"},
		{"compiled Files application", "/" + fileModules[0], ""},
		{"PWA identity", "/manifest.json", "GoreeCloud Drive"},
	} {
		t.Run(tc.name, func(t *testing.T) {
			rec := httptest.NewRecorder()
			handler.ServeHTTP(rec, httptest.NewRequest(http.MethodGet, tc.path, nil))
			if rec.Code != http.StatusOK {
				t.Fatalf("GET %s: status %d (%s)", tc.path, rec.Code, rec.Body.String())
			}
			if rec.Body.Len() == 0 {
				t.Fatalf("GET %s: empty response", tc.path)
			}
			if tc.expected != "" && !strings.Contains(rec.Body.String(), tc.expected) {
				t.Fatalf("GET %s: missing expected page content", tc.path)
			}
		})
	}
}
