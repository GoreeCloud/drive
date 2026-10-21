package web_test

import (
	"io/fs"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	web "github.com/opencloud-eu/opencloud/services/web"
	"github.com/opencloud-eu/opencloud/services/web/pkg/assets"
)

// Production-like embedded web assets must not silently replace a missing
// code chunk with HTML. That response hides deployment corruption and makes
// browsers report misleading module MIME and syntax errors.
func TestEmbeddedFilesClientRejectsMissingAssets(t *testing.T) {
	core, err := fs.Sub(web.Assets, "assets/core")
	if err != nil {
		t.Fatal(err)
	}
	handler := assets.FileServer(core)
	tests := []struct {
		path, accept string
		want         int
	}{
		{"/js/chunk-intentionally-missing-GoreeCloud.mjs", "*/*", http.StatusNotFound},
		{"/css/chunk-intentionally-missing-GoreeCloud.css", "text/css,*/*", http.StatusNotFound},
		{"/img/unknown-GoreeCloud-symbol.svg", "image/avif,image/webp,*/*", http.StatusNotFound},
		{"/config.json", "application/json", http.StatusNotFound},
		{"/files/list", "text/html,application/xhtml+xml", http.StatusOK},
	}
	for _, tt := range tests {
		t.Run(tt.path, func(t *testing.T) {
			rec := httptest.NewRecorder()
			request := httptest.NewRequest(http.MethodGet, tt.path, nil)
			request.Header.Set("Accept", tt.accept)
			handler.ServeHTTP(rec, request)
			if rec.Code != tt.want {
				t.Fatalf("%s returned %d; expected %d", tt.path, rec.Code, tt.want)
			}
			if rec.Code == http.StatusNotFound && strings.Contains(rec.Body.String(), "GoreeCloud Drive</title>") {
				t.Fatalf("missing file returned the app shell")
			}
		})
	}
}
