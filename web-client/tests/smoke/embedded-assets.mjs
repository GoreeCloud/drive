// Browser-level contract test for the *actual embedded* GoreeCloud Drive
// frontend and Go static server. No authentication or production data is used.
import assert from 'node:assert/strict'
import { chromium } from 'playwright'

const baseURL = process.env.GOREECLOUD_EMBEDDED_SMOKE_URL || 'http://127.0.0.1:18523'
const base = new URL(baseURL)
if (base.hostname !== '127.0.0.1' || base.protocol !== 'http:') {
  throw new Error('Embedded browser smoke test must target HTTP on 127.0.0.1 only')
}
const options = { headless: true }
if (process.env.GOREECLOUD_CHROMIUM_PATH) {
  options.executablePath = process.env.GOREECLOUD_CHROMIUM_PATH
}
const browser = await chromium.launch(options)
try {
  for (const width of [1366, 390]) {
    const context = await browser.newContext({ viewport: { width, height: 840 } })
    try {
      const page = await context.newPage()
      const response = await page.goto(baseURL, { waitUntil: 'domcontentloaded', timeout: 30000 })
      assert.equal(response?.status(), 200, 'embedded app bootstrap must be served')
      assert.equal(await page.title(), 'GoreeCloud Drive', 'correct frontend title must render')

      const scripts = await page.locator('script[src]').evaluateAll((nodes) =>
        nodes.map((node) => node.getAttribute('src')).filter(Boolean)
      )
      assert.ok(scripts.length > 0, 'compiled browser entrypoint must register a script')
      const realScript = await page.request.get(new URL(scripts[0], baseURL).toString())
      assert.equal(realScript.status(), 200, 'registered JS module must exist')
      assert.match(realScript.headers()['content-type'] || '', /javascript|ecmascript/, 'JS content type')

      const deepLink = await page.request.get(baseURL + '/files/list', {
        headers: { Accept: 'text/html,application/xhtml+xml' }
      })
      assert.equal(deepLink.status(), 200, 'SPA document deep link')
      assert.equal(deepLink.headers()['cache-control'], 'no-cache')
      assert.match(await deepLink.text(), /GoreeCloud Drive/, 'expected app shell')

      for (const missingPath of [
        '/js/nonexistent-goreecloud-module.mjs',
        '/css/nonexistent-goreecloud-style.css',
        '/img/nonexistent-goreecloud-icon.svg'
      ]) {
        const missing = await page.request.get(baseURL + missingPath, {
          headers: { Accept: '*/*' }
        })
        assert.equal(missing.status(), 404, 'missing asset must not return app HTML: ' + missingPath)
        assert.doesNotMatch(await missing.text(), /<title>GoreeCloud Drive/, 'must not leak HTML app shell')
      }
      const spoof = await page.request.get(baseURL + '/js/nonexistent-goreecloud-module.mjs', {
        headers: { Accept: 'text/html' }
      })
      assert.equal(spoof.status(), 404, 'HTML navigation cannot spoof JS response')
      const invalidMethod = await page.request.post(baseURL + '/js/nonexistent-goreecloud-module.mjs')
      assert.equal(invalidMethod.status(), 405)
      assert.equal(invalidMethod.headers().allow, 'GET, HEAD')

      console.log('PASS: embedded GoreeCloud Drive browser delivery', { width, scripts: scripts.length })
    } finally {
      await context.close()
    }
  }
} finally {
  await browser.close()
}
