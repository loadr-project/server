import React from 'react';
import ReactDOM from 'react-dom';
import './index.scss';
import App from './App';
import * as serviceWorker from './serviceWorker';
import {Share} from "./Share";

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.register();

window.addEventListener('load', () => {
  // TODO: this doesn't seem to work??
  // TODO: this should be in component for loading animation etc.
  // @ts-ignore
  const parsedUrl = new URL(window.location);
  console.log('Title shared: ' + parsedUrl.searchParams.get('name'));
  console.log('Text shared: ' + parsedUrl.searchParams.get('description'));
  console.log('Link shared: ' + parsedUrl.searchParams.get('link'));
  console.log('URL shared: ' + parsedUrl.searchParams.get('url'));
  if(parsedUrl.searchParams.get('link') !== null) {
    const share = new Share();
    share.share(parsedUrl.searchParams.get('link'));
  } else if(parsedUrl.searchParams.get('url') !== null) {
    const share = new Share();
    share.share(parsedUrl.searchParams.get('url'));
  }
});
