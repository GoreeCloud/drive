package theme

import (
	"errors"
	"image"
	_ "image/gif"
	_ "image/jpeg"
	_ "image/png"
	"io"
	"mime/multipart"
	"net/http"
)

// Limit both the image and the surrounding multipart request. The latter bound
// prevents excessive temporary disk use while parsing unauthenticated input.
const (
	maxLogoBytes        int64 = 5 << 20
	maxLogoRequestBytes int64 = maxLogoBytes + (64 << 10)
	maxLogoDimension          = 4096
	maxLogoPixels       int64 = 16_000_000
)

var (
	errInvalidLogo  = errors.New("invalid logo image")
	errLogoTooLarge = errors.New("logo image too large")
)

// validateLogoUpload verifies both the declared type and the actual image
// format before the request body is copied into persistent theme storage.
// The caller must have already parsed a size-limited multipart request.
func validateLogoUpload(file io.ReadSeeker, header *multipart.FileHeader) error {
	if header == nil || header.Size <= 0 {
		return errInvalidLogo
	}
	if header.Size > maxLogoBytes {
		return errLogoTooLarge
	}
	declaredType := header.Header.Get("Content-Type")
	if !isFiletypePermitted(header.Filename, declaredType) {
		return errInvalidLogo
	}

	// MIME checks alone can be spoofed; decode the format metadata and enforce
	// sane dimensions before accepting the data into theme storage.
	cfg, format, err := image.DecodeConfig(file)
	if err != nil {
		return errInvalidLogo
	}
	actualType := map[string]string{
		"jpeg": "image/jpeg",
		"png":  "image/png",
		"gif":  "image/gif",
	}[format]
	if actualType == "" || actualType != declaredType {
		return errInvalidLogo
	}
	if cfg.Width <= 0 || cfg.Height <= 0 ||
		cfg.Width > maxLogoDimension || cfg.Height > maxLogoDimension ||
		int64(cfg.Width)*int64(cfg.Height) > maxLogoPixels {
		return errInvalidLogo
	}
	if _, err := file.Seek(0, io.SeekStart); err != nil {
		return err
	}
	return nil
}

// classifyLogoUploadError distinguishes malformed/overlarge input from
// failures inside storage or seek operations, without leaking internal errors.
func classifyLogoUploadError(err error) int {
	if err == nil {
		return http.StatusOK
	}
	var maxErr *http.MaxBytesError
	if errors.Is(err, errLogoTooLarge) || errors.As(err, &maxErr) {
		return http.StatusRequestEntityTooLarge
	}
	if errors.Is(err, errInvalidLogo) || errors.Is(err, http.ErrMissingFile) {
		return http.StatusBadRequest
	}
	return http.StatusInternalServerError
}
