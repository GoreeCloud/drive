package assets

import (
	"bytes"
	"errors"
	"io"
	"io/fs"
	"net/http"
	"net/http/httptest"
	"testing"
	"testing/fstest"
)

type smallChunkFS struct{ fs.FS }

func (s smallChunkFS) Open(name string) (fs.File, error) {
	f, err := s.FS.Open(name)
	if err != nil {
		return nil, err
	}
	return &smallChunkFile{File: f}, nil
}

type smallChunkFile struct{ fs.File }

func (f *smallChunkFile) Read(p []byte) (int, error) {
	if len(p) > 1024 {
		p = p[:1024]
	}
	return f.File.Read(p)
}

type writeSizeRecorder struct {
	header  http.Header
	status  int
	total   int
	largest int
}

func (r *writeSizeRecorder) Header() http.Header {
	return r.header
}

func (r *writeSizeRecorder) WriteHeader(code int) {
	r.status = code
}

func (r *writeSizeRecorder) Write(p []byte) (int, error) {
	if r.status == 0 {
		r.status = http.StatusOK
	}
	r.total += len(p)
	if len(p) > r.largest {
		r.largest = len(p)
	}
	return len(p), nil
}

func TestStaticAssetsAreStreamedInBoundedWrites(t *testing.T) {
	const assetSize = 2 << 20
	fsys := smallChunkFS{FS: fstest.MapFS{"bundle.js": &fstest.MapFile{Data: bytes.Repeat([]byte("a"), assetSize)}}}
	w := &writeSizeRecorder{header: make(http.Header)}
	FileServer(fsys).ServeHTTP(w, httptest.NewRequest(http.MethodGet, "/bundle.js", nil))
	if w.status != http.StatusOK || w.total != assetSize {
		t.Fatalf("asset response: status %d, bytes %d; want 200 and %d", w.status, w.total, assetSize)
	}
	if w.largest > 1024 {
		t.Fatalf("static asset buffered into a %d-byte write; expected streaming", w.largest)
	}
}

type failedAssetFile struct{ fs.File }

func (f *failedAssetFile) Stat() (fs.FileInfo, error) {
	return nil, errors.New("injected filesystem stat failure")
}

type failedStatFS struct{ fs.FS }

func (s failedStatFS) Open(name string) (fs.File, error) {
	f, err := s.FS.Open(name)
	if err != nil {
		return nil, err
	}
	return &failedAssetFile{File: f}, nil
}

func TestFileServerReturns500WhenAssetStatFails(t *testing.T) {
	fsys := failedStatFS{FS: fstest.MapFS{"file.txt": &fstest.MapFile{Data: []byte("secret")}}}
	w := httptest.NewRecorder()
	FileServer(fsys).ServeHTTP(w, httptest.NewRequest(http.MethodGet, "/file.txt", nil))
	if w.Code != http.StatusInternalServerError {
		t.Fatalf("status %d; want 500", w.Code)
	}
	if bytes.Contains(w.Body.Bytes(), []byte("secret")) {
		t.Fatal("file bytes should not be sent after stat failure")
	}
}

type brokenHTMLReader struct{}

func (brokenHTMLReader) Read([]byte) (int, error) {
	return 0, errors.New("injected HTML read failure")
}

func TestWithBaseReturnsHTMLReaderError(t *testing.T) {
	var buf bytes.Buffer
	if err := withBase(&buf, io.Reader(brokenHTMLReader{}), "/"); err == nil {
		t.Fatal("expected HTML parse read error")
	}
	if buf.Len() != 0 {
		t.Fatalf("wrote %d bytes after parse failure", buf.Len())
	}
}
