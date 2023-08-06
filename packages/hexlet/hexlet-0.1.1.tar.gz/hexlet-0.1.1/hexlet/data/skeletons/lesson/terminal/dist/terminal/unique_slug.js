/* global define */

define('terminal/strings',{
  en: {
    translation: {
      "bash_man": {
        "success": "What manual page do you want?"
      },
      "bashInterpreterOnStart": "Trying 95.85.32.220...\nConnected to __addr__.\nEscape character is.",
      "bashInterpreterOnStop": "Connection closed by foreign host.",
      "bashInterpreterErrors": {
        "telnetUsage": "USAGE: telnet host port"
      }
    }
  },

  ru: {
    translation: {
      "bashInterpreterErrors": {
        "needAnotherSite": "нам нужно на __addr__",
        "needAnotherPort": "http сервер находится на 80 порту",
        "commandNotFound": ": command not found"
      }
    }
  }
});

/* global define $ _ i18n */

define('terminal/setup',["terminal/strings"], function(strings) {
  
  i18n.init({
    resStore: strings,
    lng: "ru",
    fallbackLng: "en"
  });
});

/* global define $ _ i18n */

define('terminal/unique_slug',["terminal/setup"], function() {
  
  return function(success) {
      var bashInterpreter = {
        handler: function(command, term) {
          var expectedSite = "codebattle.io";
          var prog = $.terminal.parseCommand(command);
          if (prog.name === "") { return; }
          if (prog.name === "telnet") {
            if (prog.args.length === 2) {
              var site = prog.args[0];
              var port = prog.args[1];
              var expectedPort = 80;

              var hasError = false;

              if (site !== expectedSite) {
                hasError = true;
                term.error($.t("bashInterpreterErrors.needAnotherSite", {
                  addr: expectedSite
                }));
              }
              if (port !== expectedPort) {
                hasError = true;
                term.error($.t("bashInterpreterErrors.needAnotherPort"));
              }

              if (!hasError) {
                // result.addHint("обратите внимание, несмотря на то что здесь указан host,\nна самом деле мы соединяемся с сервером (а его ip находится с помощью dns)");
                // console.log(telnetInterpreter.handler.bind(obj))
                term.echo($.t("bashInterpreterOnStart", {
                  addr: "codebattle.io"
                }));
                success();
              }
            } else {
              term.echo($.t("bashInterpreterErrors.telnetUsage"));
            }
          } else {
            term.error(_.join("bash: ", prog.name, $.t("bashInterpreterErrors.commandNotFound")));
          }
        },
        object: {
          greetings: "",
          name: "bash",
          prompt: "$ "
        }
      };

      return bashInterpreter;
    };
});

