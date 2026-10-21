package assets

import (
	"bytes"
	"io"
	"io/fs"
	"mime"
	"net/http"
	"path"
	"path/filepath"
	"strconv"
	"time"

	"golang.org/x/net/html"
)

type fileServer struct {
	fsys http.FileSystem
}

// FileServer defines the http handler for the embedded files
func FileServer(fsys fs.FS) http.Handler {
	return &fileServer{http.FS(fsys)}
}

func (f *fileServer) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	uPath := path.Clean(path.Join("/", r.URL.Path))
	r.URL.Path = uPath

	tryIndex := func() {
		r.URL.Path = "/index.html"

		// not every fs contains a file named index.html,
		// therefore, we need to check if the file exists and stop the recursion if it doesn't
		file, err := f.fsys.Open(r.URL.Path)
		if err != nil {
			http.NotFound(w, r)
			return
		}
		defer file.Close()

		f.ServeHTTP(w, r)
	}

	asset, err := f.fsys.Open(uPath)
	if err != nil {
		tryIndex()
		return
	}
	defer asset.Close()

	s, err := asset.Stat()
	if err != nil {
		http.Error(w, "could not inspect requested asset", http.StatusInternalServerError)
		return
	}
	if s.IsDir() {
		tryIndex()
		return
	}

	w.Header().Set("Content-Type", mime.TypeByExtension(filepath.Ext(s.Name())))

	switch s.Name() {
	case "index.html", "oidc-callback.html", "oidc-silent-redirect.html":
		w.Header().Del("Expires")
		w.Header().Set("Cache-Control", "no-cache")
		buf := new(bytes.Buffer)
		if err := withBase(buf, asset, "/"); err != nil {
			http.Error(w, "could not process HTML asset", http.StatusInternalServerError)
			return
		}
		// This is a transformed HTML document, so serve the transformed bytes
		// rather than the upstream file's size or modification timestamp.
		http.ServeContent(w, r, s.Name(), time.Time{}, bytes.NewReader(buf.Bytes()))
	default:
		// Most embedded assets are seekable. ServeContent supports byte ranges,
		// HEAD, and conditional responses without buffering the file.
		// Preserve streaming compatibility for alternate non-seekable fs.FS
		// implementations, including remote and generated asset sources.
		if _, err := asset.Seek(0, io.SeekCurrent); err == nil {
			http.ServeContent(w, r, s.Name(), s.ModTime(), asset)
			return
		}
		if r.Method == http.MethodHead {
			w.Header().Set("Content-Length", strconv.FormatInt(s.Size(), 10))
			return
		}
		_, _ = io.Copy(w, asset)
	}
}

func withBase(w io.Writer, r io.Reader, base string) error {
	doc, err := html.Parse(r)
	if err != nil {
		return err
	}
	var parse func(*html.Node)
	parse = func(n *html.Node) {
		if n.Type == html.ElementNode && n.Data == "head" {
			n.InsertBefore(&html.Node{
				Type: html.ElementNode,
				Data: "base",
				Attr: []html.Attribute{
					{
						Key: "href",
						Val: base,
					},
				},
			}, n.FirstChild)

			return
		}

		for c := n.FirstChild; c != nil; c = c.NextSibling {
			parse(c)
		}
	}
	parse(doc)

	return html.Render(w, doc)
}
