import ReactDOM from "react-dom"

// setup adaptor for enzyme
// see http://airbnb.io/enzyme/docs/installation/index.html
import { configure } from "enzyme"
import Adapter from "enzyme-adapter-react-16"

configure({ adapter: new Adapter() })
// Define globals we would usually get from Django
const _createSettings = () => ({})

global.SETTINGS = _createSettings()
global._testing = true
global.CSOURCE_PAYLOAD = null

window.scrollTo = () => "scroll!"

// polyfill for Object.entries
import entries from "object.entries"
if (!Object.entries) {
  entries.shim()
}

// eslint-disable-next-line mocha/no-top-level-hooks
afterEach(() => {
  const node = document.querySelector("#integration_test_div")
  if (node) {
    ReactDOM.unmountComponentAtNode(node)
  }
  document.body.innerHTML = ""
  global.SETTINGS = _createSettings()
  window.location = "http://fake/"
})

// enable chai-as-promised
import chai from "chai"
import chaiAsPromised from "chai-as-promised"
chai.use(chaiAsPromised)
