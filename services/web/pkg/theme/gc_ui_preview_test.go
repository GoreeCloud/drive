package theme_test

import (
	"encoding/json"
	"fmt"
	"io/fs"
	"math"
	"net/http"
	"net/http/httptest"
	"strconv"
	"strings"
	"testing"

	gateway "github.com/cs3org/go-cs3apis/cs3/gateway/v1beta1"
	"github.com/opencloud-eu/opencloud/pkg/x/io/fsx"
	"github.com/opencloud-eu/opencloud/services/graph/mocks"
	web "github.com/opencloud-eu/opencloud/services/web"
	"github.com/opencloud-eu/opencloud/services/web/pkg/theme"
)

type embeddedTheme struct {
	Common struct {
		Name       string         `json:"name"`
		Logo       string         `json:"logo"`
		ShareRoles map[string]any `json:"shareRoles"`
	} `json:"common"`
	Clients struct {
		Web struct {
			Defaults map[string]string `json:"defaults"`
			Themes   []struct {
				IsDark       bool   `json:"isDark"`
				Label        string `json:"label"`
				Logo         string `json:"logo"`
				DesignTokens struct {
					Roles map[string]string `json:"roles"`
				} `json:"designTokens"`
			} `json:"themes"`
		} `json:"web"`
	} `json:"clients"`
}

func readEmbeddedTheme(t *testing.T, path string) embeddedTheme {
	t.Helper()
	raw, err := fs.ReadFile(web.Assets, path)
	if err != nil {
		t.Fatalf("read %s: %v", path, err)
	}
	var got embeddedTheme
	if err := json.Unmarshal(raw, &got); err != nil {
		t.Fatalf("decode %s: %v", path, err)
	}
	return got
}

func luminance(hex string) float64 {
	value, err := strconv.ParseUint(strings.TrimPrefix(hex, "#"), 16, 24)
	if err != nil {
		panic(fmt.Sprintf("invalid hex color %q: %v", hex, err))
	}
	components := []uint64{(value >> 16) & 0xff, (value >> 8) & 0xff, value & 0xff}
	var channels [3]float64
	for i, c := range components {
		v := float64(c) / 255
		if v <= 0.04045 {
			channels[i] = v / 12.92
		} else {
			channels[i] = math.Pow((v+0.055)/1.055, 2.4)
		}
	}
	return 0.2126*channels[0] + 0.7152*channels[1] + 0.0722*channels[2]
}

func contrast(a, b string) float64 {
	light, dark := luminance(a), luminance(b)
	if dark > light {
		light, dark = dark, light
	}
	return (light + 0.05) / (dark + 0.05)
}

func TestOptInGCUIThemePreservesUpstreamCompatibility(t *testing.T) {
	preview := readEmbeddedTheme(t, "assets/themes/goreecloud/theme.json")
	upstream := readEmbeddedTheme(t, "assets/themes/opencloud/theme.json")
	if preview.Common.Name != "GoreeCloud Drive — UI Foundations Preview" {
		t.Fatalf("unexpected preview name: %q", preview.Common.Name)
	}
	if len(preview.Common.ShareRoles) != len(upstream.Common.ShareRoles) {
		t.Fatalf("preview dropped inherited share-role metadata")
	}
	for key := range upstream.Common.ShareRoles {
		if _, ok := preview.Common.ShareRoles[key]; !ok {
			t.Fatalf("missing inherited role %s", key)
		}
	}
	if len(preview.Clients.Web.Themes) != 2 || len(upstream.Clients.Web.Themes) != 2 {
		t.Fatalf("expected compatible light and dark theme variants")
	}
	if preview.Common.Logo != upstream.Common.Logo {
		t.Fatalf("preview must not replace upstream mark with an unapproved product identity")
	}
	for name, icon := range preview.Clients.Web.Defaults {
		if _, err := fs.Stat(web.Assets, "assets/"+icon); err != nil {
			t.Fatalf("default %s references absent icon %q: %v", name, icon, err)
		}
	}
	for i, theme := range preview.Clients.Web.Themes {
		if theme.IsDark != (i == 1) {
			t.Fatalf("theme %d has wrong dark appearance", i)
		}
		if len(theme.DesignTokens.Roles) != len(upstream.Clients.Web.Themes[i].DesignTokens.Roles) {
			t.Fatalf("theme %d missing required client roles", i)
		}
		expected := "#5145D9"
		if i == 1 {
			expected = "#C5BFFF"
		}
		if theme.DesignTokens.Roles["primary"] != expected {
			t.Fatalf("mode %d primary token %q should derive from GC UI Foundations 1.0.1 %q", i, theme.DesignTokens.Roles["primary"], expected)
		}
		if theme.DesignTokens.Roles["background"] == upstream.Clients.Web.Themes[i].DesignTokens.Roles["background"] {
			t.Fatalf("mode %d should use GC UI Canvas mapping, not unchanged upstream colors", i)
		}
		for _, pair := range [][2]string{
			{"primary", "onPrimary"},
			{"secondary", "onSecondary"},
			{"tertiary", "onTertiary"},
			{"error", "onError"},
			{"background", "onBackground"},
			{"surface", "onSurface"},
		} {
			ratio := contrast(theme.DesignTokens.Roles[pair[0]], theme.DesignTokens.Roles[pair[1]])
			if ratio < 4.5 {
				t.Fatalf("mode %d %s/%s contrast %.2f < 4.5", i, pair[0], pair[1], ratio)
			}
		}
	}
}

func TestOptInGCUIThemeServedByRealThemeHandler(t *testing.T) {
	fallback := fsx.NewBasePathFs(fsx.FromIOFS(web.Assets), "assets/themes")
	service, err := theme.NewService(theme.ServiceOptions{}.
		WithThemeFS(fsx.NewFallbackFS(fsx.NewMemMapFs(), fallback)).
		WithGatewaySelector(mocks.NewSelectable[gateway.GatewayAPIClient](t)))
	if err != nil {
		t.Fatal(err)
	}
	r := httptest.NewRequest(http.MethodGet, "/themes/goreecloud/theme.json", nil)
	r.SetPathValue("id", "goreecloud")
	w := httptest.NewRecorder()
	service.Get(w, r)
	if w.Code != http.StatusOK {
		t.Fatalf("response status %d, body: %s", w.Code, w.Body.String())
	}
	var response embeddedTheme
	if err := json.Unmarshal(w.Body.Bytes(), &response); err != nil {
		t.Fatalf("handler returned invalid JSON: %v", err)
	}
	if response.Common.Name != "GoreeCloud Drive — UI Foundations Preview" {
		t.Fatalf("unexpected handler theme name: %q", response.Common.Name)
	}
	if len(response.Clients.Web.Themes) != 2 {
		t.Fatalf("expected both GC UI palette modes from the actual handler")
	}
}
