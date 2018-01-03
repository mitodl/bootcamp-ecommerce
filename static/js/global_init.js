// Define globals we would usually get from Django
const _createSettings = () => ({
  user: {
    full_name: "Jane Doe",
    username:  "janedoe"
  }
})

global.SETTINGS = _createSettings()

// polyfill for Object.entries
import entries from "object.entries"
if (!Object.entries) {
  entries.shim()
}

// eslint-disable-next-line mocha/no-top-level-hooks
afterEach(() => {
  document.body.innerHTML = ""
  global.SETTINGS = _createSettings()
  window.location = "http://fake/"
})

// enable chai-as-promised
import chai from "chai"
import chaiAsPromised from "chai-as-promised"
chai.use(chaiAsPromised)
