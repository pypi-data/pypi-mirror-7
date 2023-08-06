'use strict';

define(['strings'], function(strings) {
  i18n.init({
    resStore: strings,
    lng: 'ru',
    fallbackLng: 'en'
  });

  return function(expectedSite, nextInterpreter, options) {
    var bashInterpreter = {
      handler: function(command, term) {
        var prog = $.terminal.parseCommand(command);
        if (prog.name == '') return;
        if (prog.name == 'telnet') {
          if (prog.args.length == 2) {
            var site = prog.args[0];
            var port = prog.args[1];
            var expectedPort = 80;

            var has_error = false;

            if (site !== expectedSite) {
              has_error = true;
              term.error($.t('bashInterpreterErrors.needAnotherSite', {
                addr: expectedSite
              }));
            }
            if (port !== expectedPort) {
              has_error = true;
              term.error($.t('bashInterpreterErrors.needAnotherPort'));
            }

            if (!has_error) {
              // result.addHint('обратите внимание, несмотря на то что здесь указан host,\nна самом деле мы соединяемся с сервером (а его ip находится с помощью dns)');
              // console.log(telnetInterpreter.handler.bind(obj))
              term.push(nextInterpreter, options)
            }
          } else {
            term.echo($.t('bashInterpreterErrors.telnetUsage'));
          }
        } else {
          term.error('bash: ' + prog.name + $.t('bashInterpreterErrors.commandNotFound'));
        }
      },
      object: {
        greetings: '',
        name: 'bash',
        prompt: '$ '
      }
    };

    return bashInterpreter;
  }
})