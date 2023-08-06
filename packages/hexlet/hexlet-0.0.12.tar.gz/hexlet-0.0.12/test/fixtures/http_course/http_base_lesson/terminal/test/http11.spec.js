'use strict';

define(['js/http11', 'strings'], function(bashFn, strings) {
  i18n.init({
    resStore: strings,
    lng: 'ru',
    fallbackLng: 'en'
  });

  describe('http 1.1', function() {

    var t;

    beforeEach(function() {
      var bash = bashFn(
        jasmine.createSpy(),
        jasmine.createSpy()
      );
      t = $('<div></div>').terminal(bash.handler, bash.object);
      t.exec('telnet codebattle.io 80')
    })

    it('success', function() {
      t.exec('GET / HTTP/1.1')
        .exec('HOST: codebattle.io')
        .exec('');
      expect(t.get_output().indexOf($.t('response11'))).not.toEqual(-1);
    });

    it('error with wrong http version', function() {
      t.exec('GET / HTTP/1.0')
        .exec('HOST: blabla')
        .exec('');

      expect(t.get_output().indexOf($.t('http11Msgs.wrongProtocolVersion'))).not.toEqual(-1);
    });

    it('error without host header', function() {
      t.exec('GET / HTTP/1.1')
        .exec('');

      expect(t.get_output().indexOf($.t('http11Msgs.noHeader'))).not.toEqual(-1);
    });

    it('error with wrong host', function() {
      t.exec('GET / HTTP/1.1')
        .exec('HOST: blabla')
        .exec('');

      expect(t.get_output().indexOf($.t('http11Msgs.wrongHost'))).not.toEqual(-1);
    });

    it('incorrect input', function() {
      t.exec('123456');

      expect(t.get_output().indexOf($.t('fail'))).not.toEqual(-1);
    });

    it('reaction to empty command', function() {
      t.exec('');

      expect(t.get_output().indexOf($.t('bashInterpreterOnStart', {
        addr: 'codebattle.io'
      }))).not.toEqual(-1);
    });

    it('check two subsequent requests', function() {
      t.exec('GET / HTTP/1.0')
        .exec('HOST: blabla')
        .exec('');

      expect(t.get_output().indexOf($.t('http11Msgs.wrongProtocolVersion'))).not.toEqual(-1);

      t.exec('telnet codebattle.io 80')
        .exec('GET / HTTP/1.1')
        .exec('HOST: codebattle.io')
        .exec('');
      expect(t.get_output().indexOf($.t('response11'))).not.toEqual(-1);
    });
  });
});
