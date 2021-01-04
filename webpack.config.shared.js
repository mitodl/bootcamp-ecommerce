const path = require("path")
const webpack = require("webpack")

module.exports = {
  config: {
    entry: {
      root: ["core-js/stable", "regenerator-runtime/runtime", "./static/js/entry/root"],
      header: ["core-js/stable", "regenerator-runtime/runtime", "./static/js/entry/header"],
      sentry_client: './static/js/entry/sentry_client.js',
      style: "./static/js/entry/style",
      third_party:  "./static/js/entry/third-party",
    },
    module: {
      rules: [
        {
          test: /\.(svg|ttf|woff|woff2|eot|gif)$/,
          use:  "url-loader"
        },
        {
          test: require.resolve("jquery"),
          use:  [
            {
              loader:  "expose-loader",
              options: "jQuery"
            },
            {
              loader:  "expose-loader",
              options: "$"
            }
          ]
        }
      ]
    },
    resolve: {
      modules:    [path.join(__dirname, "static/js"), "node_modules"],
      extensions: [".js", ".jsx"]
    },
    performance: {
      hints: false
    }
  },
  babelSharedLoader: {
    test:    /\.jsx?$/,
    include: [
      path.resolve(__dirname, "static/js"),
      // The query-string is only published in ES6. These paths are added to transpile that library
      // and some of its dependencies to ES5.
      path.resolve(__dirname, "node_modules/query-string"),
      path.resolve(__dirname, "node_modules/strict-uri-encode"),
      path.resolve(__dirname, "node_modules/split-on-first"),
      path.resolve(__dirname, "node_modules/waait")
    ],
    loader:  "babel-loader",
    query:   {
      presets: [
        ["@babel/preset-env", { modules: false }],
        "@babel/preset-react",
        "@babel/preset-flow"
      ],
      plugins: [
        "react-hot-loader/babel",
        "@babel/plugin-proposal-object-rest-spread",
        "@babel/plugin-proposal-class-properties",
        "@babel/plugin-syntax-dynamic-import"
      ]
    }
  }
}
