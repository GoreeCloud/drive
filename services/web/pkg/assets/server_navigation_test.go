package assets

import (
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"testing/fstest"
)

func TestFileServerOnlyFallsBackForDocumentNavigation(t *testing.T) {
	fsys := fstest.MapFS{
		"index.html":        &fstest.MapFile{Data: []byte("<html><head></head><body>Drive app shell</body></html>")},
		"js/real-chunk.mjs": &fstest.MapFile{Data: []byte("export const available = true;")},
	}
	handler := FileServer(fsys)
	cases := []struct {
		name, method, path, accept string
		wantStatus                 int
		wantHTML                   bool
	}{
		{"browser navigation", http.MethodGet, "/files/list", "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8", http.StatusOK, true},
		{"legacy navigation without accept", http.MethodGet, "/files/list", "", http.StatusOK, true},
		{"document route containing file suffix", http.MethodGet, "/files/spaces/document.pdf", "text/html", http.StatusOK, true},
		{"HEAD document navigation", http.MethodHead, "/files/list", "text/html", http.StatusOK, true},
		{"existing script", http.MethodGet, "/js/real-chunk.mjs", "*/*", http.StatusOK, false},
		{"missing script", http.MethodGet, "/js/missing-chunk.mjs", "*/*", http.StatusNotFound, false},
		{"missing script explicit HTML navigation", http.MethodGet, "/js/missing-chunk.mjs", "text/html", http.StatusNotFound, false},
		{"missing stylesheet", http.MethodGet, "/css/theme.css", "text/css,*/*;q=0.1", http.StatusNotFound, false},
		{"missing image", http.MethodGet, "/img/logo.svg", "image/avif,image/webp,*/*", http.StatusNotFound, false},
		{"missing configuration", http.MethodGet, "/config.json", "*/*", http.StatusNotFound, false},
		{"missing configuration opened as page", http.MethodGet, "/config.json", "text/html", http.StatusNotFound, false},
		{"missing manifest opened as page", http.MethodGet, "/manifest.json", "text/html", http.StatusNotFound, false},
		{"missing favicon", http.MethodGet, "/favicon.ico", "image/*", http.StatusNotFound, false},
		{"missing service worker", http.MethodGet, "/service-worker.js", "*/*", http.StatusNotFound, false},
		{"missing API-like resource", http.MethodGet, "/api/missing", "text/html", http.StatusNotFound, false},
		{"missing route requested as JSON", http.MethodGet, "/files/list", "application/json", http.StatusNotFound, false},
		{"missing route requesting unacceptable HTML", http.MethodGet, "/files/list", "text/html;q=0", http.StatusNotFound, false},
		{"missing route requesting zero-weight HTML", http.MethodGet, "/files/list", "text/html;q=0.00", http.StatusNotFound, false},
		{"missing route with invalid accept weight", http.MethodGet, "/files/list", "text/html;q=banana", http.StatusNotFound, false},
		{"valid weighted browser navigation", http.MethodGet, "/files/list", "text/html;q=0.5,*/*;q=0.1", http.StatusOK, true},
		{"missing file suffix without Accept", http.MethodGet, "/js/missing.mjs", "", http.StatusNotFound, false},
		{"POST must not render app", http.MethodPost, "/files/list", "text/html", http.StatusMethodNotAllowed, false},
		{"DELETE must not return script", http.MethodDelete, "/js/real-chunk.mjs", "*/*", http.StatusMethodNotAllowed, false},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			rec := httptest.NewRecorder()
			req := httptest.NewRequest(tc.method, tc.path, nil)
			if tc.accept != "" {
				req.Header.Set("Accept", tc.accept)
			}
			handler.ServeHTTP(rec, req)
			if rec.Code != tc.wantStatus {
				t.Fatalf("%s %s Accept=%q: status %d, want %d (%q)", tc.method, tc.path, tc.accept, rec.Code, tc.wantStatus, rec.Body.String())
			}
			if tc.wantHTML {
				if rec.Header().Get("Cache-Control") != "no-cache" {
					t.Fatalf("navigation should return no-cache, got %q", rec.Header().Get("Cache-Control"))
				}
				if tc.method == http.MethodGet && !strings.Contains(rec.Body.String(), "Drive app shell") {
					t.Fatalf("navigation did not receive app shell: %q", rec.Body.String())
				}
				if tc.method == http.MethodHead && rec.Body.Len() != 0 {
					t.Fatalf("HEAD should have no body, got %d bytes", rec.Body.Len())
				}
			} else if strings.Contains(rec.Body.String(), "Drive app shell") {
				t.Fatalf("non-navigation leaked index.html instead of asset error")
			}
			if tc.wantStatus == http.StatusMethodNotAllowed && rec.Header().Get("Allow") != "GET, HEAD" {
				t.Fatalf("method restriction missing Allow: %q", rec.Header().Get("Allow"))
			}
		})
	}
}
