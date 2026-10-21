import app from '../../src/index'

vi.mock('vue3-gettext', () => ({
  useGettext: () => ({ $gettext: (value: string) => value })
}))
vi.mock('../../src/extensions', () => ({
  extensions: () => []
}))
vi.mock('../../src/extensionPoints', () => ({
  extensionPoints: () => []
}))

describe('Search application registration', () => {
  it('keeps Search application identity and extensions without an obsolete standalone route', () => {
    const registration = app.setup({ applicationConfig: {} as never })

    expect(registration.appInfo).toEqual({
      id: 'search',
      name: 'Search',
      icon: 'folder'
    })
    expect(registration).not.toHaveProperty('routes')
    expect(registration).toHaveProperty('extensions')
    expect(registration).toHaveProperty('extensionPoints')
    expect(registration).toHaveProperty('translations')
  })
})
