package theme_test

import (
	"net/http"
	"net/http/httptest"
	"testing"

	gateway "github.com/cs3org/go-cs3apis/cs3/gateway/v1beta1"

	"github.com/opencloud-eu/opencloud/pkg/x/io/fsx"
	"github.com/opencloud-eu/opencloud/services/graph/mocks"
	"github.com/opencloud-eu/opencloud/services/web/pkg/theme"
)

func TestLogoAdministrationRejectsUnauthenticatedRequests(t *testing.T) {
	service, err := theme.NewService(
		theme.ServiceOptions{}.
			WithThemeFS(fsx.NewFallbackFS(fsx.NewMemMapFs(), fsx.NewMemMapFs())).
			WithGatewaySelector(mocks.NewSelectable[gateway.GatewayAPIClient](t)),
	)
	if err != nil {
		t.Fatal(err)
	}
	tests := []struct {
		name    string
		method  string
		handler http.HandlerFunc
	}{
		{"upload", http.MethodPost, service.LogoUpload},
		{"reset", http.MethodDelete, service.LogoReset},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			recorder := httptest.NewRecorder()
			request := httptest.NewRequest(tc.method, "/branding/logo", nil)
			tc.handler(recorder, request)
			if recorder.Code != http.StatusUnauthorized {
				t.Fatalf("status %d; expected 401 for missing authenticated user", recorder.Code)
			}
		})
	}
}
