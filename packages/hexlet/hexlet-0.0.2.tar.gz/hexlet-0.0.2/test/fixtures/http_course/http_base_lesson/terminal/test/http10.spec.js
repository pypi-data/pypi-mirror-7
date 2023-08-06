'use strict';

define(['js/http10', 'strings'], function(bashFn, strings) {
  i18n.init({
    resStore: strings,
    lng: 'ru',
    fallbackLng: 'en'
  });

  describe('http 1.0', function() {

    var t;

    beforeEach(function() {
      var bash = bashFn(
        jasmine.createSpy(),
        jasmine.createSpy()
      );
      t = $('<div></div>').terminal(bash.handler, bash.object);
      t.exec('telnet google.com 80');
    })

    it('success', function() {
      t.exec('GET / HTTP/1.0')
        .exec('');

      expect(t.get_output().indexOf($.t('response10'))).not.toEqual(-1);
    });

    it('error with wrong http version', function() {
      t.exec('GET / HTTP/1.1')
        .exec('HOST: blabla')
        .exec('');

      expect(t.get_output().indexOf($.t('http10Msgs.wrongProtocolVersion'))).not.toEqual(-1);
    });

    it('error with host header', function() {
      t.exec('GET / HTTP/1.0')
        .exec('HOST: blabla')
        .exec('');

      expect(t.get_output().indexOf($.t('http10Msgs.notRequiredHost'))).not.toEqual(-1);
    });

    it('incorrect input', function() {
      t.exec('123456');

      expect(t.get_output().indexOf($.t('fail'))).not.toEqual(-1);
    });

    it('reaction to empty command', function() {
      t.exec('');

      expect(t.get_output().indexOf($.t('bashInterpreterOnStart', {
        addr: 'google.com'
      }))).not.toEqual(-1);
    });

    it('check two subsequent requests', function() {
      t.exec('GET / HTTP/1.0')
        .exec('HOST: blabla')
        .exec('');

      expect(t.get_output().indexOf($.t('http10Msgs.notRequiredHost'))).not.toEqual(-1);

      t.exec('telnet google.com 80')
        .exec('GET / HTTP/1.0')
        .exec('');

      expect(t.get_output().indexOf($.t('response10'))).not.toEqual(-1);
    });
  });
});