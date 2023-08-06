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

define('terminal/bash_man',["terminal/setup"], function() {
  
  return function(success) {
      var bashInterpreter = {
        handler: function(command, term) {
          var expected = "man";
          var prog = $.terminal.parseCommand(command);
          if (prog.name === "") { return; }
          if (prog.name === expected) {
            term.echo($.t("bash_man.success"));
            success();
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



