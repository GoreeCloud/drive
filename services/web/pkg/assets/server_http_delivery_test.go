package assets

import (
	"net/http"
	"net/http/httptest"
	"testing"
	"testing/fstest"
	"time"
)

func TestStaticAssetsSupportStandardHTTPDelivery(t *testing.T) {
	modified := time.Date(2026, time.October, 20, 12, 0, 0, 0, time.UTC)
	fileSystem := fstest.MapFS{
		"bundle.js": &fstest.MapFile{
			Data:    []byte("abcdefghijklmnop"),
			ModTime: modified,
		},
	}
	testCases := []struct {
		name           string
		method         string
		rangeHeader    string
		modifiedSince  string
		expectedStatus int
		expectedBody   string
		expectedRange  string
	}{
		{
			name: "full asset", method: http.MethodGet,
			expectedStatus: http.StatusOK, expectedBody: "abcdefghijklmnop",
		},
		{
			name: "head does not send content", method: http.MethodHead,
			expectedStatus: http.StatusOK, expectedBody: "",
		},
		{
			name: "partial content", method: http.MethodGet, rangeHeader: "bytes=3-6",
			expectedStatus: http.StatusPartialContent, expectedBody: "defg",
			expectedRange: "bytes 3-6/16",
		},
		{
			name: "suffix partial content", method: http.MethodGet, rangeHeader: "bytes=-4",
			expectedStatus: http.StatusPartialContent, expectedBody: "mnop",
			expectedRange: "bytes 12-15/16",
		},
		{
			name: "unsatisfiable range", method: http.MethodGet, rangeHeader: "bytes=100-",
			expectedStatus: http.StatusRequestedRangeNotSatisfiable,
			expectedRange:  "bytes */16",
		},
		{
			name: "not modified", method: http.MethodGet,
			modifiedSince:  modified.Format(http.TimeFormat),
			expectedStatus: http.StatusNotModified,
		},
	}
	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			rec := httptest.NewRecorder()
			req := httptest.NewRequest(tc.method, "/bundle.js", nil)
			if tc.rangeHeader != "" {
				req.Header.Set("Range", tc.rangeHeader)
			}
			if tc.modifiedSince != "" {
				req.Header.Set("If-Modified-Since", tc.modifiedSince)
			}
			FileServer(fileSystem).ServeHTTP(rec, req)
			if rec.Code != tc.expectedStatus {
				t.Fatalf("got status %d; want %d", rec.Code, tc.expectedStatus)
			}
			if tc.expectedStatus != http.StatusRequestedRangeNotSatisfiable && rec.Body.String() != tc.expectedBody {
				t.Fatalf("got body %q; want %q", rec.Body.String(), tc.expectedBody)
			}
			if tc.expectedRange != "" && rec.Header().Get("Content-Range") != tc.expectedRange {
				t.Fatalf("got Content-Range %q; want %q", rec.Header().Get("Content-Range"), tc.expectedRange)
			}
			if tc.method == http.MethodHead && rec.Header().Get("Content-Length") != "16" {
				t.Fatalf("got HEAD Content-Length %q; want 16", rec.Header().Get("Content-Length"))
			}
		})
	}
}

func TestHTMLBootstrapPreservesNoCacheAndHeadSemantics(t *testing.T) {
	fileSystem := fstest.MapFS{
		"index.html": &fstest.MapFile{Data: []byte("<html><head></head><body>Welcome</body></html>")},
	}
	for _, method := range []string{http.MethodGet, http.MethodHead} {
		t.Run(method, func(t *testing.T) {
			rec := httptest.NewRecorder()
			FileServer(fileSystem).ServeHTTP(rec, httptest.NewRequest(method, "/missing-route", nil))
			if rec.Code != http.StatusOK {
				t.Fatalf("got status %d; want 200", rec.Code)
			}
			if rec.Header().Get("Cache-Control") != "no-cache" {
				t.Fatalf("unexpected bootstrap cache policy: %q", rec.Header().Get("Cache-Control"))
			}
			if method == http.MethodGet && rec.Body.String() != `<html><head><base href="/"/></head><body>Welcome</body></html>` {
				t.Fatalf("bootstrap content not rewritten: %q", rec.Body.String())
			}
			if method == http.MethodHead && rec.Body.Len() != 0 {
				t.Fatalf("HEAD served %d HTML body bytes", rec.Body.Len())
			}
		})
	}
}

func TestFileServerPreservesFileNotFound(t *testing.T) {
	fileSystem := fstest.MapFS{}
	rec := httptest.NewRecorder()
	FileServer(fileSystem).ServeHTTP(rec, httptest.NewRequest(http.MethodGet, "/missing", nil))
	if rec.Code != http.StatusNotFound {
		t.Fatalf("missing static asset: got status %d", rec.Code)
	}
}

func TestNonSeekableAssetsRetainHeadAndFullStreamFallback(t *testing.T) {
	fileSystem := smallChunkFS{FS: fstest.MapFS{
		"payload.bin": &fstest.MapFile{Data: []byte("original-file")},
	}}
	handler := FileServer(fileSystem)
	for _, tc := range []struct {
		name, method, rangeHeader, wantBody, wantLength string
	}{
		{name: "head", method: http.MethodHead, wantLength: "13"},
		{name: "range fallback", method: http.MethodGet, rangeHeader: "bytes=1-3", wantBody: "original-file"},
	} {
		t.Run(tc.name, func(t *testing.T) {
			rec := httptest.NewRecorder()
			req := httptest.NewRequest(tc.method, "/payload.bin", nil)
			if tc.rangeHeader != "" {
				req.Header.Set("Range", tc.rangeHeader)
			}
			handler.ServeHTTP(rec, req)
			if rec.Code != http.StatusOK {
				t.Fatalf("got status %d; want 200", rec.Code)
			}
			if rec.Body.String() != tc.wantBody {
				t.Fatalf("got fallback body %q, want %q", rec.Body.String(), tc.wantBody)
			}
			if tc.wantLength != "" && rec.Header().Get("Content-Length") != tc.wantLength {
				t.Fatalf("got Content-Length %q, want %q", rec.Header().Get("Content-Length"), tc.wantLength)
			}
		})
	}
}
