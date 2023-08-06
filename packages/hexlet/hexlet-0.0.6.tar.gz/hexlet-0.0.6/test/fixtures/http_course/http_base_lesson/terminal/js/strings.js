"use strict";

define({
    en: {
        translation: {
            'bashInterpreterOnStart': 'Trying 95.85.32.220...\nConnected to __addr__.\nEscape character is.',
            'bashInterpreterOnStop': 'Connection closed by foreign host.',

            'bashInterpreterErrors': {
                'telnetUsage': 'USAGE: telnet host port'
            }
        }
    },

    ru: {
        translation: {

            'fail': [
                'Работая в telnet ошибаться нельзя.',
                'Так как после перевода строки, данные уходят на сервер.'
            ].join("\n"),

            'responseBadRequest10': [
                'HTTP/1.1 400 Bad Request',
                'Server: nginx/1.4.7',
                'Date: Sun, 11 May 2014 14:08:51 GMT',
                'Content-Type: text/html',
                'Content-Length: 172',
                'Connection: close',

                '<html>',
                '<head><title>400 Bad Request</title></head>',
                '<body bgcolor="white">',
                '<center><h1>400 Bad Request</h1></center>',
                '<hr><center>nginx/1.4.7</center>',
                '</body>',
                '</html>'
            ].join("\n"),

            'response10': [
                'HTTP/1.0 302 Found',
                'Cache-Control: private',
                'Content-Type: text/html; charset=UTF-8',
                'Location: http://www.google.ru/?gfe_rd=cr',
                'Content-Length: 256',
                'Date: Sun, 11 May 2014 13:30:38 GMT',
                'Server: GFE/2.0',
                'Alternate-Protocol: 80:quic',

                '<HTML><HEAD><meta http-equiv="content-type" content="text/html;charset=utf-8">',
                '<TITLE>302 Moved</TITLE></HEAD><BODY>',
                '<H1>302 Moved</H1>',
                'The document has moved',
                '<A HREF="http://www.google.ru/?gfe_rd=cr">here</A>.',
                '</BODY></HTML>'
            ].join("\n"),

            'response11': [
                'HTTP/1.1 200 OK',
                'Server: nginx/1.4.7',
                'Date: Wed, 16 Apr 2014 10:46:38 GMT',
                'Content-Type: text/html',
                'Content-Length: 612',
                'Last-Modified: Tue, 18 Mar 2014 13:17:09 GMT',
                'Connection: close',
                '\n\n',
                '<!DOCTYPE html>',
                '<html>',
                '  <head>',
                '    <title>Welcome to nginx!</title>',
                '  </head>',
                '  <body>',
                '    <h1>Welcome to nginx!</h1>',
                '  </body>',
                '</html>'
            ].join("\n"),

            'bashInterpreterErrors': {
                'needAnotherSite': 'нам нужно на __addr__',
                'needAnotherPort': 'http сервер находится на 80 порту',
                'commandNotFound': ': command not found'
            },

            'http11Msgs': {
                'wrongProtocolVersion': 'Не та версия протокола ;)',
                'wrongHost': 'а хост-то не тот ;)',
                'noHeader': 'не указан обязательный заголовок'
            },

            'http10Msgs': {
                'wrongProtocolVersion': 'Не та версия протокола ;)',
                'notRequiredHost': 'В http 1.0 не существует понятия virtual host, поэтому заголовок host не нужен.'
            },

            'postRequestMsgs': {
                'wrongMethod': 'Неправильный метод запроса',
                'noHostName': 'Не указано имя хоста',
                'wrongHostName': 'Неправильное имя хоста',
                'noContentType': 'Не указан тип контента',
                'wrongContentType': 'Неправильный тип контента',
                'wrongContent': 'Неправильный контент',
                'noContentLength': 'Не указана длина контента',
                'wrongContentLength': 'Неправильная длина контента'
            },

            'postResponse': [
                'HTTP/1.1 302 Found',
                'Server: nginx/1.4.5',
                'Date: Thu, 15 May 2014 13:55:34 GMT',
                'Content-Type: text/html; charset=utf-8',
                'Transfer-Encoding: chunked',
                'Connection: keep-alive',
                'Status: 302 Found',
                'Location: http://coursify.ru/',
                'Cache-Control: no-cache'
            ].join('\n'),

            'response400': [
                'HTTP/1.1 400 Bad Request',
                'Server: nginx/1.4.5',
                'Date: Fri, 16 May 2014 08:49:51 GMT',
                'Content-Type: text/html; charset=utf-8',
                'Content-Length: 0',
                'Connection: keep-alive',
                'Status: 400 Bad Request'
            ].join('\n'),

            'response404': [
                'HTTP/1.1 404 Not Found',
                'Server: nginx/1.4.5',
                'Date: Fri, 16 May 2014 08:53:07 GMT',
                'Content-Type: text/html; charset=utf-8',
                'Transfer-Encoding: chunked',
                'Connection: keep-alive',
                'Status: 404 Not Found',
                'Content-Encoding: gzip'
            ].join('\n'),

            'taskSuccessfullyCompleted': 'Задание успешно выполнено',
            'necessaryHeadersNotSpecified': 'Не указаны необходимые http-заголовки'
        }
    }
})