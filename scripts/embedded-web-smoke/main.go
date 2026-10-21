// Embedded Files frontend HTTP fixture for isolated browser-delivery tests.
// It serves no user data, authentication, production configuration or storage.
package main

import (
	"io/fs"
	"log"
	"net"
	"net/http"
	"os"
	"time"

	web "github.com/opencloud-eu/opencloud/services/web"
	"github.com/opencloud-eu/opencloud/services/web/pkg/assets"
)

func main() {
	addr := os.Getenv("GOREECLOUD_EMBEDDED_SMOKE_ADDR")
	if addr == "" {
		addr = "127.0.0.1:18523"
	}
	host, _, err := net.SplitHostPort(addr)
	if err != nil {
		log.Fatal(err)
	}
	ip := net.ParseIP(host)
	if ip == nil || !ip.IsLoopback() {
		log.Fatal("embedded browser fixture must bind only to loopback")
	}

	core, err := fs.Sub(web.Assets, "assets/core")
	if err != nil {
		log.Fatal(err)
	}
	server := &http.Server{
		Addr:              addr,
		Handler:           assets.FileServer(core),
		ReadHeaderTimeout: 5 * time.Second,
	}
	log.Printf("Serving development-only GoreeCloud Drive static assets at http://%s", addr)
	log.Fatal(server.ListenAndServe())
}
