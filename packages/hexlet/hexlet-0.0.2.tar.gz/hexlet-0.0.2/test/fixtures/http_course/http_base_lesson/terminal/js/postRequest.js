'use strict';

define(['strings', 'bashInterpreter'], function(strings, bashFn) {
  i18n.init({
    resStore: strings,
    lng: 'ru',
    fallbackLng: 'en'
  });
  _.mixin(_.string.exports());

  return function(success, error) {
    var expectedSite = 'coursify.ru',
      expectedPage = '/login',
      expectedContent = 'login=user&password=12345678',
      expectedContentType = 'application/x-www-form-urlencoded';

    var telnetInterpreter = function() {
      var currentState = 'waitForQuery';
      var headers = {
        'host': undefined,
        'content-type': undefined,
        'content-length': undefined
      };

      function resetInterpreter() {
        currentState = 'waitForQuery';
        headers = {
          'host': undefined,
          'content-type': undefined,
          'content-length': undefined
        };
      }

      return function(command, term) {
        switch (currentState) {
          case 'waitForQuery':
            var matches = command.match(/(\S+)(?:\s+)(\S+)(?:\s)HTTP\/1.1/);
            if (!matches) {
              term.pop();
              term.error($.t('fail'));
            } else if (matches[1] !== 'POST') {
              term.pop();
              term.error($.t('postRequestMsgs.wrongMethod'));
              error();
            } else if (matches[2] !== expectedPage) {
              term.pop();
              term.error($.t('response404'));
              error();
            } else {
              currentState = 'waitForHeaders';
            }
            break;
          case 'waitForHeaders':
            if (command !== '') {
              var matches = command.match(/(.+?):(.+)/);
              if (matches) {
                headers[matches[1].trim().toLowerCase()] = matches[2].trim().toLowerCase();
              } else {
                term.pop();
                term.error($.t('fail'));
                resetInterpreter();
              }
            } else {
              currentState = 'waitForContent';
            }
            break;
          case 'waitForContent':
            if (command === '') {
              if (headers['host'] !== undefined &&
                headers['content-type'] !== undefined &&
                headers['content-length'] !== undefined) {
                term.echo($.t('postResponse'));
                term.pop();
                success();
                term.echo($.t('taskSuccessfullyCompleted'));
              } else {
                term.pop();
                error();
                term.error($.t('necessaryHeadersNotSpecified'));
              }
              resetInterpreter();
            } else {
              command = _(command).unescapeHTML();

              if (headers['host'] !== expectedSite) {
                term.echo($.t('response400'));
                term.pop();
                if (headers['host'] === undefined) {
                  term.error($.t('postRequestMsgs.noHostName'));
                } else {
                  term.error($.t('postRequestMsgs.wrongHostName'));
                }
                error();
                resetInterpreter();
              } else if (headers['content-type'] != expectedContentType) {
                term.echo($.t('response400'));
                term.pop();
                if (headers['content-type'] === undefined) {
                  term.error($.t('postRequestMsgs.noContentType'));
                } else {
                  term.error($.t('postRequestMsgs.wrongContentType'));
                }
                error();
                resetInterpreter();
              } else if (command.length !== parseInt(headers['content-length'])) {
                term.echo($.t('response400'));
                term.pop();
                if (headers['content-length'] === undefined) {
                  term.error($.t('postRequestMsgs.noContentLength'));
                } else {
                  term.error($.t('postRequestMsgs.wrongContentLength'));
                }
                error();
                resetInterpreter();
              } else if (command !== expectedContent) {
                term.pop();
                term.error($.t('postRequestMsgs.wrongContent'));
                error();
                resetInterpreter();
              }
            }
            break;
        }
      }
    }

    var options = {
      name: 'telnet',
      onStart: function(term) {
        term.set_prompt('');
        term.echo($.t('bashInterpreterOnStart', {
          addr: expectedSite
        }));
      },
      onExit: function(term) {
        term.echo($.t('bashInterpreterOnStop'));
      }
    }

    return bashFn(expectedSite, telnetInterpreter(), options);
  }
});