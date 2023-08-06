/* global define $ _ i18n */

define(["terminal/strings"], function(strings) {
  
  i18n.init({
    resStore: strings,
    lng: "ru",
    fallbackLng: "en"
  });
});
