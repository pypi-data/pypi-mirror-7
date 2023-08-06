define(['js/http11', 'strings'], function(bashFn, strings) {
  i18n.init({
    resStore: strings,
    lng: 'ru',
    fallbackLng: 'en'
  });

  describe('Bash interpreter tests: ', function() {
    var t;

    beforeEach(function() {
      var bash = bashFn(
        jasmine.createSpy(),
        jasmine.createSpy()
      );
      t = $('<div></div>').terminal(bash.handler, bash.object);
    });

    it('connection to the correct address:port', function() {
      t.exec('telnet codebattle.io 80');
      expect(t.get_output().indexOf($.t('bashInterpreterOnStart', {
        addr: 'codebattle.io'
      }))).not.toBe(-1);
    });

    it('connection to the wrong address', function() {
      t.exec('telnet codebattle123.io 80');
      expect(t.get_output().indexOf($.t('bashInterpreterErrors.needAnotherSite', {
        addr: 'codebattle.io'
      }))).not.toEqual(-1);
    });

    it('connection to the wrong port', function() {
      t.exec('telnet codebattle.io 180');
      expect(t.get_output().indexOf($.t('bashInterpreterErrors.needAnotherPort'))).not.toEqual(-1);
    });

    it('reaction to the empty telnet command parameters', function() {
      t.exec('telnet');
      expect(t.get_output().indexOf($.t('bashInterpreterErrors.telnetUsage'))).not.toEqual(-1);
    });

    it('reaction to the wrong command', function() {
      t.exec('123456');
      expect(t.get_output().indexOf($.t('bashInterpreterErrors.commandNotFound'))).not.toEqual(-1);
    });
  });
});