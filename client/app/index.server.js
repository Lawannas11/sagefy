const express = require('express')
const toHTML = require('vdom-to-html')
const template = require('./views/index.tmpl')
const {route} = require('./modules/route_actions')
const store = require('./modules/store')
const reducer = require('./reducers/index')
const cookieParser = require('cookie-parser')

// Require all tasks
require('./tasks/card')
require('./tasks/follow')
require('./tasks/form')
require('./tasks/menu')
require('./tasks/notice')
require('./tasks/post')
require('./tasks/route')
require('./tasks/search')
require('./tasks/set')
require('./tasks/topic')
require('./tasks/unit')
require('./tasks/user')
require('./tasks/user_sets')

const app = express()
app.use(cookieParser())

store.setReducer(reducer)

const htmlTop = [
    '<!doctype html>',
    '<meta charset="utf-8">',
    '<meta name="viewport" content="width=device-width, initial-scale=1">',
    '<link rel="stylesheet" href="/index.css?___">',
    '<script src="/index.js?___"></script>',
    '<body>',
].join('')

const htmlBottom = '</body>'

function render() {
    const state = store.data
    return htmlTop +
           toHTML(template(state)) +
           `<script>window.preload=${JSON.stringify(state)}</script>` +
           htmlBottom
}

app.get(/.*/, (request, response) => {
    const path = request.originalUrl
    console.log(path) // eslint-disable-line
    store.data = {} // make sure it doesn't use a pre-existing state
    if(request.cookies) {
        store.dispatch({
            type: 'SET_CURRENT_USER_ID',
            currentUserID: request.cookies.currentUserID,
        })
    }
    global.requestCookie = `session_id=${request.cookies.session_id}`
    const promise = route(path)
    if (promise) {
        promise.then(() => {
            response.status(200).send(render())
        }).catch((error) => {
            console.error(error) // eslint-disable-line
        })
    } else {
        response.status(200).send(render())
    }
})

app.listen(5984, () => {
    console.log('serving app realness') // eslint-disable-line
})
