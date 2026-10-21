package theme

import (
	"bytes"
	"errors"
	"image"
	"image/color"
	"image/gif"
	"image/jpeg"
	"image/png"
	"io"
	"mime/multipart"
	"net/http"
	"net/textproto"
	"testing"
)

func testLogoHeader(filename, contentType string, size int) *multipart.FileHeader {
	h := textproto.MIMEHeader{}
	h.Set("Content-Type", contentType)
	return &multipart.FileHeader{Filename: filename, Size: int64(size), Header: h}
}

func tinyPNG(t *testing.T) []byte {
	t.Helper()
	img := image.NewRGBA(image.Rect(0, 0, 2, 2))
	img.Set(0, 0, color.RGBA{R: 100, G: 100, B: 100, A: 255})
	var b bytes.Buffer
	if err := png.Encode(&b, img); err != nil {
		t.Fatal(err)
	}
	return b.Bytes()
}

func TestValidateLogoUpload(t *testing.T) {
	valid := tinyPNG(t)
	tests := []struct {
		name, filename, declaredType string
		payload                      []byte
		size                         int
		want                         error
	}{
		{name: "valid png", filename: "brand.png", declaredType: "image/png", payload: valid, size: len(valid)},
		{name: "extension mismatch", filename: "brand.jpg", declaredType: "image/png", payload: valid, size: len(valid), want: errInvalidLogo},
		{name: "declared mime mismatch", filename: "brand.png", declaredType: "image/jpeg", payload: valid, size: len(valid), want: errInvalidLogo},
		{name: "spoofed html", filename: "brand.png", declaredType: "image/png", payload: []byte("<script>alert(1)</script>"), size: len("<script>alert(1)</script>"), want: errInvalidLogo},
		{name: "incomplete png", filename: "brand.png", declaredType: "image/png", payload: valid[:9], size: 9, want: errInvalidLogo},
		{name: "empty", filename: "brand.png", declaredType: "image/png", payload: nil, size: 0, want: errInvalidLogo},
		{name: "oversized", filename: "brand.png", declaredType: "image/png", payload: valid, size: int(maxLogoBytes + 1), want: errLogoTooLarge},
		{name: "svg rejected", filename: "brand.svg", declaredType: "image/svg+xml", payload: []byte("<svg/>"), size: 6, want: errInvalidLogo},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			file := bytes.NewReader(tt.payload)
			err := validateLogoUpload(file, testLogoHeader(tt.filename, tt.declaredType, tt.size))
			if !errors.Is(err, tt.want) {
				t.Fatalf("validateLogoUpload() error = %v, want %v", err, tt.want)
			}
			if err == nil {
				// Reading image dimensions must not consume bytes that the
				// storage layer expects to receive in a successful upload.
				got, readErr := io.ReadAll(file)
				if readErr != nil || !bytes.Equal(got, tt.payload) {
					t.Fatalf("successful validation did not rewind the upload: %v", readErr)
				}
			}
		})
	}
}

func TestLogoUploadErrorStatus(t *testing.T) {
	if status := classifyLogoUploadError(http.ErrMissingFile); status != http.StatusBadRequest {
		t.Fatalf("missing file status = %d", status)
	}
	if status := classifyLogoUploadError(errInvalidLogo); status != http.StatusBadRequest {
		t.Fatalf("invalid image status = %d", status)
	}
	if status := classifyLogoUploadError(errLogoTooLarge); status != http.StatusRequestEntityTooLarge {
		t.Fatalf("oversized file status = %d", status)
	}
	if status := classifyLogoUploadError(&http.MaxBytesError{Limit: maxLogoRequestBytes}); status != http.StatusRequestEntityTooLarge {
		t.Fatalf("oversized request status = %d", status)
	}
	if status := classifyLogoUploadError(errors.New("disk failure")); status != http.StatusInternalServerError {
		t.Fatalf("internal error status = %d", status)
	}
}

func TestValidateOtherAllowedLogoFormats(t *testing.T) {
	img := image.NewRGBA(image.Rect(0, 0, 2, 2))
	for _, test := range []struct {
		name, filename, contentType string
		encode                      func(*bytes.Buffer) error
	}{
		{
			name: "jpeg", filename: "logo.jpg", contentType: "image/jpeg",
			encode: func(b *bytes.Buffer) error { return jpeg.Encode(b, img, nil) },
		},
		{
			name: "gif", filename: "logo.gif", contentType: "image/gif",
			encode: func(b *bytes.Buffer) error { return gif.Encode(b, img, nil) },
		},
	} {
		t.Run(test.name, func(t *testing.T) {
			var b bytes.Buffer
			if err := test.encode(&b); err != nil {
				t.Fatal(err)
			}
			data := b.Bytes()
			if err := validateLogoUpload(bytes.NewReader(data), testLogoHeader(test.filename, test.contentType, len(data))); err != nil {
				t.Fatalf("supported %s must be accepted: %v", test.contentType, err)
			}
		})
	}
}

func TestRejectOversizedLogoDimensions(t *testing.T) {
	img := image.NewRGBA(image.Rect(0, 0, maxLogoDimension+1, 1))
	var b bytes.Buffer
	if err := png.Encode(&b, img); err != nil {
		t.Fatal(err)
	}
	if err := validateLogoUpload(bytes.NewReader(b.Bytes()), testLogoHeader("wide.png", "image/png", b.Len())); !errors.Is(err, errInvalidLogo) {
		t.Fatalf("oversized pixel dimensions must be rejected, got %v", err)
	}
}
