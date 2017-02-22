var path = require("path");
var webpack = require("webpack");

module.exports = {
  entry: {
    'root': './static/js/root',
    'style': './static/js/style',
  },
  output: {
    path: path.resolve('./static/bundles/'),
    filename: "[name].js"
  },

  module: {
    loaders: [
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        loader: 'babel-loader',
        query: {
          presets: ['es2015', 'stage-1', 'react']
        }
      },  // to transform JSX into JS
      {
        test: /\.(svg|ttf|woff|woff2|eot)$/,
        exclude: /node_modules/,
        loader: 'url-loader'
      },
      {
        test: /\.scss$/,
        exclude: /node_modules/,
        loader: 'style!css!sass'
      },
      {
        test: /\.css$/,
        exclude: /node_modules/,
        loader: 'style!css'
      },
    ]
  },

  resolve: {
    modulesDirectories: ['node_modules'],
    extensions: ['', '.js', '.jsx']
  }
};
