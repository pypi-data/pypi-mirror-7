'use strict';

define(['strings', 'bashInterpreter'], function(strings, bashFn) {
  i18n.init({
    resStore: strings,
    lng: 'ru',
    fallbackLng: 'en'
  });

  return function(success, error) {
    var expectedSite = 'google.com'

    var telnetInterpreter = function() {
      var currentState = 'waitForQuery';
      var headers = {};

      function resetInterpreter() {
        currentState = 'waitForQuery';
        headers = {};
      }

      return function(command, term) {
        switch (currentState) {
          case 'waitForQuery':
            if (command === '') return;
            var matches = command.match(/GET(?:\s+)(\S+)(?:\s)HTTP\/1\.(\d)/);
            if (!matches) {
              term.pop();
              term.error($.t('fail'));
            } else if (matches[2] !== '0') {
              term.pop();
              term.error($.t('http10Msgs.wrongProtocolVersion'));
              error();
            } else {
              currentState = 'waiting';
            }
            break;

          case 'waiting':
            if (command === '') {
              if (headers.host) {
                term.error($.t('http10Msgs.notRequiredHost'));
                term.pop();
                error();
              } else {
                term.echo($.t('response10'));
                term.pop();
                success();
                term.echo($.t('taskSuccessfullyCompleted'));
              }
              resetInterpreter();
            } else {
              var matches = command.match(/(.+?):(.+)/);
              if (matches) {
                headers[matches[1].trim().toLowerCase()] = matches[2].trim().toLowerCase();
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

    var bashInterpreter = bashFn(expectedSite, telnetInterpreter(), options)

    return bashInterpreter;
  }
})
